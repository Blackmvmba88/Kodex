from __future__ import annotations

from pathlib import Path

import pytest

from agent.checkpoint import Checkpoint, CheckpointStore, create_checkpoint


class TestCheckpoint:
    def test_id_is_generated(self):
        ckpt = Checkpoint()
        assert ckpt.checkpoint_id.startswith("ckpt-")

    def test_round_trip(self):
        ckpt = Checkpoint(branch="feat/x", task="do thing", provider="noop")
        recovered = Checkpoint.from_dict(ckpt.to_dict())
        assert recovered.branch == "feat/x"
        assert recovered.task == "do thing"
        assert recovered.checkpoint_id == ckpt.checkpoint_id

    def test_to_json_is_valid(self):
        import json

        ckpt = Checkpoint(files={"agent/foo.py": "x = 1\n"})
        parsed = json.loads(ckpt.to_json())
        assert parsed["files"]["agent/foo.py"] == "x = 1\n"


class TestCheckpointStore:
    def test_save_and_load(self, tmp_path):
        store = CheckpointStore(tmp_path)
        ckpt = Checkpoint(branch="kodex/write-activation", task="MVP")
        path = store.save(ckpt)
        assert path.exists()
        loaded = store.load(ckpt.checkpoint_id)
        assert loaded.branch == "kodex/write-activation"

    def test_latest_returns_most_recent(self, tmp_path):
        store = CheckpointStore(tmp_path)
        c1 = Checkpoint(task="first")
        c2 = Checkpoint(task="second")
        store.save(c1)
        store.save(c2)
        latest = store.latest()
        assert latest is not None
        assert latest.task == "second"

    def test_latest_returns_none_when_empty(self, tmp_path):
        store = CheckpointStore(tmp_path)
        assert store.latest() is None

    def test_list_all(self, tmp_path):
        store = CheckpointStore(tmp_path)
        for i in range(3):
            store.save(Checkpoint(task=f"task-{i}"))
        assert len(store.list_all()) == 3


class TestCreateCheckpoint:
    def test_convenience_function(self, tmp_path):
        ckpt, path = create_checkpoint(
            repo_root=tmp_path,
            branch="kodex/write-activation",
            task="Implement MVP",
            provider="noop",
            write_plan={"allowed": True},
            files={"agent/foo.py": "pass\n"},
        )
        assert ckpt.checkpoint_id.startswith("ckpt-")
        assert path.exists()
        assert path.suffix == ".json"
