from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.checks import run_project_checks
from agent.diff_guard import inspect_diff
from agent.git_ops import git_status
from agent.openai_adapter import ask_model
from agent.repo_scanner import scan_repo
from agent.task_planner import build_plan


def execute_task(task: str, path: str | Path = ".", dry_run: bool = True) -> dict[str, Any]:
    """Build a safe execution packet for a task.

    In dry-run mode, this does not edit files. It inspects the repository,
    generates a plan, checks git state, and prepares model guidance.
    """
    project = scan_repo(path)
    status = git_status(path)
    plan = build_plan(task, project)
    model_result = ask_model(task, project, dry_run=dry_run)

    packet: dict[str, Any] = {
        "task": task,
        "dry_run": dry_run,
        "project": project,
        "git": status,
        "plan": plan,
        "model": {
            "ok": model_result.ok,
            "mode": model_result.mode,
            "content": model_result.content,
            "metadata": model_result.metadata,
        },
    }

    if not dry_run:
        packet["checks"] = run_project_checks(project)
        packet["diff"] = inspect_diff(path)

    return packet
