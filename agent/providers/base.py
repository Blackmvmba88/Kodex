from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class ProviderRequest:
    """Structured request sent to a model provider."""

    task: str
    system: str
    context: dict
    constraints: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProviderResult:
    """Structured model-provider response normalized for Kodex."""

    ok: bool
    message: str
    files: dict[str, str] = field(default_factory=dict)
    diagnostics: list[str] = field(default_factory=list)
    raw: str | None = None


class ModelProvider(Protocol):
    """Provider contract used by the app-building pipeline."""

    name: str

    def generate(self, request: ProviderRequest) -> ProviderResult:
        """Generate candidate file changes for a task."""
