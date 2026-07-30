from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.diagnostics import diagnose_text
from agent.git_ops import git_status
from agent.snapshot import build_snapshot


def _bullet_list(items: list[str], fallback: str = "None") -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- `{item}`" for item in items)


def _changed_files_from_git(status: dict[str, Any]) -> list[str]:
    files: list[str] = []
    for entry in status.get("changed_files", []):
        parts = str(entry).split(maxsplit=1)
        files.append(parts[1] if len(parts) == 2 else str(entry))
    return files


def build_pr_summary(
    title: str,
    path: str | Path = ".",
    *,
    test_output: str | None = None,
    extra_summary: str | None = None,
) -> dict[str, Any]:
    """Build a structured pull request summary from repo state and optional test output."""
    root = Path(path).expanduser().resolve()
    snapshot = build_snapshot(root)
    git = git_status(root)
    changed_files = _changed_files_from_git(git)
    diagnosis = diagnose_text(test_output or "") if test_output else None

    tests_status = "not_provided"
    if test_output:
        tests_status = "passed" if "failed" not in test_output.lower() and "error" not in test_output.lower() else "needs_review"

    risk_level = "low"
    risks: list[str] = []
    if git.get("dirty"):
        risks.append("working tree has uncommitted changes")
    if not snapshot.get("diff", {}).get("safe"):
        risks.append("diff guard reported warnings")
    if diagnosis and diagnosis.get("phase") != "UNKNOWN":
        risks.append(f"diagnosis phase: {diagnosis.get('phase')}")
    if risks:
        risk_level = "medium"

    body = f"""## Summary
{extra_summary or f'Kodex-generated PR summary for: {title}'}

## Changed files
{_bullet_list(changed_files)}

## Validation
- Snapshot status: `{snapshot.get('status')}`
- Tests: `{tests_status}`
- Diff safe: `{snapshot.get('diff', {}).get('safe')}`

## Risk
- Level: `{risk_level}`
{_bullet_list(risks, fallback='No known risks detected')}

## Diagnosis
- Phase: `{diagnosis.get('phase') if diagnosis else 'not_run'}`
- Reason: `{diagnosis.get('reason') if diagnosis else 'No diagnostic log provided'}`
- Suggested fix: `{diagnosis.get('suggested_fix') if diagnosis else 'Run tests and attach output if review is needed'}`

## Human approval checklist
- [ ] I reviewed the changed files.
- [ ] I verified tests/checks are acceptable.
- [ ] I confirmed no secrets or destructive changes were included.
- [ ] I am ready to merge or request changes.
"""

    return {
        "title": title,
        "path": str(root),
        "changed_files": changed_files,
        "snapshot_status": snapshot.get("status"),
        "tests_status": tests_status,
        "risk_level": risk_level,
        "risks": risks,
        "diagnosis": diagnosis,
        "body": body,
    }
