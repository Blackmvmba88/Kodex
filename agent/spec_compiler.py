from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_SPEC_SOURCES = ["README.md", "SPEC.md", "AGENTS.md"]


@dataclass(frozen=True)
class CompiledSpec:
    """Normalized product/task specification compiled from repo documents."""

    task: str
    sources: list[str]
    title: str
    body: str
    requirements: list[str] = field(default_factory=list)
    missing_sources: list[str] = field(default_factory=list)

    def to_context(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "sources": self.sources,
            "title": self.title,
            "body": self.body,
            "requirements": self.requirements,
            "missing_sources": self.missing_sources,
        }


def _extract_title(body: str, fallback: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def _extract_requirements(body: str) -> list[str]:
    requirements: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            requirements.append(stripped[2:].strip())
        elif stripped.startswith(("[ ]", "[x]", "[X]")):
            requirements.append(stripped[3:].strip())
    return [item for item in requirements if item]


def compile_spec(
    repo_root: str | Path = ".",
    *,
    task: str = "Implement MVP",
    sources: list[str] | None = None,
) -> CompiledSpec:
    """Compile README/SPEC/AGENTS-style documents into a normalized spec."""
    root = Path(repo_root).expanduser().resolve()
    requested_sources = sources or DEFAULT_SPEC_SOURCES

    existing: list[str] = []
    missing: list[str] = []
    chunks: list[str] = []

    for source in requested_sources:
        path = root / source
        if path.exists() and path.is_file():
            existing.append(source)
            chunks.append(f"# Source: {source}\n\n{path.read_text(encoding='utf-8')}")
        else:
            missing.append(source)

    body = "\n\n---\n\n".join(chunks).strip()
    title = _extract_title(body, fallback=task)
    requirements = _extract_requirements(body)

    return CompiledSpec(
        task=task,
        sources=existing,
        title=title,
        body=body,
        requirements=requirements,
        missing_sources=missing,
    )
