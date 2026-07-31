from __future__ import annotations

import os

from agent.providers.base import ProviderRequest, ProviderResult


class OpenAIProvider:
    """Safe OpenAI provider boundary.

    The transport is intentionally not implemented yet. This class only validates
    configuration and returns a structured, non-secret diagnostic packet.
    """

    name = "openai"

    def __init__(
        self,
        *,
        model: str | None = None,
        api_key_env: str = "OPENAI_API_KEY",
    ) -> None:
        self.model = model or os.getenv("KODEX_OPENAI_MODEL", "gpt-5.6-codex")
        self.api_key_env = api_key_env

    def generate(self, request: ProviderRequest) -> ProviderResult:
        if not os.getenv(self.api_key_env):
            return ProviderResult(
                ok=False,
                message="openai provider is not configured",
                diagnostics=[
                    f"missing environment variable: {self.api_key_env}",
                    "no network request was attempted",
                ],
            )

        return ProviderResult(
            ok=False,
            message="openai provider transport is not implemented yet",
            diagnostics=[
                f"configured model: {self.model}",
                "credentials were detected but never exposed or transmitted",
                "implement the transport behind this provider boundary before enabling it",
            ],
        )
