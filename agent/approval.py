from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_MAX_FILES = 8
DEFAULT_MAX_BYTES = 120_000
BLOCKED_PATH_PARTS = {".git", "node_modules", ".venv", "venv", "__pycache__"}
SENSITIVE_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}


@dataclass(frozen=True)
class ApprovalDecision:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _is_sensitive_path(path: Path) -> bool:
    parts = set(path.parts)
    if parts & BLOCKED_PATH_PARTS:
        return True
    if path.name in SENSITIVE_NAMES:
        return True
    if path.suffix in SENSITIVE_SUFFIXES:
        return True
    return False


def review_write_plan(
    repo_root: str | Path,
    file_changes: dict[str, str],
    *,
    force: bool = False,
    max_files: int = DEFAULT_MAX_FILES,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> ApprovalDecision:
    """Review a write plan before touching disk.

    The gremlin can move fast, but it does not touch secrets, dependency folders,
    or huge batches unless the caller deliberately forces the operation.
    """
    root = Path(repo_root).expanduser().resolve()
    reasons: list[str] = []
    warnings: list[str] = []

    if len(file_changes) > max_files:
        reasons.append(f"too many files requested: {len(file_changes)} > {max_files}")

    total_bytes = sum(len(content.encode("utf-8")) for content in file_changes.values())
    if total_bytes > max_bytes:
        reasons.append(f"write plan too large: {total_bytes} bytes > {max_bytes}")

    for relative_path in file_changes:
        target = (root / relative_path).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            reasons.append(f"path escapes repo root: {relative_path}")
            continue

        path = Path(relative_path)
        if _is_sensitive_path(path):
            reasons.append(f"blocked sensitive or generated path: {relative_path}")

        if target.exists():
            warnings.append(f"will overwrite existing file: {relative_path}")
        else:
            warnings.append(f"will create new file: {relative_path}")

    if reasons and not force:
        return ApprovalDecision(allowed=False, reasons=reasons, warnings=warnings)

    if reasons and force:
        warnings.extend([f"forced despite: {reason}" for reason in reasons])

    return ApprovalDecision(allowed=True, reasons=[] if force else reasons, warnings=warnings)
