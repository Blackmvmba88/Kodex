from __future__ import annotations

import os

from agent.providers.base import ProviderRequest, ProviderResult


class OllamaProvider:
    """Safe local Ollama provider boundary with transport disabled by default."""

    name = "ollama"

    def __init__(
        self,
        *,
        model: str | None = None,
        host: str | None = None,
    ) -> None:
        self.model = model or os.getenv("KODEX_OLLAMA_MODEL")
        self.host = host or os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")

    def generate(self, request: ProviderRequest) -> ProviderResult:
        diagnostics = [
            f"configured host: {self.host}",
            "no local network request was attempted",
        ]
        if not self.model:
            diagnostics.insert(0, "missing KODEX_OLLAMA_MODEL configuration")
            return ProviderResult(
                ok=False,
                message="ollama provider is not configured",
                diagnostics=diagnostics,
            )

        diagnostics.insert(0, f"configured model: {self.model}")
        diagnostics.append("implement the transport behind this provider boundary before enabling it")
        return ProviderResult(
            ok=False,
            message="ollama provider transport is not implemented yet",
            diagnostics=diagnostics,
        )
