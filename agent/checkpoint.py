from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_CHECKPOINTS_DIR = Path(".kodex") / "checkpoints"


@dataclass
class Checkpoint:
    checkpoint_id: str = field(default_factory=lambda: f"ckpt-{uuid.uuid4().hex[:12]}")
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    branch: str = ""
    task: str = ""
    provider: str = ""
    write_plan: dict[str, Any] = field(default_factory=dict)
    files: dict[str, str] = field(default_factory=dict)
    status: str = "pending"
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Checkpoint":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


class CheckpointStore:
    """Persists checkpoints as JSON under ``<repo_root>/.kodex/checkpoints/``."""

    def __init__(self, repo_root: str | Path = ".") -> None:
        self.repo_root = Path(repo_root).expanduser().resolve()
        self.checkpoints_dir = self.repo_root / _CHECKPOINTS_DIR

    def save(self, checkpoint: Checkpoint) -> Path:
        """Atomically write *checkpoint* to disk; returns the written path."""
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        target = self.checkpoints_dir / f"{checkpoint.checkpoint_id}.json"
        temp = target.with_suffix(".json.tmp")
        temp.write_text(checkpoint.to_json() + "\n", encoding="utf-8")
        temp.replace(target)
        return target

    def load(self, checkpoint_id: str) -> Checkpoint:
        target = self.checkpoints_dir / f"{checkpoint_id}.json"
        data = json.loads(target.read_text(encoding="utf-8"))
        return Checkpoint.from_dict(data)

    def latest(self) -> Checkpoint | None:
        if not self.checkpoints_dir.exists():
            return None
        files = sorted(
            self.checkpoints_dir.glob("ckpt-*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return self.load(files[0].stem) if files else None

    def list_all(self) -> list[Checkpoint]:
        if not self.checkpoints_dir.exists():
            return []
        return [
            self.load(p.stem)
            for p in sorted(self.checkpoints_dir.glob("ckpt-*.json"), key=lambda p: p.stat().st_mtime)
        ]


def create_checkpoint(
    *,
    repo_root: str | Path = ".",
    branch: str,
    task: str,
    provider: str,
    write_plan: dict[str, Any],
    files: dict[str, str],
    metadata: dict[str, Any] | None = None,
) -> tuple[Checkpoint, Path]:
    """Convenience function: build a Checkpoint, save it, return (checkpoint, path)."""
    ckpt = Checkpoint(
        branch=branch,
        task=task,
        provider=provider,
        write_plan=write_plan,
        files=files,
        metadata=metadata or {},
    )
    store = CheckpointStore(repo_root)
    path = store.save(ckpt)
    return ckpt, path
