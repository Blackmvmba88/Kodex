from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass
class RunState:
    run_id: str
    task: str
    path: str
    phase: str = "created"
    status: str = "running"
    branch: str | None = None
    files_changed: list[str] = field(default_factory=list)
    checks: list[dict[str, Any]] = field(default_factory=list)
    commit: str | None = None
    pr: int | None = None
    error: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def create(cls, task: str, path: str | Path) -> "RunState":
        return cls(run_id=f"run-{uuid4().hex[:12]}", task=task, path=str(Path(path).expanduser().resolve()))

    def update(self, **changes: Any) -> "RunState":
        for key, value in changes.items():
            if not hasattr(self, key):
                raise AttributeError(f"unknown run-state field: {key}")
            setattr(self, key, value)
        self.updated_at = datetime.now(timezone.utc).isoformat()
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunState":
        return cls(**data)


class RunStore:
    def __init__(self, repo_root: str | Path = ".") -> None:
        self.repo_root = Path(repo_root).expanduser().resolve()
        self.runs_dir = self.repo_root / ".kodex" / "runs"

    def save(self, state: RunState) -> Path:
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        target = self.runs_dir / f"{state.run_id}.json"
        temp = target.with_suffix(".json.tmp")
        temp.write_text(json.dumps(state.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temp.replace(target)
        return target

    def load(self, run_id: str) -> RunState:
        target = self.runs_dir / f"{run_id}.json"
        data = json.loads(target.read_text(encoding="utf-8"))
        return RunState.from_dict(data)

    def latest(self) -> RunState | None:
        if not self.runs_dir.exists():
            return None
        files = sorted(self.runs_dir.glob("run-*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
        return self.load(files[0].stem) if files else None
