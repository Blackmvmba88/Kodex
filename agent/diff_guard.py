from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.git_ops import _run_git

SENSITIVE_PATTERNS = [
    ".env",
    "id_rsa",
    "id_ed25519",
    "secret",
    "token",
    "password",
    "credential",
]

DESTRUCTIVE_HINTS = [
    " delete mode ",
    "deleted file mode",
]


def get_diff(path: str | Path = ".") -> dict[str, Any]:
    root = Path(path).expanduser().resolve()
    diff = _run_git(["diff", "--stat"], root)
    patch = _run_git(["diff", "--name-status"], root)
    return {
        "path": str(root),
        "stat": diff.get("stdout", ""),
        "name_status": patch.get("stdout", ""),
        "ok": diff.get("ok", False) and patch.get("ok", False),
    }


def inspect_diff(path: str | Path = ".") -> dict[str, Any]:
    diff = get_diff(path)
    text = "\n".join([diff.get("stat", ""), diff.get("name_status", "")]).lower()

    warnings: list[str] = []
    for pattern in SENSITIVE_PATTERNS:
        if pattern in text:
            warnings.append(f"sensitive-looking path or keyword detected: {pattern}")

    for hint in DESTRUCTIVE_HINTS:
        if hint in text:
            warnings.append(f"destructive diff hint detected: {hint.strip()}")

    diff["safe"] = not warnings
    diff["warnings"] = warnings
    return diff
