from __future__ import annotations

from typing import Callable

from agent.providers.base import ModelProvider
from agent.providers.noop_provider import NoopProvider
from agent.providers.openai_provider import OpenAIProvider
from agent.providers.ollama_provider import OllamaProvider

ProviderFactory = Callable[[], ModelProvider]

_PROVIDER_FACTORIES: dict[str, ProviderFactory] = {
    "noop": NoopProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
}


def available_providers() -> list[str]:
    return sorted(_PROVIDER_FACTORIES)


def get_provider(name: str = "noop") -> ModelProvider:
    key = name.strip().lower()
    if key not in _PROVIDER_FACTORIES:
        raise ValueError(f"unknown provider: {name}. Available: {', '.join(available_providers())}")
    return _PROVIDER_FACTORIES[key]()
