from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.approval import evaluate_write_plan
from agent.code_generator import generate_code
from agent.context_builder import build_context
from agent.providers.noop_provider import NoopProvider
from agent.spec_compiler import compile_spec


def _provider_by_name(name: str):
    if name == "noop":
        return NoopProvider()
    raise ValueError(f"unknown provider: {name}")


def build_app(
    repository: str | Path = ".",
    *,
    sources: list[str] | None = None,
    task: str = "Implement MVP",
    provider: str = "noop",
    max_repair_attempts: int = 0,
) -> dict[str, Any]:
    """Compile a spec, build context, request generation, and validate the write plan.

    This function does not write files, create branches, commit, or push. It is the
    first safe contract for turning README/SPEC/AGENTS inputs into candidate
    multi-file changes.
    """
    root = Path(repository).expanduser().resolve()
    compiled = compile_spec(root, task=task, sources=sources)
    context = build_context(root, compiled)
    selected_provider = _provider_by_name(provider)
    generation = generate_code(task, context, selected_provider)
    write_plan = evaluate_write_plan(root, generation.files)

    ok = bool(generation.ok) and bool(write_plan.get("allowed"))

    return {
        "task": task,
        "repository": str(root),
        "mode": "app_builder_preview",
        "provider": provider,
        "max_repair_attempts": max_repair_attempts,
        "ok": ok,
        "status": "ready_for_review" if ok else "needs_attention",
        "spec": compiled.to_context(),
        "context": context,
        "generation": {
            "ok": generation.ok,
            "message": generation.message,
            "files": generation.files,
            "diagnostics": generation.diagnostics,
        },
        "write_plan": write_plan,
        "next_step": "review generated files, then pass them through guarded patch/apply flow" if ok else None,
    }
