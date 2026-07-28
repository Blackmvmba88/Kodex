from __future__ import annotations

import json
from pathlib import Path
from typing import Any


STACK_MARKERS = {
    "python": ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"],
    "node": ["package.json", "pnpm-lock.yaml", "yarn.lock", "package-lock.json"],
    "rust": ["Cargo.toml"],
    "go": ["go.mod"],
    "docker": ["Dockerfile", "docker-compose.yml", "compose.yml"],
    "github-actions": [".github/workflows"],
}

ENTRYPOINT_CANDIDATES = [
    "main.py",
    "app.py",
    "server.py",
    "src/main.ts",
    "src/main.tsx",
    "src/App.tsx",
    "index.js",
    "src/index.ts",
]

TEST_MARKERS = [
    "tests",
    "test",
    "pytest.ini",
    "vitest.config.ts",
    "jest.config.js",
]


def _exists(root: Path, marker: str) -> bool:
    return (root / marker).exists()


def detect_stack(root: Path) -> list[str]:
    stack: list[str] = []
    for name, markers in STACK_MARKERS.items():
        if any(_exists(root, marker) for marker in markers):
            stack.append(name)
    return stack


def detect_entrypoints(root: Path) -> list[str]:
    return [candidate for candidate in ENTRYPOINT_CANDIDATES if _exists(root, candidate)]


def detect_tests(root: Path) -> list[str]:
    return [marker for marker in TEST_MARKERS if _exists(root, marker)]


def detect_commands(root: Path) -> dict[str, str]:
    commands: dict[str, str] = {}

    package_json = root / "package.json"
    if package_json.exists():
        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            scripts = data.get("scripts", {})
            for key in ["dev", "test", "build", "lint"]:
                if key in scripts:
                    commands[key] = f"npm run {key}"
        except json.JSONDecodeError:
            commands["package_json_error"] = "package.json is not valid JSON"

    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        if (root / "tests").exists() or (root / "pytest.ini").exists():
            commands.setdefault("test", "pytest")

    return commands


def detect_risks(root: Path, stack: list[str], tests: list[str]) -> list[str]:
    risks: list[str] = []
    if not tests:
        risks.append("no tests detected")
    if "github-actions" not in stack:
        risks.append("no GitHub Actions workflow detected")
    if not (root / "README.md").exists():
        risks.append("no README.md detected")
    return risks


def scan_repo(path: str | Path) -> dict[str, Any]:
    root = Path(path).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repo path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repo path is not a directory: {root}")

    stack = detect_stack(root)
    tests = detect_tests(root)

    return {
        "name": root.name,
        "path": str(root),
        "stack": stack,
        "entrypoints": detect_entrypoints(root),
        "tests": tests,
        "commands": detect_commands(root),
        "risks": detect_risks(root, stack, tests),
    }
