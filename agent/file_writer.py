from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.approval import review_write_plan


def write_files(
    repo_root: str | Path,
    file_changes: dict[str, str],
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Write a set of UTF-8 files after policy review."""
    root = Path(repo_root).expanduser().resolve()
    decision = review_write_plan(root, file_changes, force=force)

    result: dict[str, Any] = {
        "allowed": decision.allowed,
        "reasons": decision.reasons,
        "warnings": decision.warnings,
        "written": [],
    }

    if not decision.allowed:
        return result

    for relative_path, content in file_changes.items():
        target = (root / relative_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        result["written"].append(relative_path)

    return result
