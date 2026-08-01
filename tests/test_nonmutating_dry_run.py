from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from agent.write_mode import run_write_mode
from agent.write_policy import WritePolicy


def _git_init_clean(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@kodex.local"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Kodex Test"], cwd=path, check=True)
    (path / "README.md").write_text("# test repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init", "-q"], cwd=path, check=True)


def test_write_mode_dry_run_is_fully_non_mutating(tmp_path):
    _git_init_clean(tmp_path)
    policy = WritePolicy(
        require_clean_worktree=False,
        require_task_branch=False,
        allow_direct_main=True,
        blocked_paths=[],
    )

    with patch("agent.write_mode._current_branch", return_value="kodex/test"), \
         patch("agent.write_mode._run_checks") as run_checks:
        data = run_write_mode(
            tmp_path,
            task="Implement MVP",
            provider="noop",
            dry_run=True,
            policy=policy,
        )

    assert data["ok"] is True
    assert data["status"] == "dry_run_ready"
    assert data["dry_run"] is True
    assert data["checkpoint"] is None
    assert data["checkpoint_preview"]["would_create"] is True
    assert data["run_state_preview"]["would_persist"] is True
    assert data["written"] == []
    assert data["metadata_written"] == []
    assert data["checks_ok"] is None
    assert data["diff_safe"] is None

    run_checks.assert_not_called()
    assert not (tmp_path / ".kodex").exists()
    assert not (tmp_path / "generated").exists()
    assert not (tmp_path / ".pytest_cache").exists()


def test_write_mode_dry_run_suggests_apply_command(tmp_path):
    _git_init_clean(tmp_path)
    policy = WritePolicy(
        require_clean_worktree=False,
        require_task_branch=False,
        allow_direct_main=True,
        blocked_paths=[],
    )

    with patch("agent.write_mode._current_branch", return_value="kodex/test"):
        data = run_write_mode(
            tmp_path,
            task="Implement MVP",
            provider="noop",
            dry_run=True,
            policy=policy,
        )

    assert data["next_commands"] == ["kodex app-build 'Implement MVP' --apply"]
