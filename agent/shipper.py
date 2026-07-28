from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.checks import run_project_checks
from agent.diff_guard import inspect_diff
from agent.git_ops import commit_message, git_status
from agent.patcher import apply_patch
from agent.repo_scanner import scan_repo


def _checks_ok(checks: list[dict[str, Any]]) -> bool:
    return bool(checks) and all(check.get("ok") for check in checks)


def _changed_files(status: dict[str, Any]) -> list[str]:
    files: list[str] = []
    for entry in status.get("changed_files", []):
        # Git porcelain examples: "M README.md", "?? tests/test_x.py"
        parts = str(entry).split(maxsplit=1)
        if len(parts) == 2:
            files.append(parts[1])
        elif parts:
            files.append(parts[0])
    return files


def ship_task(task: str, path: str | Path = ".", force: bool = False) -> dict[str, Any]:
    """Apply a guarded patch, run checks, inspect diff, and prepare commit instructions.

    This intentionally does not commit or push. It prepares the repo for a human-reviewed commit.
    """
    root = Path(path).expanduser().resolve()
    before_status = git_status(root)

    if before_status.get("is_git_repo") and before_status.get("dirty"):
        return {
            "task": task,
            "path": str(root),
            "status": "blocked_dirty_worktree",
            "ok": False,
            "reason": "working tree has existing changes; commit/stash them before shipping",
            "git": before_status,
        }

    project = scan_repo(root)
    patch_result = apply_patch(task, root, force=force)
    after_status = git_status(root)
    diff = inspect_diff(root)
    checks = run_project_checks(project)

    checks_ok = _checks_ok(checks)
    diff_safe = bool(diff.get("safe"))
    write_allowed = bool(patch_result.get("write_result", {}).get("allowed"))

    ok = write_allowed and checks_ok and diff_safe
    status = "ready_for_commit" if ok else "needs_review"
    changed_files = _changed_files(after_status)
    suggested_commit = commit_message(task)

    return {
        "task": task,
        "path": str(root),
        "status": status,
        "ok": ok,
        "patch": patch_result,
        "checks_ok": checks_ok,
        "diff_safe": diff_safe,
        "changed_files": changed_files,
        "suggested_commit": suggested_commit,
        "next_commands": [
            f"git add {' '.join(changed_files) if changed_files else '<files>'}",
            f"git commit -m \"{suggested_commit}\"",
            "git push",
        ] if ok else [],
        "checks": checks,
        "diff": diff,
        "git": after_status,
    }
