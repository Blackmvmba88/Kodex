from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.code_generator import generate_code
from agent.generated_patch import prepare_generated_patch
from agent.providers.base import ModelProvider, ProviderResult


def _serialize_generation(result: ProviderResult) -> dict[str, Any]:
    return {
        "ok": result.ok,
        "message": result.message,
        "files": dict(result.files),
        "diagnostics": list(result.diagnostics),
        "raw": result.raw,
    }


def _build_feedback(generation: ProviderResult, patch: dict[str, Any]) -> list[str]:
    feedback = list(generation.diagnostics)
    feedback.extend(str(reason) for reason in patch.get("reasons", []))
    if not feedback:
        feedback.append("generation did not satisfy the write-plan contract")
    return feedback


def run_repair_loop(
    *,
    task: str,
    context: dict[str, Any],
    provider: ModelProvider,
    repo_root: str | Path,
    max_attempts: int = 0,
) -> dict[str, Any]:
    """Generate and validate bounded candidate patches with auditable retries.

    ``max_attempts`` counts retries after the initial generation. The function
    never writes files, creates branches, commits, or performs external actions.
    """
    if max_attempts < 0:
        raise ValueError("max_attempts cannot be negative")

    history: list[dict[str, Any]] = []
    feedback: list[str] = []
    final_generation: ProviderResult | None = None
    final_patch: dict[str, Any] | None = None

    for attempt in range(max_attempts + 1):
        generation = generate_code(
            task,
            context,
            provider,
            feedback=feedback,
            attempt=attempt,
        )
        patch = prepare_generated_patch(repo_root, generation)
        accepted = bool(patch.get("ready"))

        history.append(
            {
                "attempt": attempt,
                "accepted": accepted,
                "generation": _serialize_generation(generation),
                "patch": patch,
            }
        )
        final_generation = generation
        final_patch = patch

        if accepted:
            break
        feedback = _build_feedback(generation, patch)

    assert final_generation is not None
    assert final_patch is not None

    return {
        "ok": bool(final_patch.get("ready")),
        "status": "ready_for_review" if final_patch.get("ready") else "repair_exhausted",
        "attempt_count": len(history),
        "max_attempts": max_attempts,
        "history": history,
        "generation": _serialize_generation(final_generation),
        "patch": final_patch,
    }
