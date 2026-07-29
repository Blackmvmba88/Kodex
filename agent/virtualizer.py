from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.git_ops import commit_message, suggest_branch_name
from agent.patcher import propose_patch
from agent.snapshot import build_snapshot
from agent.task_planner import build_plan


def virtualize_task(task: str, path: str | Path = ".", *, use_branch: bool = True) -> dict[str, Any]:
    """Build a no-write execution simulation for a task.

    This is the safest planning layer: it does not create branches, write files,
    run tests, commit, or push. It predicts the execution packet that Kodex would
    attempt when the user later calls ship.
    """
    root = Path(path).expanduser().resolve()
    snapshot = build_snapshot(root)
    proposal = propose_patch(task, root)
    plan = build_plan(task, proposal.get("project"))

    files = proposal.get("files", {})
    predicted_files = sorted(files.keys())
    branch_name = suggest_branch_name(task)
    checks = list(plan.get("checks", []))
    can_execute = bool(snapshot.get("ready")) and bool(predicted_files)

    blockers: list[str] = []
    warnings: list[str] = []

    git = snapshot.get("git", {})
    if not git.get("is_git_repo"):
        blockers.append("path is not a git repository")
    if git.get("dirty"):
        blockers.append("working tree has existing changes")
    if not snapshot.get("diff", {}).get("safe"):
        blockers.append("diff guard is not safe")
    if not checks:
        warnings.append("no check commands detected")
    if not predicted_files:
        blockers.append("no files predicted for this task")

    status = "ready_to_ship" if can_execute and not blockers else "needs_attention"

    return {
        "task": task,
        "path": str(root),
        "mode": "virtualized",
        "status": status,
        "ready": status == "ready_to_ship",
        "use_branch": use_branch,
        "branch": branch_name if use_branch else None,
        "snapshot": snapshot,
        "plan": plan,
        "predicted_files": predicted_files,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "suggested_commit": commit_message(task),
        "next_command": (
            f"kodex ship {task!r} --branch" if use_branch else f"kodex ship {task!r}"
        ) if status == "ready_to_ship" else None,
    }
