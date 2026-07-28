from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

DEFAULT_TIMEOUT_SECONDS = 120


def run_command(command: str, path: str | Path = ".", timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict[str, Any]:
    root = Path(path).expanduser().resolve()
    try:
        result = subprocess.run(
            command,
            cwd=root,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "path": str(root),
            "ok": False,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "error": f"command timed out after {timeout}s",
        }

    return {
        "command": command,
        "path": str(root),
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def run_project_checks(project: dict[str, Any], timeout: int = DEFAULT_TIMEOUT_SECONDS) -> list[dict[str, Any]]:
    commands = project.get("commands", {})
    path = project.get("path", ".")

    preferred = ["lint", "test", "build"]
    checks: list[dict[str, Any]] = []

    for name in preferred:
        command = commands.get(name)
        if command:
            result = run_command(command, path=path, timeout=timeout)
            result["name"] = name
            checks.append(result)

    if not checks:
        checks.append(
            {
                "name": "none",
                "command": None,
                "path": str(Path(path).expanduser().resolve()),
                "ok": False,
                "returncode": None,
                "stdout": "",
                "stderr": "",
                "error": "no check commands detected",
            }
        )

    return checks
