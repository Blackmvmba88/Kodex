from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def run_git(repo_path: str | Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    root = Path(repo_path).expanduser().resolve()
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


# Backward-compatible internal alias used by diff_guard.
def _run_git(repo_path: str | Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return run_git(repo_path, args)


def is_git_repo(repo_path: str | Path) -> bool:
    result = run_git(repo_path, ["rev-parse", "--is-inside-work-tree"])
    return result.returncode == 0 and result.stdout.strip() == "true"


def current_branch(repo_path: str | Path) -> str | None:
    result = run_git(repo_path, ["branch", "--show-current"])
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def git_status(repo_path: str | Path) -> dict[str, Any]:
    if not is_git_repo(repo_path):
        return {
            "is_git_repo": False,
            "branch": None,
            "dirty": None,
            "changed_files": [],
            "error": "not a git repository",
        }

    porcelain = run_git(repo_path, ["status", "--short", "--untracked-files=all"])
    changed_files = [line.strip() for line in porcelain.stdout.splitlines() if line.strip()]

    return {
        "is_git_repo": True,
        "branch": current_branch(repo_path),
        "dirty": bool(changed_files),
        "changed_files": changed_files,
        "error": porcelain.stderr.strip() if porcelain.returncode != 0 else None,
    }


def suggest_branch_name(task: str) -> str:
    clean = "".join(char.lower() if char.isalnum() else "-" for char in task)
    clean = "-".join(part for part in clean.split("-") if part)
    return f"kodex/{clean[:48] or 'task'}"


def commit_message(task: str) -> str:
    normalized = " ".join(task.strip().split())
    if not normalized:
        return "kodex: update project"
    return f"kodex: {normalized[:72]}"
