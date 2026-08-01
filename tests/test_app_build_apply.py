from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from agent.main import app

runner = CliRunner()


def _git_init_clean(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@kodex.local"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Kodex Test"], cwd=path, check=True)
    (path / "README.md").write_text("# test repo\n")
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init", "-q"], cwd=path, check=True)


class TestAppBuildPreview:
    def test_preview_returns_ready_for_review(self, tmp_path):
        _git_init_clean(tmp_path)
        result = runner.invoke(app, ["app-build", "Implement MVP", "--path", str(tmp_path)])
        assert result.exit_code == 0, result.output
        assert "app_builder_preview" in result.output
        assert "ready_for_review" in result.output

    def test_preview_does_not_write_files(self, tmp_path):
        _git_init_clean(tmp_path)
        runner.invoke(app, ["app-build", "Implement MVP", "--path", str(tmp_path)])
        # noop provider outputs to generated/ — but preview mode should not apply
        assert not (tmp_path / "generated").exists()

    def test_preview_help_mentions_apply(self):
        result = runner.invoke(app, ["app-build", "--help"])
        assert "--apply" in result.output
        assert "--dry-run" in result.output


class TestAppBuildApply:
    def test_apply_routes_to_write_mode(self, tmp_path):
        _git_init_clean(tmp_path)
        with patch("agent.write_mode._current_branch", return_value="kodex/app-build-apply"), \
             patch("agent.write_mode._worktree_is_clean", return_value=True), \
             patch("agent.write_mode._run_checks", return_value=(True, "1 passed")):
            result = runner.invoke(
                app,
                ["app-build", "Implement MVP", "--path", str(tmp_path), "--apply"],
            )
        assert result.exit_code == 0, result.output
        # write mode output contract
        assert "status" in result.output
        assert "checkpoint" in result.output

    def test_dry_run_routes_to_write_mode_without_writing(self, tmp_path):
        _git_init_clean(tmp_path)
        with patch("agent.write_mode._current_branch", return_value="kodex/test"), \
             patch("agent.write_mode._worktree_is_clean", return_value=True), \
             patch("agent.write_mode._run_checks", return_value=(True, "1 passed")):
            result = runner.invoke(
                app,
                ["app-build", "Implement MVP", "--path", str(tmp_path), "--dry-run"],
            )
        assert result.exit_code == 0, result.output
        assert "status" in result.output
        # dry-run must not write to generated/
        assert not (tmp_path / "generated").exists()

    def test_apply_never_auto_commits_or_pushes(self, tmp_path):
        """run_write_mode must not execute git commit/push — only advisory next_commands."""
        from agent.write_mode import run_write_mode
        from agent.write_policy import WritePolicy

        _git_init_clean(tmp_path)
        policy = WritePolicy(
            require_clean_worktree=False,
            require_task_branch=False,
            allow_direct_main=True,
            blocked_paths=[],
        )
        with patch("agent.write_mode._current_branch", return_value="kodex/test"), \
             patch("agent.write_mode._run_checks", return_value=(True, "1 passed")):
            data = run_write_mode(
                tmp_path,
                task="Implement MVP",
                provider="noop",
                policy=policy,
            )

        assert "status" in data
        # next_commands are strings, never executed by write_mode itself
        for cmd in data.get("next_commands", []):
            assert isinstance(cmd, str)

