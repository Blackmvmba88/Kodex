from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.virtualizer import virtualize_task


def orchestrate_task(task: str, path: str | Path = ".", *, use_branch: bool = True) -> dict[str, Any]:
    """Plan the safest next step for a task without mutating the repository.

    The orchestrator is the decision layer above virtualize/branch/ship. It does
    not write files, create branches, commit, or push. It explains what Kodex
    would do next and why.
    """
    simulation = virtualize_task(task, path, use_branch=use_branch)
    blockers = list(simulation.get("blockers", []))
    warnings = list(simulation.get("warnings", []))
    ready = bool(simulation.get("ready")) and not blockers

    if blockers:
        decision = "blocked"
        next_action = "resolve_blockers"
        next_command = None
    elif ready:
        decision = "ready"
        next_action = "ship_with_branch" if use_branch else "ship"
        next_command = simulation.get("next_command")
    else:
        decision = "needs_review"
        next_action = "review_simulation"
        next_command = None

    return {
        "task": task,
        "path": simulation.get("path"),
        "mode": "orchestrated",
        "decision": decision,
        "ready": decision == "ready",
        "next_action": next_action,
        "next_command": next_command,
        "branch": simulation.get("branch"),
        "predicted_files": simulation.get("predicted_files", []),
        "checks": simulation.get("checks", []),
        "blockers": blockers,
        "warnings": warnings,
        "simulation": simulation,
    }
