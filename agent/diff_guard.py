from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.git_ops import is_git_repo, run_git

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

    if not is_git_repo(root):
        return {
            "path": str(root),
            "stat": "",
            "name_status": "",
            "ok": False,
            "error": "not a git repository",
        }

    diff = run_git(root, ["diff", "--stat"])
    patch = run_git(root, ["diff", "--name-status"])

    return {
        "path": str(root),
        "stat": diff.stdout,
        "name_status": patch.stdout,
        "ok": diff.returncode == 0 and patch.returncode == 0,
        "error": (diff.stderr or patch.stderr).strip() or None,
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

    diff["safe"] = diff.get("ok", False) and not warnings
    diff["warnings"] = warnings
    return diff
