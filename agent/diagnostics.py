from __future__ import annotations

import re
from pathlib import Path
from typing import Any


_PHASE_HINTS: list[tuple[str, str]] = [
    ("pip install", "INSTALL"),
    ("Preparing editable metadata", "INSTALL"),
    ("ERROR: Could not", "INSTALL"),
    ("FAILED", "TEST"),
    ("short test summary info", "TEST"),
    ("AssertionError", "TEST"),
    ("ModuleNotFoundError", "IMPORT"),
    ("ImportError", "IMPORT"),
    ("No such command", "CLI"),
    ("Usage:", "CLI"),
    ("git:", "GIT"),
    ("not a git repository", "GIT"),
    ("blocked_dirty_worktree", "GIT"),
    ("diff guard", "DIFF"),
    ("unsafe", "DIFF"),
    ("permission denied", "PERMISSION"),
    ("Permission denied", "PERMISSION"),
]


_FIX_HINTS: dict[str, str] = {
    "INSTALL": "reinstall the editable package and inspect pyproject.toml/dependencies",
    "TEST": "inspect the failing test contract, then update implementation or test expectation",
    "IMPORT": "verify module path, package exports, and editable install state",
    "CLI": "verify the command is wired in agent/main.py and reinstall editable package",
    "GIT": "inspect git status/branch and clean, commit, or switch branches before retrying",
    "DIFF": "inspect diff output and confirm no risky or secret-like changes were introduced",
    "PERMISSION": "check filesystem or GitHub permission boundaries before retrying",
    "UNKNOWN": "read the first traceback/error block and classify it before changing code",
}


def _detect_phase(text: str) -> str:
    for needle, phase in _PHASE_HINTS:
        if needle in text:
            return phase
    return "UNKNOWN"


def _extract_failed_file(text: str) -> str | None:
    patterns = [
        r"FAILED\s+([^\s:]+)",
        r"([^\s:]+\.py):\d+:\s+AssertionError",
        r"File \"([^\"]+\.py)\"",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def _extract_reason(text: str, phase: str) -> str:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    interesting_markers = (
        "AssertionError",
        "ModuleNotFoundError",
        "ImportError",
        "No such command",
        "FAILED",
        "ERROR:",
        "git:",
        "blocked_",
    )
    for line in lines:
        if any(marker in line for marker in interesting_markers):
            return line.strip()
    if lines:
        return lines[-1].strip()
    return f"no explicit error text detected for phase {phase}"


def diagnose_text(text: str) -> dict[str, Any]:
    """Classify raw terminal/log text into a compact, readable diagnostic."""
    phase = _detect_phase(text)
    failed_file = _extract_failed_file(text)
    reason = _extract_reason(text, phase)
    return {
        "phase": phase,
        "failed_file": failed_file,
        "reason": reason,
        "suggested_fix": _FIX_HINTS.get(phase, _FIX_HINTS["UNKNOWN"]),
        "ok": phase == "UNKNOWN" and not reason,
    }


def diagnose_file(path: str | Path) -> dict[str, Any]:
    """Read a log file and diagnose its likely failure phase."""
    log_path = Path(path).expanduser().resolve()
    if not log_path.exists():
        return {
            "phase": "FILE",
            "failed_file": str(log_path),
            "reason": "diagnostic log file does not exist",
            "suggested_fix": "write terminal output to a file or pass an existing log path",
            "ok": False,
        }
    return {
        "path": str(log_path),
        **diagnose_text(log_path.read_text(encoding="utf-8")),
    }
