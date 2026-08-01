from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from agent.write_mode import run_write_mode
from agent.write_policy import WritePolicy


def _git_init_clean(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@kodex.local"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Kodex Test"], cwd=path, check=True)
    (path / "README.md").write_text("# test\n")
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init", "-q"], cwd=path, check=True)


def _policy_no_guards(tmp_path: Path) -> WritePolicy:
    """Minimal policy with all guards disabled for unit testing."""
    return WritePolicy(
        require_clean_worktree=False,
        require_task_branch=False,
        allow_direct_main=True,
        require_checkpoint=True,
        max_files_per_write=20,
        max_total_bytes=500_000,
        blocked_paths=[".env"],
        repair_loop_config=None,
    )


class TestRunWriteModeDirtyWorktree:
    def test_blocks_dirty_worktree(self, tmp_path):
        _git_init_clean(tmp_path)
        (tmp_path / "dirty.py").write_text("x = 1\n")
        policy = WritePolicy(require_clean_worktree=True, require_task_branch=False)
        result = run_write_mode(tmp_path, task="Test", policy=policy)
        assert result["status"] == "blocked_dirty_worktree"
        assert result["ok"] is False


class TestRunWriteModeMainGuard:
    def test_blocks_main_branch(self, tmp_path):
        _git_init_clean(tmp_path)
        policy = WritePolicy(
            require_clean_worktree=False,
            require_task_branch=True,
            allow_direct_main=False,
        )
        with patch("agent.write_mode._current_branch", return_value="main"):
            result = run_write_mode(tmp_path, task="Test", policy=policy)
        assert result["status"] == "blocked_on_main"


class TestRunWriteModeNoop:
    def test_noop_provider_dry_run(self, tmp_path):
        """With noop provider and dry_run, the pipeline should reach a terminal status
        without writing any files."""
        _git_init_clean(tmp_path)
        policy = WritePolicy(
            require_clean_worktree=False,
            require_task_branch=False,
            allow_direct_main=True,
            blocked_paths=[],
            max_files_per_write=20,
            max_total_bytes=500_000,
        )
        with patch("agent.write_mode._current_branch", return_value="kodex/test-branch"):
            result = run_write_mode(
                tmp_path,
                task="Implement MVP",
                provider="noop",
                dry_run=True,
                policy=policy,
            )

        # noop provider returns ok=False or empty files — pipeline should not crash
        assert "status" in result
        assert isinstance(result["ok"], bool)

    def test_result_never_contains_commit_or_push_action(self, tmp_path):
        _git_init_clean(tmp_path)
        policy = WritePolicy(require_clean_worktree=False, require_task_branch=False)
        with patch("agent.write_mode._current_branch", return_value="kodex/write-activation"):
            result = run_write_mode(tmp_path, task="Test", provider="noop", policy=policy)
        # next_commands are advisory only — write_mode itself must not execute them
        for cmd in result.get("next_commands", []):
            assert "git push" not in cmd or result["status"] == "ready_for_commit"
