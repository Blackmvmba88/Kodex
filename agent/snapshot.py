from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.diff_guard import inspect_diff
from agent.git_ops import git_status
from agent.repo_scanner import scan_repo


def build_snapshot(path: str | Path = ".") -> dict[str, Any]:
    """Build a compact readiness snapshot for a repository."""
    root = Path(path).expanduser().resolve()
    project = scan_repo(root)
    git = git_status(root)
    diff = inspect_diff(root)

    commands = project.get("commands", {})
    risks = project.get("risks", [])
    dirty = bool(git.get("dirty"))
    diff_safe = bool(diff.get("safe"))
    checks_available = bool(commands)

    ready = (
        bool(git.get("is_git_repo"))
        and not dirty
        and diff_safe
        and not risks
        and checks_available
    )

    return {
        "project": project.get("name", "unknown"),
        "path": str(root),
        "stack": project.get("stack", []),
        "entrypoints": project.get("entrypoints", []),
        "tests": project.get("tests", []),
        "commands": commands,
        "risks": risks,
        "git": {
            "is_git_repo": git.get("is_git_repo"),
            "branch": git.get("branch"),
            "dirty": dirty,
            "changed_files": git.get("changed_files", []),
            "error": git.get("error"),
        },
        "diff": {
            "ok": diff.get("ok"),
            "safe": diff_safe,
            "warnings": diff.get("warnings", []),
        },
        "ready": ready,
        "status": "ready" if ready else "needs_attention",
    }
