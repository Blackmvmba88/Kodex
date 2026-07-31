from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent.diagnostics import diagnose_text
from agent.providers.base import ModelProvider, ProviderRequest, ProviderResponse


@dataclass
class RepairAttempt:
    index: int
    diagnosis: dict[str, Any]
    provider_ok: bool
    files: dict[str, str] = field(default_factory=dict)
    message: str = ""


@dataclass
class RepairResult:
    ok: bool
    attempts: list[RepairAttempt]
    final_files: dict[str, str] = field(default_factory=dict)
    status: str = "not_run"

    def to_context(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "status": self.status,
            "attempts": [
                {
                    "index": attempt.index,
                    "diagnosis": attempt.diagnosis,
                    "provider_ok": attempt.provider_ok,
                    "files": attempt.files,
                    "message": attempt.message,
                }
                for attempt in self.attempts
            ],
            "final_files": self.final_files,
        }


def run_repair_loop(
    *,
    task: str,
    context: dict[str, Any],
    provider: ModelProvider,
    failure_log: str,
    max_attempts: int = 1,
) -> RepairResult:
    """Run a bounded repair contract over a failure log.

    This is intentionally conservative: it asks the provider for candidate repair
    files but does not write, commit, push, or mutate the repository.
    """
    attempts: list[RepairAttempt] = []
    if max_attempts <= 0:
        return RepairResult(ok=False, attempts=[], status="disabled")

    diagnosis = diagnose_text(failure_log)
    request_context = {
        **context,
        "repair": {
            "failure_log": failure_log,
            "diagnosis": diagnosis,
            "max_attempts": max_attempts,
        },
    }

    final_files: dict[str, str] = {}
    for index in range(1, max_attempts + 1):
        response: ProviderResponse = provider.generate(
            ProviderRequest(
                task=f"Repair failure for task: {task}",
                context=request_context,
                constraints=[
                    "Return only candidate files; do not assume writes are allowed.",
                    "Prefer minimal changes that directly address the diagnosis.",
                ],
            )
        )
        final_files = response.files if response.ok else {}
        attempts.append(
            RepairAttempt(
                index=index,
                diagnosis=diagnosis,
                provider_ok=response.ok,
                files=final_files,
                message=response.content,
            )
        )
        if response.ok and final_files:
            return RepairResult(ok=True, attempts=attempts, final_files=final_files, status="candidate_repair_ready")

    return RepairResult(ok=False, attempts=attempts, final_files={}, status="needs_human_review")
