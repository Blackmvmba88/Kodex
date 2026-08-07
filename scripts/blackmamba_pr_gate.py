#!/usr/bin/env python3
"""BlackMamba PR Gate.

Classifies pull requests, detects common blockers/overlap, applies bm:* labels,
and maintains one sticky status comment. It is intentionally advisory: no merge,
close, branch update, or code mutation is performed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

API = "https://api.github.com"
GRAPHQL = "https://api.github.com/graphql"
MARKER = "<!-- blackmamba-pr-gate -->"

FAIL_CONCLUSIONS = {
    "failure",
    "cancelled",
    "timed_out",
    "action_required",
    "startup_failure",
    "stale",
}
PASS_CONCLUSIONS = {"success", "neutral", "skipped"}

STOPWORDS = {
    "a", "an", "and", "the", "to", "for", "of", "in", "on", "with",
    "add", "adds", "fix", "fixes", "improve", "improves", "update", "updates",
    "optimize", "optimizes", "feat", "feature", "chore", "refactor", "docs",
}

LABEL_META = {
    "bm:ready": ("2DA44E", "BlackMamba: safe candidate ready for merge review"),
    "bm:approval": ("8250DF", "BlackMamba: clean but requires human approval"),
    "bm:blocked-ci": ("CF222E", "BlackMamba: CI/check failure blocks progress"),
    "bm:blocked-review": ("CF222E", "BlackMamba: unresolved review feedback blocks progress"),
    "bm:blocked-conflict": ("CF222E", "BlackMamba: merge conflict or unmergeable state"),
    "bm:waiting-ci": ("BF8700", "BlackMamba: checks are still running"),
    "bm:consolidate": ("D4A72C", "BlackMamba: overlaps another open PR; compare before merge"),
    "bm:draft": ("6E7781", "BlackMamba: draft PR"),
    "bm:docs": ("0969DA", "BlackMamba: documentation-only change"),
    "bm:tests": ("1F883D", "BlackMamba: tests-only change"),
    "bm:dependency": ("5319E7", "BlackMamba: dependency maintenance"),
    "bm:code": ("0E8A16", "BlackMamba: executable/runtime code change"),
}


class GitHubError(RuntimeError):
    pass


@dataclass
class Assessment:
    number: int
    title: str
    kind: str
    state: str
    ci: str
    unresolved_threads: int
    review_decision: str | None
    duplicate_prs: list[int]
    files: list[str]
    reasons: list[str]


class GitHub:
    def __init__(self, token: str, repo: str) -> None:
        self.token = token
        self.repo = repo
        try:
            self.owner, self.name = repo.split("/", 1)
        except ValueError as exc:
            raise GitHubError(f"Invalid GITHUB_REPOSITORY: {repo!r}") from exc

    def _request(
        self,
        method: str,
        url: str,
        payload: dict[str, Any] | list[Any] | None = None,
        *,
        accept: str = "application/vnd.github+json",
    ) -> Any:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", accept)
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                raw = response.read()
                return json.loads(raw.decode("utf-8")) if raw else None
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise GitHubError(f"GitHub API {method} {url} -> {exc.code}: {body}") from exc

    def api(self, method: str, path: str, payload: Any = None, *, accept: str = "application/vnd.github+json") -> Any:
        return self._request(method, f"{API}{path}", payload, accept=accept)

    def graphql(self, query: str, variables: dict[str, Any]) -> Any:
        result = self._request("POST", GRAPHQL, {"query": query, "variables": variables})
        if result.get("errors"):
            raise GitHubError(f"GraphQL errors: {result['errors']}")
        return result["data"]

    def paginate(self, path: str, *, per_page: int = 100, max_pages: int = 10) -> list[Any]:
        out: list[Any] = []
        separator = "&" if "?" in path else "?"
        for page in range(1, max_pages + 1):
            batch = self.api("GET", f"{path}{separator}per_page={per_page}&page={page}")
            if not isinstance(batch, list):
                raise GitHubError(f"Expected list from {path}, got {type(batch).__name__}")
            out.extend(batch)
            if len(batch) < per_page:
                break
        return out

    def pull(self, number: int) -> dict[str, Any]:
        return self.api("GET", f"/repos/{self.repo}/pulls/{number}")

    def pull_files(self, number: int) -> list[dict[str, Any]]:
        return self.paginate(f"/repos/{self.repo}/pulls/{number}/files")

    def open_pulls(self) -> list[dict[str, Any]]:
        return self.paginate(f"/repos/{self.repo}/pulls?state=open&sort=updated&direction=desc")

    def review_state(self, number: int) -> tuple[str | None, int]:
        query = """
        query($owner:String!, $name:String!, $number:Int!) {
          repository(owner:$owner, name:$name) {
            pullRequest(number:$number) {
              reviewDecision
              reviewThreads(first:100) {
                nodes { isResolved }
              }
            }
          }
        }
        """
        data = self.graphql(
            query,
            {"owner": self.owner, "name": self.name, "number": number},
        )
        pr = data["repository"]["pullRequest"]
        threads = pr["reviewThreads"]["nodes"] or []
        unresolved = sum(1 for node in threads if not node.get("isResolved", False))
        return pr.get("reviewDecision"), unresolved

    def check_state(self, sha: str) -> tuple[str, list[str]]:
        check_runs = self.api(
            "GET",
            f"/repos/{self.repo}/commits/{sha}/check-runs?per_page=100",
            accept="application/vnd.github+json",
        ).get("check_runs", [])

        # Ignore this gate's own job so it never blocks itself.
        relevant_runs = [
            run for run in check_runs
            if "blackmamba pr gate" not in str(run.get("name", "")).lower()
        ]

        statuses = self.api("GET", f"/repos/{self.repo}/commits/{sha}/status").get("statuses", [])

        failures: list[str] = []
        pending = False
        evidence = False

        for run in relevant_runs:
            evidence = True
            status = run.get("status")
            conclusion = run.get("conclusion")
            name = run.get("name", "check")
            if status != "completed":
                pending = True
            elif conclusion in FAIL_CONCLUSIONS:
                failures.append(f"{name}: {conclusion}")
            elif conclusion not in PASS_CONCLUSIONS:
                pending = True

        for status in statuses:
            evidence = True
            state = status.get("state")
            context = status.get("context", "status")
            if state in {"error", "failure"}:
                failures.append(f"{context}: {state}")
            elif state == "pending":
                pending = True

        if failures:
            return "failed", failures
        if pending:
            return "pending", []
        if evidence:
            return "passed", []
        return "none", []

    def ensure_labels(self, names: Iterable[str]) -> None:
        existing = {item["name"] for item in self.paginate(f"/repos/{self.repo}/labels")}
        for name in names:
            if name in existing:
                continue
            color, description = LABEL_META[name]
            try:
                self.api(
                    "POST",
                    f"/repos/{self.repo}/labels",
                    {"name": name, "color": color, "description": description},
                )
            except GitHubError as exc:
                # Concurrent runs may create the same label between list and POST.
                if "422" not in str(exc):
                    raise

    def set_bm_labels(self, number: int, desired: list[str]) -> None:
        issue = self.api("GET", f"/repos/{self.repo}/issues/{number}")
        current = [item["name"] for item in issue.get("labels", [])]
        bm_current = [name for name in current if name.startswith("bm:")]

        self.ensure_labels(desired)

        for name in bm_current:
            if name not in desired:
                encoded = urllib.parse.quote(name, safe="")
                try:
                    self.api("DELETE", f"/repos/{self.repo}/issues/{number}/labels/{encoded}")
                except GitHubError as exc:
                    if "404" not in str(exc):
                        raise

        missing = [name for name in desired if name not in current]
        if missing:
            self.api("POST", f"/repos/{self.repo}/issues/{number}/labels", {"labels": missing})

    def upsert_comment(self, number: int, body: str) -> None:
        comments = self.paginate(f"/repos/{self.repo}/issues/{number}/comments")
        for comment in comments:
            if MARKER in str(comment.get("body", "")):
                self.api(
                    "PATCH",
                    f"/repos/{self.repo}/issues/comments/{comment['id']}",
                    {"body": body},
                )
                return
        self.api("POST", f"/repos/{self.repo}/issues/{number}/comments", {"body": body})


def load_config() -> dict[str, Any]:
    path = Path(".github/blackmamba/pr-gate.json")
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def event_pr_number(explicit: int | None) -> int | None:
    if explicit:
        return explicit
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path or not Path(event_path).exists():
        return None
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    pr = event.get("pull_request")
    if isinstance(pr, dict) and pr.get("number"):
        return int(pr["number"])
    return None


def normalized_title_tokens(title: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9]+", title.lower()))
    return {token for token in tokens if len(token) > 1 and token not in STOPWORDS}


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def file_overlap(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / min(len(left), len(right))


def classify_kind(pr: dict[str, Any], files: list[str]) -> str:
    title = str(pr.get("title", "")).lower()
    author = str((pr.get("user") or {}).get("login", "")).lower()
    if "dependabot" in author or title.startswith(("bump ", "deps:", "chore(deps)")):
        return "dependency"

    def is_doc(path: str) -> bool:
        lower = path.lower()
        return (
            lower.startswith("docs/")
            or lower.endswith((".md", ".mdx", ".rst", ".txt"))
        )

    def is_test(path: str) -> bool:
        lower = path.lower()
        name = Path(lower).name
        return lower.startswith(("test/", "tests/")) or name.startswith("test_") or name.endswith("_test.py")

    if files and all(is_doc(path) for path in files):
        return "docs"
    if files and all(is_test(path) for path in files):
        return "tests"
    return "code"


def duplicate_candidates(
    gh: GitHub,
    pr: dict[str, Any],
    files: list[str],
    config: dict[str, Any],
    open_pulls: list[dict[str, Any]] | None = None,
) -> list[int]:
    settings = config.get("duplicate_detection", {})
    if settings.get("enabled", True) is False:
        return []

    file_threshold = float(settings.get("file_overlap_threshold", 0.75))
    title_threshold = float(settings.get("title_similarity_threshold", 0.25))
    max_open = int(settings.get("max_open_prs_to_compare", 40))

    current_number = int(pr["number"])
    current_files = set(files)
    current_tokens = normalized_title_tokens(str(pr.get("title", "")))
    candidates: list[int] = []

    pulls = (open_pulls or gh.open_pulls())[:max_open]
    for other in pulls:
        number = int(other["number"])
        if number == current_number:
            continue
        other_files = {item["filename"] for item in gh.pull_files(number)}
        overlap = file_overlap(current_files, other_files)
        if overlap < file_threshold:
            continue
        title_score = jaccard(current_tokens, normalized_title_tokens(str(other.get("title", ""))))
        if title_score >= title_threshold:
            candidates.append(number)

    return sorted(candidates)


def assess(
    gh: GitHub,
    number: int,
    config: dict[str, Any],
    open_pulls: list[dict[str, Any]] | None = None,
) -> Assessment:
    pr = gh.pull(number)
    files = [item["filename"] for item in gh.pull_files(number)]
    kind = classify_kind(pr, files)
    review_decision, unresolved_threads = gh.review_state(number)
    ci, ci_failures = gh.check_state(pr["head"]["sha"])
    duplicates = duplicate_candidates(gh, pr, files, config, open_pulls)

    reasons: list[str] = []
    mergeable = pr.get("mergeable")
    mergeable_state = pr.get("mergeable_state")

    if pr.get("draft"):
        state = "DRAFT"
        reasons.append("PR is still a draft")
    elif mergeable is False or mergeable_state == "dirty":
        state = "BLOCKED_CONFLICT"
        reasons.append("GitHub reports the PR as unmergeable/conflicted")
    elif ci == "failed":
        state = "BLOCKED_CI"
        reasons.extend(ci_failures or ["One or more checks failed"])
    elif unresolved_threads > 0 or review_decision == "CHANGES_REQUESTED":
        state = "BLOCKED_REVIEW"
        if unresolved_threads:
            reasons.append(f"{unresolved_threads} unresolved review thread(s)")
        if review_decision == "CHANGES_REQUESTED":
            reasons.append("A reviewer requested changes")
    elif duplicates:
        state = "CONSOLIDATE"
        reasons.append("High-overlap open PR candidate(s): " + ", ".join(f"#{n}" for n in duplicates))
    elif ci == "pending":
        state = "WAITING_CI"
        reasons.append("Checks are still running")
    elif review_decision == "REVIEW_REQUIRED":
        state = "READY_FOR_APPROVAL"
        reasons.append("Repository policy still requires human review")
    elif kind == "docs" and (ci in {"passed", "none"}):
        state = "READY"
        reasons.append("Documentation-only change with no active blocker")
    else:
        state = "READY_FOR_APPROVAL"
        reasons.append("No active blocker; executable or policy-sensitive change needs human approval")

    return Assessment(
        number=number,
        title=str(pr.get("title", "")),
        kind=kind,
        state=state,
        ci=ci,
        unresolved_threads=unresolved_threads,
        review_decision=review_decision,
        duplicate_prs=duplicates,
        files=files,
        reasons=reasons,
    )


def labels_for(result: Assessment) -> list[str]:
    kind_label = {
        "docs": "bm:docs",
        "tests": "bm:tests",
        "dependency": "bm:dependency",
        "code": "bm:code",
    }[result.kind]

    state_label = {
        "READY": "bm:ready",
        "READY_FOR_APPROVAL": "bm:approval",
        "BLOCKED_CI": "bm:blocked-ci",
        "BLOCKED_REVIEW": "bm:blocked-review",
        "BLOCKED_CONFLICT": "bm:blocked-conflict",
        "WAITING_CI": "bm:waiting-ci",
        "CONSOLIDATE": "bm:consolidate",
        "DRAFT": "bm:draft",
    }[result.state]
    return [kind_label, state_label]


def render_comment(result: Assessment) -> str:
    reason_lines = "\n".join(f"- {reason}" for reason in result.reasons) or "- No blockers detected"
    duplicates = ", ".join(f"#{n}" for n in result.duplicate_prs) if result.duplicate_prs else "none"
    review = result.review_decision or "none"
    return f"""{MARKER}
## 🐍 BlackMamba PR Gate

**State:** `{result.state}`  
**Type:** `{result.kind}`  
**CI:** `{result.ci}`  
**Review decision:** `{review}`  
**Unresolved review threads:** `{result.unresolved_threads}`  
**Potential overlapping PRs:** {duplicates}

### Why
{reason_lines}

### Policy
This gate is **advisory**. It may classify and label the PR, but it does **not** merge, close, push, rewrite branches, or modify PR code. Human approval remains the final authority for executable changes.

_Updated automatically by BlackMamba PR Gate v1._
"""


def write_step_summary(results: list[Assessment]) -> None:
    path = os.getenv("GITHUB_STEP_SUMMARY")
    if not path:
        return
    lines = [
        "## 🐍 BlackMamba PR Gate",
        "",
        "| PR | Type | State | CI | Review threads |",
        "|---:|---|---|---|---:|",
    ]
    for item in results:
        lines.append(
            f"| #{item.number} | {item.kind} | {item.state} | {item.ci} | {item.unresolved_threads} |"
        )
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def process_one(gh: GitHub, number: int, config: dict[str, Any], open_pulls: list[dict[str, Any]] | None) -> Assessment:
    result = assess(gh, number, config, open_pulls)
    desired = labels_for(result)
    gh.set_bm_labels(number, desired)
    gh.upsert_comment(number, render_comment(result))
    print(
        json.dumps(
            {
                "pr": result.number,
                "state": result.state,
                "type": result.kind,
                "ci": result.ci,
                "review_threads": result.unresolved_threads,
                "duplicates": result.duplicate_prs,
                "labels": desired,
            },
            sort_keys=True,
        )
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and label pull requests using BlackMamba PR Gate policy")
    parser.add_argument("--pr", type=int, help="Specific PR number")
    parser.add_argument("--all-open", action="store_true", help="Process all open pull requests")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not token or not repo:
        print("GITHUB_TOKEN and GITHUB_REPOSITORY are required", file=sys.stderr)
        return 2

    gh = GitHub(token, repo)
    config = load_config()
    explicit = event_pr_number(args.pr)

    if args.all_open or explicit is None:
        pulls = gh.open_pulls()
        numbers = [int(item["number"]) for item in pulls]
        open_pulls = pulls
    else:
        numbers = [explicit]
        open_pulls = None

    results: list[Assessment] = []
    for number in numbers:
        try:
            results.append(process_one(gh, number, config, open_pulls))
        except GitHubError as exc:
            print(f"PR #{number}: {exc}", file=sys.stderr)
            if len(numbers) == 1:
                return 1

    write_step_summary(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
