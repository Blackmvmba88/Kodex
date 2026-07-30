from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.diff_guard import inspect_diff
from agent.git_ops import git_status
from agent.repo_scanner import scan_repo

REQUIRED_FILES = {
    "readme": "README.md",
    "architecture": "docs/ARCHITECTURE.md",
    "operations": "docs/OPERATIONS.md",
    "verify_script": "scripts/verify.sh",
    "ci": ".github/workflows/ci.yml",
    "pr_template": ".github/pull_request_template.md",
    "bug_template": ".github/ISSUE_TEMPLATE/bug_report.md",
    "feature_template": ".github/ISSUE_TEMPLATE/feature_request.md",
}


def _file_checks(root: Path) -> dict[str, bool]:
    return {name: (root / path).exists() for name, path in REQUIRED_FILES.items()}


def _missing_files(checks: dict[str, bool]) -> list[str]:
    return [REQUIRED_FILES[name] for name, present in checks.items() if not present]


def release_check(path: str | Path = ".") -> dict[str, Any]:
    """Evaluate whether the repository is ready for release/versioning."""
    root = Path(path).expanduser().resolve()
    project = scan_repo(root)
    git = git_status(root)
    diff = inspect_diff(root)
    files = _file_checks(root)
    missing = _missing_files(files)

    tests_detected = bool(project.get("tests"))
    checks_detected = bool(project.get("commands"))
    docs_ready = files["readme"] and files["architecture"] and files["operations"]
    github_ready = files["ci"] and files["pr_template"] and files["bug_template"] and files["feature_template"]
    clean = bool(git.get("is_git_repo")) and not bool(git.get("dirty"))
    diff_safe = bool(diff.get("safe"))

    blockers: list[str] = []
    warnings: list[str] = []

    if not git.get("is_git_repo"):
        blockers.append("path is not a git repository")
    if git.get("dirty"):
        blockers.append("working tree has uncommitted changes")
    if not diff_safe:
        blockers.append("diff guard is not safe")
    if not tests_detected:
        blockers.append("no tests detected")
    if not checks_detected:
        blockers.append("no check commands detected")
    if missing:
        warnings.append("missing release infrastructure files")

    score_items = {
        "git_clean": clean,
        "diff_safe": diff_safe,
        "tests_detected": tests_detected,
        "checks_detected": checks_detected,
        "docs_ready": docs_ready,
        "github_ready": github_ready,
        "verify_script": files["verify_script"],
    }
    score = sum(1 for ok in score_items.values() if ok)
    total = len(score_items)
    ready = not blockers and docs_ready and github_ready and files["verify_script"]

    return {
        "path": str(root),
        "project": project.get("name", "unknown"),
        "status": "release_ready" if ready else "needs_attention",
        "ready": ready,
        "score": {"passed": score, "total": total},
        "checks": score_items,
        "required_files": files,
        "missing_files": missing,
        "blockers": blockers,
        "warnings": warnings,
        "git": git,
        "diff": {
            "ok": diff.get("ok"),
            "safe": diff_safe,
            "warnings": diff.get("warnings", []),
        },
        "next_actions": [] if ready else [
            "restore missing release infrastructure files",
            "commit or clean working tree changes",
            "run scripts/verify.sh",
        ],
    }
