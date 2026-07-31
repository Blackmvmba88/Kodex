from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.context_builder import build_context
from agent.providers.registry import get_provider
from agent.repair_loop import run_repair_loop
from agent.spec_compiler import compile_spec


def build_app(
    repository: str | Path = ".",
    *,
    sources: list[str] | None = None,
    task: str = "Implement MVP",
    provider: str = "noop",
    max_repair_attempts: int = 0,
) -> dict[str, Any]:
    """Compile specs and produce a policy-reviewed app patch preview.

    This function never writes files, creates branches, commits, pushes, or calls
    external transports that a provider has not explicitly implemented.
    """
    root = Path(repository).expanduser().resolve()
    compiled = compile_spec(root, task=task, sources=sources)
    context = build_context(root, compiled)
    selected_provider = get_provider(provider)
    repair = run_repair_loop(
        task=task,
        context=context,
        provider=selected_provider,
        repo_root=root,
        max_attempts=max_repair_attempts,
    )

    ok = bool(repair["ok"])

    return {
        "task": task,
        "repository": str(root),
        "mode": "app_builder_preview",
        "provider": selected_provider.name,
        "max_repair_attempts": max_repair_attempts,
        "ok": ok,
        "status": repair["status"],
        "spec": compiled.to_context(),
        "context": context,
        "generation": repair["generation"],
        "write_plan": repair["patch"],
        "repair": {
            "attempt_count": repair["attempt_count"],
            "max_attempts": repair["max_attempts"],
            "history": repair["history"],
        },
        "next_step": (
            "review generated files, then pass the accepted generation to apply_generated_patch"
            if ok
            else "inspect provider diagnostics and repair history"
        ),
    }
