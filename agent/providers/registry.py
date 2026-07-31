from __future__ import annotations

from collections.abc import Callable

from agent.providers.base import ModelProvider
from agent.providers.noop_provider import NoopProvider
from agent.providers.ollama_provider import OllamaProvider
from agent.providers.openai_provider import OpenAIProvider


ProviderFactory = Callable[[], ModelProvider]

_PROVIDER_FACTORIES: dict[str, ProviderFactory] = {
    "noop": NoopProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
}


def available_providers() -> list[str]:
    """Return registered provider names in deterministic order."""
    return sorted(_PROVIDER_FACTORIES)


def register_provider(
    name: str,
    factory: ProviderFactory,
    *,
    replace: bool = False,
) -> None:
    """Register a provider factory for tests or external integrations."""
    normalized = name.strip().lower()
    if not normalized:
        raise ValueError("provider name cannot be empty")
    if normalized in _PROVIDER_FACTORIES and not replace:
        raise ValueError(f"provider already registered: {normalized}")
    _PROVIDER_FACTORIES[normalized] = factory


def get_provider(name: str) -> ModelProvider:
    """Create a provider instance by normalized registry name."""
    normalized = name.strip().lower()
    try:
        factory = _PROVIDER_FACTORIES[normalized]
    except KeyError as exc:
        available = ", ".join(available_providers())
        raise ValueError(f"unknown provider: {name}; available: {available}") from exc
    return factory()
