from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

CLEAN_PATTERNS = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
]

CLEAN_SUFFIXES = [
    ".egg-info",
]

PROTECTED_NAMES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
}


def _is_cleanable(path: Path) -> bool:
    name = path.name
    if name in PROTECTED_NAMES:
        return False
    if name in CLEAN_PATTERNS:
        return True
    return any(name.endswith(suffix) for suffix in CLEAN_SUFFIXES)


def find_clean_targets(repo_root: str | Path = ".") -> list[str]:
    """Find generated local artifacts that are safe to remove."""
    root = Path(repo_root).expanduser().resolve()
    targets: list[str] = []

    for path in root.rglob("*"):
        if any(part in PROTECTED_NAMES for part in path.relative_to(root).parts):
            continue
        if _is_cleanable(path):
            targets.append(str(path.relative_to(root)))

    return sorted(set(targets))


def clean_repo(repo_root: str | Path = ".", *, apply: bool = False) -> dict[str, Any]:
    """Preview or remove generated local artifacts.

    The cleaner only targets common generated cache/build metadata folders.
    It never removes source files, git metadata, virtualenvs, node_modules, or secrets.
    """
    root = Path(repo_root).expanduser().resolve()
    targets = find_clean_targets(root)
    removed: list[str] = []

    if apply:
        for target in targets:
            full_path = root / target
            if full_path.exists() and _is_cleanable(full_path):
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                else:
                    full_path.unlink()
                removed.append(target)

    return {
        "path": str(root),
        "mode": "apply" if apply else "preview",
        "targets": targets,
        "removed": removed,
        "ok": True,
    }
