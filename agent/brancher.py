from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.git_ops import git_status, run_git, suggest_branch_name


def prepare_branch(task: str, path: str | Path = ".", *, checkout: bool = True) -> dict[str, Any]:
    """Create and optionally check out a safe task branch.

    The command refuses to run when the working tree is dirty so Kodex does not
    accidentally mix unrelated changes into a new task branch.
    """
    root = Path(path).expanduser().resolve()
    status = git_status(root)
    branch_name = suggest_branch_name(task)

    if not status.get("is_git_repo"):
        return {
            "task": task,
            "path": str(root),
            "branch": branch_name,
            "ok": False,
            "status": "blocked_not_git_repo",
            "reason": "path is not a git repository",
            "git": status,
        }

    if status.get("dirty"):
        return {
            "task": task,
            "path": str(root),
            "branch": branch_name,
            "ok": False,
            "status": "blocked_dirty_worktree",
            "reason": "commit, stash, or clean existing changes before creating a task branch",
            "git": status,
        }

    existing = run_git(root, ["rev-parse", "--verify", branch_name])
    exists = existing.returncode == 0

    if checkout:
        if exists:
            result = run_git(root, ["checkout", branch_name])
            action = "checked_out_existing_branch"
        else:
            result = run_git(root, ["checkout", "-b", branch_name])
            action = "created_and_checked_out_branch"
    else:
        if exists:
            result = existing
            action = "branch_already_exists"
        else:
            result = run_git(root, ["branch", branch_name])
            action = "created_branch"

    after = git_status(root)
    ok = result.returncode == 0

    return {
        "task": task,
        "path": str(root),
        "branch": branch_name,
        "ok": ok,
        "status": action if ok else "branch_failed",
        "checkout": checkout,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "git": after,
        "next_commands": [
            f"git push -u origin {branch_name}",
        ] if ok else [],
    }
