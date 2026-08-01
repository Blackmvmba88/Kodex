from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Any


@dataclass(frozen=True)
class ProviderRequest:
    """Structured request sent to a model provider."""

    task: str
    context: dict
    constraints: list[str] = field(default_factory=list)
    system: str = ""


@dataclass(frozen=True)
class ProviderResult:
    """Structured model-provider response normalized for Kodex."""

    ok: bool
    message: str = ""
    files: dict[str, str] = field(default_factory=dict)
    diagnostics: list[str] = field(default_factory=list)
    raw: str | None = None
    # Extended fields used by openai/ollama providers
    provider: str = ""
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# Public alias — some modules import ProviderResponse
ProviderResponse = ProviderResult


class ModelProvider(Protocol):
    """Provider contract used by the app-building pipeline."""

    name: str

    def generate(self, request: ProviderRequest) -> ProviderResult:
        """Generate candidate file changes for a task."""

