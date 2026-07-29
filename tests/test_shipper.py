from pathlib import Path

from agent.shipper import ship_task


def _init_clean_python_repo(tmp_path: Path) -> None:
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "kodex@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Kodex"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='demo'\n\n[tool.pytest.ini_options]\ntestpaths=['tests']\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "README.md", "pyproject.toml"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True, text=True)


def _is_smoke_test_path(path: str) -> bool:
    candidate = Path(path)
    return (
        len(candidate.parts) == 2
        and candidate.parts[0] == "tests"
        and candidate.name.startswith("test_")
        and "_smoke" in candidate.stem
        and candidate.suffix == ".py"
    )


def test_ship_task_blocks_dirty_worktree(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / "README.md").write_text("# Dirty\n", encoding="utf-8")

    result = ship_task("add smoke test", tmp_path)

    assert result["ok"] is False
    assert result["status"] == "blocked_dirty_worktree"


def test_ship_task_prepares_commit_when_safe(tmp_path):
    _init_clean_python_repo(tmp_path)

    result = ship_task("add smoke test", tmp_path)

    assert result["ok"] is True
    assert result["status"] == "ready_for_commit"
    assert result["changed_files"]
    assert any(_is_smoke_test_path(path) for path in result["changed_files"])
    assert result["checks_ok"] is True
    assert result["diff_safe"] is True
    assert result["suggested_commit"] == "kodex: add smoke test"
    assert result["next_commands"]


def test_ship_task_can_prepare_branch_before_shipping(tmp_path):
    _init_clean_python_repo(tmp_path)

    result = ship_task("add smoke test", tmp_path, use_branch=True)

    assert result["ok"] is True
    assert result["status"] == "ready_for_commit"
    assert result["branch"]["ok"] is True
    assert result["branch"]["branch"] == "kodex/add-smoke-test"
    assert result["git"]["branch"] == "kodex/add-smoke-test"
    assert any(_is_smoke_test_path(path) for path in result["changed_files"])
    assert result["next_commands"][-1] == "git push -u origin kodex/add-smoke-test"
