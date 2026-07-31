from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.approval import review_write_plan
from agent.file_writer import write_files
from agent.providers.base import ProviderResult


def prepare_generated_patch(
    repo_root: str | Path,
    generation: ProviderResult,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Convert provider output into a normalized, policy-reviewed patch packet."""
    decision = review_write_plan(repo_root, generation.files, force=force)
    ready = bool(generation.ok) and bool(generation.files) and decision.allowed

    reasons = list(decision.reasons)
    if not generation.ok:
        reasons.append(generation.message)
    if not generation.files:
        reasons.append("provider returned no file changes")

    return {
        "ready": ready,
        "allowed": decision.allowed,
        "provider_ok": generation.ok,
        "files": dict(generation.files),
        "reasons": reasons,
        "warnings": list(decision.warnings),
        "diagnostics": list(generation.diagnostics),
    }


def apply_generated_patch(
    repo_root: str | Path,
    generation: ProviderResult,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Apply provider-generated files only after the handoff is explicitly ready."""
    packet = prepare_generated_patch(repo_root, generation, force=force)
    if not packet["ready"]:
        return {
            "ok": False,
            "status": "blocked",
            "patch": packet,
            "write_result": None,
        }

    write_result = write_files(repo_root, generation.files, force=force)
    return {
        "ok": bool(write_result.get("allowed")),
        "status": "applied" if write_result.get("allowed") else "blocked",
        "patch": packet,
        "write_result": write_result,
    }
