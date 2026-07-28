from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_MEMORY_PATH = Path("memory/projects.json")


def load_projects(memory_path: str | Path = DEFAULT_MEMORY_PATH) -> list[dict[str, Any]]:
    path = Path(memory_path)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_project(project: dict[str, Any], memory_path: str | Path = DEFAULT_MEMORY_PATH) -> None:
    path = Path(memory_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    projects = load_projects(path)
    projects = [item for item in projects if item.get("path") != project.get("path")]
    projects.append(project)

    path.write_text(json.dumps(projects, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def find_project(name: str | None, memory_path: str | Path = DEFAULT_MEMORY_PATH) -> dict[str, Any] | None:
    if not name:
        return None

    needle = name.lower()
    for project in load_projects(memory_path):
        candidates = [
            str(project.get("name", "")).lower(),
            str(project.get("path", "")).lower(),
        ]
        if any(needle in candidate for candidate in candidates):
            return project
    return None
