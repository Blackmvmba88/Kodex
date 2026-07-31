from __future__ import annotations

from agent.providers.base import ModelProvider, ProviderRequest, ProviderResponse


class OllamaProvider(ModelProvider):
    """Ollama provider placeholder.

    This class intentionally does not make local HTTP calls yet. It locks the
    provider contract before model discovery, endpoint configuration, timeout
    handling, and local resource limits are introduced.
    """

    name = "ollama"

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse(
            provider=self.name,
            ok=False,
            content="",
            files={},
            metadata={
                "status": "not_configured",
                "reason": "Ollama provider contract exists, but runtime calls are disabled",
                "required_next_step": "configure Ollama endpoint, model selection, timeout, and resource budget",
                "task": request.task,
            },
        )
