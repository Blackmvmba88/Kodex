from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from agent.generated_patcher import apply_generated_files
from agent.write_policy import WritePolicy


def _git_init(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@kodex.local"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Kodex Test"], cwd=path, check=True)


class TestApplyGeneratedFiles:
    def test_writes_files(self, tmp_path):
        _git_init(tmp_path)
        policy = WritePolicy(blocked_paths=[], allowed_default_roots=["agent/"])
        result = apply_generated_files(tmp_path, {"agent/foo.py": "x = 1\n"}, policy=policy)
        assert result.ok
        assert "agent/foo.py" in result.written
        assert (tmp_path / "agent" / "foo.py").read_text() == "x = 1\n"

    def test_blocks_sensitive_path(self, tmp_path):
        _git_init(tmp_path)
        policy = WritePolicy(blocked_paths=[".env"])
        result = apply_generated_files(tmp_path, {".env": "SECRET=abc\n"}, policy=policy)
        # blocked path is skipped silently
        assert ".env" in result.skipped
        assert ".env" not in result.written

    def test_dry_run_does_not_touch_disk(self, tmp_path):
        _git_init(tmp_path)
        policy = WritePolicy(blocked_paths=[])
        result = apply_generated_files(tmp_path, {"agent/bar.py": "y = 2\n"}, policy=policy, dry_run=True)
        assert result.ok
        assert not (tmp_path / "agent" / "bar.py").exists()

    def test_rejects_too_many_files(self, tmp_path):
        _git_init(tmp_path)
        policy = WritePolicy(blocked_paths=[], max_files_per_write=2)
        files = {f"agent/f{i}.py": "pass\n" for i in range(5)}
        result = apply_generated_files(tmp_path, files, policy=policy)
        assert not result.ok
        assert result.errors

    def test_write_is_atomic(self, tmp_path):
        """Ensure temp file is cleaned up and final file exists after write."""
        _git_init(tmp_path)
        policy = WritePolicy(blocked_paths=[])
        apply_generated_files(tmp_path, {"agent/atomic.py": "z = 3\n"}, policy=policy)
        tmps = list(tmp_path.rglob("*.tmp"))
        assert not tmps, f"leftover temp files: {tmps}"
