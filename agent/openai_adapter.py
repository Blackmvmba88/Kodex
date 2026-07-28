from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class AdapterResult:
    ok: bool
    mode: str
    content: str
    metadata: dict[str, Any]


def build_system_prompt() -> str:
    return """You are Kodex, the BlackMamba Dev Agent.
Inspect first, propose small safe changes, avoid destructive actions, and produce executable engineering plans."""


def dry_run_response(task: str, project: dict[str, Any] | None = None) -> AdapterResult:
    name = project.get("name") if project else "unknown"
    content = (
        f"Dry-run plan for {name}:\n"
        "1. Inspect current repo map and git status.\n"
        "2. Identify the smallest files affected by the task.\n"
        "3. Make a minimal patch locally.\n"
        "4. Run detected checks.\n"
        "5. Inspect diff guard warnings.\n"
        "6. Prepare commit/PR text after human review.\n"
        f"\nTask: {task}"
    )
    return AdapterResult(ok=True, mode="dry-run", content=content, metadata={"project": name})


def ask_model(task: str, project: dict[str, Any] | None = None, dry_run: bool = True) -> AdapterResult:
    """Return a model-assisted plan.

    This adapter is intentionally conservative. The first implementation keeps
    dry-run behavior as the default. A real API-backed implementation can be
    wired here once credentials and model policy are configured locally.
    """
    if dry_run or not os.getenv("OPENAI_API_KEY"):
        return dry_run_response(task, project)

    return AdapterResult(
        ok=False,
        mode="not-configured",
        content="OPENAI_API_KEY detected, but live model execution is not wired yet.",
        metadata={"reason": "adapter stub"},
    )
