from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.orchestrator import orchestrate_task
from agent.run_state import RunState, RunStore
from agent.shipper import ship_task


TERMINAL_PHASES = {"blocked", "needs_review", "ready_for_commit", "failed"}


def autonomous_run(
    task: str,
    path: str | Path = ".",
    *,
    apply: bool = False,
    force: bool = False,
    use_branch: bool = True,
) -> dict[str, Any]:
    """Run Kodex's persisted autonomous loop through its safe local boundary.

    Without ``apply`` this persists the orchestration decision only. With
    ``apply`` it delegates to ``ship_task`` and stops at ``ready_for_commit``;
    Kodex still does not commit, push, open PRs, or merge without an external
    integration explicitly performing those actions.
    """
    root = Path(path).expanduser().resolve()
    store = RunStore(root)
    state = RunState.create(task, root)
    store.save(state)

    try:
        state.update(phase="orchestrating")
        store.save(state)
        plan = orchestrate_task(task, root, use_branch=use_branch)

        if not plan.get("ready"):
            phase = "blocked" if plan.get("decision") == "blocked" else "needs_review"
            state.update(phase=phase, status=phase, branch=plan.get("branch"))
            store.save(state)
            return {"run": state.to_dict(), "orchestration": plan, "ship": None}

        state.update(phase="ready", branch=plan.get("branch"))
        store.save(state)

        if not apply:
            state.update(phase="planned", status="paused")
            store.save(state)
            return {"run": state.to_dict(), "orchestration": plan, "ship": None}

        state.update(phase="shipping")
        store.save(state)
        shipped = ship_task(task, root, force=force, use_branch=use_branch)

        phase = str(shipped.get("status") or "needs_review")
        state.update(
            phase=phase,
            status="paused" if phase == "ready_for_commit" else phase,
            files_changed=list(shipped.get("changed_files", [])),
            checks=list(shipped.get("checks", [])),
        )
        store.save(state)
        return {"run": state.to_dict(), "orchestration": plan, "ship": shipped}
    except Exception as exc:
        state.update(phase="failed", status="failed", error=f"{type(exc).__name__}: {exc}")
        store.save(state)
        raise


def resume_run(run_id: str, path: str | Path = ".") -> dict[str, Any]:
    """Load a persisted run and return the safe next action.

    v0.1 recovery is intentionally conservative: it restores state and tells
    the caller how to continue rather than replaying mutating operations.
    """
    store = RunStore(path)
    state = store.load(run_id)

    if state.phase in TERMINAL_PHASES or state.phase == "planned":
        next_action = "review"
    elif state.phase in {"created", "orchestrating", "ready"}:
        next_action = "rerun"
    elif state.phase == "shipping":
        next_action = "inspect_worktree_before_retry"
    else:
        next_action = "review"

    return {"run": state.to_dict(), "next_action": next_action}
