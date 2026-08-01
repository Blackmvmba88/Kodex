from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent.approval import review_write_plan, ApprovalDecision
from agent.write_policy import WritePolicy, load_write_policy


@dataclass
class PatchResult:
    ok: bool
    written: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    approval: ApprovalDecision | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "written": self.written,
            "skipped": self.skipped,
            "errors": self.errors,
            "approval": {
                "allowed": self.approval.allowed,
                "reasons": self.approval.reasons,
                "warnings": self.approval.warnings,
            } if self.approval else None,
        }


def apply_generated_files(
    repo_root: str | Path,
    files: dict[str, str],
    *,
    policy: WritePolicy | None = None,
    force: bool = False,
    dry_run: bool = False,
) -> PatchResult:
    """Apply *files* (relative-path → content) to disk under *repo_root*.

    The write is gated by approval rules.  Each file is written atomically via a
    temp-file rename.  Blocked paths are always skipped regardless of *force*.

    Args:
        repo_root: Absolute or relative path to the repository root.
        files: Mapping of repo-relative paths to UTF-8 file contents.
        policy: Optional pre-loaded WritePolicy; loads from disk if None.
        force: If True, bypass soft approval limits (but not hard blocked-path rules).
        dry_run: If True, validate and report but do not touch disk.

    Returns:
        PatchResult describing what was (or would be) written.
    """
    root = Path(repo_root).expanduser().resolve()
    loaded_policy = policy or load_write_policy(root)

    # Hard-block sensitive paths regardless of force flag
    clean_files: dict[str, str] = {}
    hard_skipped: list[str] = []
    for rel_path, content in files.items():
        if loaded_policy.is_blocked_path(rel_path):
            hard_skipped.append(rel_path)
        else:
            clean_files[rel_path] = content

    # Soft approval (file count, byte limits, path-escape checks)
    approval = review_write_plan(
        root,
        clean_files,
        force=force,
        max_files=loaded_policy.max_files_per_write,
        max_bytes=loaded_policy.max_total_bytes,
    )

    if not approval.allowed:
        return PatchResult(
            ok=False,
            skipped=hard_skipped,
            errors=[f"write plan rejected: {'; '.join(approval.reasons)}"],
            approval=approval,
        )

    if dry_run:
        return PatchResult(
            ok=True,
            written=[],
            skipped=hard_skipped + list(clean_files.keys()),
            approval=approval,
        )

    written: list[str] = []
    errors: list[str] = []

    for rel_path, content in clean_files.items():
        target = (root / rel_path).resolve()
        try:
            target.relative_to(root)  # redundant safety check
        except ValueError:
            errors.append(f"path escapes repo root (skipped): {rel_path}")
            continue

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_suffix(target.suffix + ".tmp")
            temp.write_text(content, encoding="utf-8")
            temp.replace(target)
            written.append(rel_path)
        except OSError as exc:
            errors.append(f"write failed for {rel_path}: {exc}")

    return PatchResult(
        ok=not errors,
        written=written,
        skipped=hard_skipped,
        errors=errors,
        approval=approval,
    )
