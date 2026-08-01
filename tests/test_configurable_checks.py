from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from agent.write_mode import _run_checks, run_write_mode
from agent.write_policy import CheckPolicy, WritePolicy, load_write_policy


def _git_init_clean(path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@kodex.local"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Kodex Test"], cwd=path, check=True)
    (path / "README.md").write_text("# test repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init", "-q"], cwd=path, check=True)


def test_write_policy_defaults_to_pytest_check() -> None:
    policy = WritePolicy()
    assert policy.checks.normalized_commands() == ["python -m pytest -x -q --tb=short"]


def test_write_policy_loads_check_commands_from_object(tmp_path: Path) -> None:
    config = tmp_path / "configs" / "kodex_write_policy.json"
    config.parent.mkdir()
    config.write_text(
        json.dumps(
            {
                "checks": {
                    "commands": ["python -m pytest", "ruff check ."],
                    "stop_on_failure": False,
                    "timeout_seconds": 7,
                }
            }
        ),
        encoding="utf-8",
    )

    policy = load_write_policy(tmp_path)

    assert policy.checks.commands == ["python -m pytest", "ruff check ."]
    assert policy.checks.stop_on_failure is False
    assert policy.checks.timeout_seconds == 7


def test_write_policy_loads_check_commands_from_list_shorthand(tmp_path: Path) -> None:
    config = tmp_path / "configs" / "kodex_write_policy.json"
    config.parent.mkdir()
    config.write_text(json.dumps({"checks": ["python -m pytest", "ruff check ."]}), encoding="utf-8")

    policy = load_write_policy(tmp_path)

    assert policy.checks.commands == ["python -m pytest", "ruff check ."]


def test_run_checks_executes_configured_commands_in_order(tmp_path: Path) -> None:
    policy = WritePolicy(
        checks=CheckPolicy(
            commands=[
                "python -c 'print(1)'",
                "python -c 'print(2)'",
            ]
        )
    )

    ok, output, details = _run_checks(tmp_path, policy)

    assert ok is True
    assert "1" in output
    assert "2" in output
    assert [detail["command"] for detail in details] == [
        "python -c 'print(1)'",
        "python -c 'print(2)'",
    ]
    assert all(detail["ok"] for detail in details)


def test_run_checks_stops_on_first_failure_by_default(tmp_path: Path) -> None:
    policy = WritePolicy(
        checks=CheckPolicy(
            commands=[
                "python -c 'import sys; sys.exit(3)'",
                "python -c 'print(should_not_run)'",
            ]
        )
    )

    ok, _output, details = _run_checks(tmp_path, policy)

    assert ok is False
    assert len(details) == 1
    assert details[0]["returncode"] == 3


def test_run_checks_can_continue_after_failure(tmp_path: Path) -> None:
    policy = WritePolicy(
        checks=CheckPolicy(
            commands=[
                "python -c 'import sys; sys.exit(3)'",
                "python -c 'print(2)'",
            ],
            stop_on_failure=False,
        )
    )

    ok, output, details = _run_checks(tmp_path, policy)

    assert ok is False
    assert len(details) == 2
    assert "2" in output


def test_write_mode_uses_configured_checks(tmp_path: Path) -> None:
    _git_init_clean(tmp_path)
    policy = WritePolicy(
        require_clean_worktree=False,
        require_task_branch=False,
        allow_direct_main=True,
        blocked_paths=[],
        checks=CheckPolicy(commands=["python -c 'print(12345)'"]),
    )

    with patch("agent.write_mode._current_branch", return_value="kodex/test"):
        data = run_write_mode(
            tmp_path,
            task="Implement MVP",
            provider="noop",
            policy=policy,
        )

    assert data["status"] == "ready_for_commit"
    assert data["checks_ok"] is True
    assert data["checks"][0]["command"] == "python -c 'print(12345)'"
    assert "12345" in data["checks"][0]["output"]


def test_write_mode_reports_configured_check_failure(tmp_path: Path) -> None:
    _git_init_clean(tmp_path)
    policy = WritePolicy(
        require_clean_worktree=False,
        require_task_branch=False,
        allow_direct_main=True,
        blocked_paths=[],
        repair_loop=type(WritePolicy().repair_loop)(enabled=False),
        checks=CheckPolicy(commands=["python -c 'import sys; sys.exit(9)'"]),
    )

    with patch("agent.write_mode._current_branch", return_value="kodex/test"):
        data = run_write_mode(
            tmp_path,
            task="Implement MVP",
            provider="noop",
            policy=policy,
        )

    assert data["status"] == "checks_failed"
    assert data["checks_ok"] is False
    assert data["checks"][0]["returncode"] == 9


def test_dry_run_apply_command_keeps_target_path(tmp_path: Path) -> None:
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

    assert data["next_commands"] == [
        f"kodex app-build 'Implement MVP' --path {str(tmp_path.resolve())!r} --apply"
    ]
