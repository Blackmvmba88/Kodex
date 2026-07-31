from __future__ import annotations

from typing import Any

from agent.providers.base import ModelProvider, ProviderRequest, ProviderResponse


class OpenAIProvider(ModelProvider):
    """OpenAI provider placeholder.

    This class intentionally does not make network calls yet. It locks the
    provider contract before secrets, SDK configuration, retries, and cost
    controls are introduced.
    """

    name = "openai"

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse(
            provider=self.name,
            ok=False,
            content="",
            files={},
            metadata={
                "status": "not_configured",
                "reason": "OpenAI provider contract exists, but runtime calls are disabled",
                "required_next_step": "configure SDK adapter, model, API key handling, and safety budget",
                "task": request.task,
            },
        )
