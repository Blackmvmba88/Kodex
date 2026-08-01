from __future__ import annotations

"""write_mode.py — guarded end-to-end write pipeline for Kodex.

Implements the contract described in docs/WRITE_MODE.md:

    1.  snapshot / clean-worktree guard
    2.  task-branch guard
    3.  compile spec
    4.  build context
    5.  call provider
    6.  validate write plan
    7.  create checkpoint
    8.  apply files
    9.  run checks
    10. inspect diff
    11. repair loop (if configured)
    12. stop at ready_for_commit

Kodex never auto-commits, pushes, merges, deletes sensitive files, or opens
a PR.  The caller is always responsible for the final ``git add / commit / push``.
"""

import shlex
import subprocess
from pathlib import Path
from typing import Any

from agent.checkpoint import create_checkpoint
from agent.code_generator import generate_code
from agent.context_builder import build_context
from agent.diagnostics import diagnose_text
from agent.generated_patcher import apply_generated_files
from agent.providers.registry import get_provider
from agent.repair_loop import run_repair_loop
from agent.run_state import RunState, RunStore
from agent.spec_compiler import compile_spec
from agent.write_policy import WritePolicy, load_write_policy


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _current_branch(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def _worktree_is_clean(repo_root: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == ""


def _run_checks(repo_root: Path) -> tuple[bool, str]:
    """Run the project's fast check suite (pytest -x -q). Returns (ok, output)."""
    result = subprocess.run(
        ["python", "-m", "pytest", "-x", "-q", "--tb=short"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def _safe_diff(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "diff", "--stat"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------

def run_write_mode(
    repository: str | Path = ".",
    *,
    task: str = "Implement MVP",
    provider: str | None = None,
    sources: list[str] | None = None,
    force_branch: bool = False,
    dry_run: bool = False,
    policy: WritePolicy | None = None,
) -> dict[str, Any]:
    """Run the full guarded write pipeline.

    Args:
        repository: Path to the repo root (default: current directory).
        task: Natural-language task description passed to the provider.
        provider: Provider key (e.g. ``"noop"``, ``"openai"``). Defaults to
            the policy's configured default.
        sources: Optional list of source globs / paths for context building.
        force_branch: If True, skip the task-branch guard. Use carefully.
        dry_run: If True, perform a fully non-mutating simulation. It validates
            the write plan and returns checkpoint/run-state previews, but writes
            no generated files, checkpoints, run-state files, pytest cache, or
            metadata.
        policy: Pre-loaded WritePolicy; loaded from disk if None.

    Returns:
        A dict with ``status``, ``ok``, ``branch``, ``checkpoint``,
        ``written``, ``checks``, ``diagnosis``, ``repair_attempts``, and
        ``next_commands``.
    """
    root = Path(repository).expanduser().resolve()
    loaded_policy = policy or load_write_policy(root)
    selected_provider_key = provider or loaded_policy.providers.default

    result: dict[str, Any] = {
        "status": "initializing",
        "ok": False,
        "dry_run": dry_run,
        "branch": "",
        "checkpoint": None,
        "checkpoint_preview": None,
        "run_state_preview": None,
        "metadata_written": [],
        "written": [],
        "checks_ok": None,
        "checks": [],
        "diff_safe": None,
        "diagnosis": None,
        "repair_attempts": [],
        "next_commands": [],
    }

    # ------------------------------------------------------------------
    # 1. Worktree guard
    # ------------------------------------------------------------------
    if loaded_policy.require_clean_worktree and not _worktree_is_clean(root):
        result["status"] = "blocked_dirty_worktree"
        result["diagnosis"] = diagnose_text("blocked_dirty_worktree")
        return result

    # ------------------------------------------------------------------
    # 2. Branch guard
    # ------------------------------------------------------------------
    branch = _current_branch(root)
    result["branch"] = branch

    if not force_branch and loaded_policy.require_task_branch:
        if branch == "main" and not loaded_policy.allow_direct_main:
            result["status"] = "blocked_on_main"
            result["diagnosis"] = diagnose_text(
                "git: cannot write directly to main branch without allow_direct_main=true"
            )
            return result

    # ------------------------------------------------------------------
    # 3–5. Spec → context → generate
    # ------------------------------------------------------------------
    compiled = compile_spec(root, task=task, sources=sources)
    context = build_context(root, compiled)
    selected_provider = get_provider(selected_provider_key)
    generation = generate_code(task, context, selected_provider)

    if not generation.ok:
        result["status"] = "generation_failed"
        result["diagnosis"] = diagnose_text(generation.message)
        return result

    # ------------------------------------------------------------------
    # 6. Validate write plan
    # ------------------------------------------------------------------
    from agent.approval import evaluate_write_plan  # local import avoids circular risk

    write_plan = evaluate_write_plan(root, generation.files)
    if not write_plan["allowed"]:
        result["status"] = "write_plan_rejected"
        result["diagnosis"] = {"reasons": write_plan["reasons"], "warnings": write_plan["warnings"]}
        return result

    # ------------------------------------------------------------------
    # 7. Fully non-mutating dry-run boundary
    # ------------------------------------------------------------------
    if dry_run:
        result["status"] = "dry_run_ready"
        result["ok"] = True
        result["checkpoint"] = None
        result["checkpoint_preview"] = {
            "would_create": loaded_policy.require_checkpoint,
            "branch": branch,
            "task": task,
            "provider": selected_provider_key,
            "file_count": len(generation.files),
            "write_plan": write_plan,
        }
        result["run_state_preview"] = {
            "would_persist": True,
            "status": "dry_run_ready",
            "branch": branch,
            "task": task,
        }
        result["written"] = []
        result["checks_ok"] = None
        result["diff_safe"] = None
        result["next_commands"] = [
            f"kodex app-build {task!r} --apply",
        ]
        return result

    # ------------------------------------------------------------------
    # 8. Checkpoint
    # ------------------------------------------------------------------
    checkpoint, ckpt_path = create_checkpoint(
        repo_root=root,
        branch=branch,
        task=task,
        provider=selected_provider_key,
        write_plan=write_plan,
        files=generation.files,
    )
    result["checkpoint"] = str(ckpt_path)
    result["metadata_written"].append(str(ckpt_path))

    # ------------------------------------------------------------------
    # 9. Apply files
    # ------------------------------------------------------------------
    patch = apply_generated_files(root, generation.files, policy=loaded_policy, dry_run=False)
    result["written"] = patch.written

    if not patch.ok:
        result["status"] = "apply_failed"
        result["diagnosis"] = diagnose_text("; ".join(patch.errors))
        return result

    # ------------------------------------------------------------------
    # 10. Run checks
    # ------------------------------------------------------------------
    checks_ok, check_output, check_details = _run_checks(root, loaded_policy)
    result["checks_ok"] = checks_ok
    result["checks"] = check_details

    # ------------------------------------------------------------------
    # 11. Diff safety
    # ------------------------------------------------------------------
    diff = _safe_diff(root)
    result["diff_safe"] = bool(diff)

    # ------------------------------------------------------------------
    # 12. Repair loop (if checks failed and policy allows)
    # ------------------------------------------------------------------
    if not checks_ok and loaded_policy.repair_loop.enabled:
        repair = run_repair_loop(
            task=task,
            context=context,
            provider=selected_provider,
            failure_log=check_output,
            max_attempts=loaded_policy.repair_loop.max_attempts,
        )
        result["repair_attempts"] = repair.to_context()["attempts"]
        if repair.ok:
            repair_patch = apply_generated_files(root, repair.final_files, policy=loaded_policy, dry_run=False)
            result["written"].extend(repair_patch.written)
            checks_ok, check_output, check_details = _run_checks(root, loaded_policy)
            result["checks_ok"] = checks_ok
            result["checks"] = check_details

    # ------------------------------------------------------------------
    # 13. Final status — always stop before commit/push
    # ------------------------------------------------------------------
    if checks_ok:
        result["status"] = "ready_for_commit"
        result["ok"] = True
        result["next_commands"] = [
            f"git add {' '.join(result['written'])}",
            f'git commit -m "kodex: {task.lower()}"',
            f"git push -u origin {branch}",
        ]
    else:
        result["status"] = "checks_failed"
        result["diagnosis"] = diagnose_text(check_output)

    # Persist run state only in real apply mode.
    store = RunStore(root)
    run = RunState.create(task=task, path=root)
    run.update(branch=branch, status=result["status"])
    run_path = store.save(run)
    result["metadata_written"].append(str(run_path))

    return result
