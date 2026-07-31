from __future__ import annotations

from typing import Any

from agent.providers.base import ModelProvider, ProviderRequest, ProviderResult


SYSTEM_PROMPT = """You are Kodex, a local-first app-building agent.
Return safe, bounded, multi-file changes only. Never include secrets. Never write outside the repository.
Prefer the smallest coherent MVP step that can be tested and reviewed by a human.
""".strip()


DEFAULT_CONSTRAINTS = [
    "Do not write outside the repository root.",
    "Do not create or modify secret files.",
    "Prefer small, reviewable changes.",
    "Include tests when implementation changes behavior.",
]


def generate_code(
    task: str,
    context: dict[str, Any],
    provider: ModelProvider,
    *,
    constraints: list[str] | None = None,
    feedback: list[str] | None = None,
    attempt: int = 0,
) -> ProviderResult:
    """Ask a model provider for candidate file changes using normalized context."""
    request = ProviderRequest(
        task=task,
        system=SYSTEM_PROMPT,
        context=context,
        constraints=constraints or DEFAULT_CONSTRAINTS,
        feedback=feedback or [],
        attempt=attempt,
    )
    return provider.generate(request)
