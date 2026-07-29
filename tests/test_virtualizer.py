from agent.virtualizer import virtualize_task


def test_virtualize_task_predicts_safe_branch_ship(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "kodex@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Kodex"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='demo'\n\n[tool.pytest.ini_options]\ntestpaths=['tests']\n",
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_demo.py").write_text("def test_demo():\n    assert True\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True, text=True)

    result = virtualize_task("add smoke test", tmp_path)

    assert result["mode"] == "virtualized"
    assert result["ready"] is True
    assert result["status"] == "ready_to_ship"
    assert result["branch"] == "kodex/add-smoke-test"
    assert result["predicted_files"]
    assert result["checks"] == ["pytest"]
    assert result["blockers"] == []
    assert result["next_command"] == "kodex ship 'add smoke test' --branch"


def test_virtualize_task_blocks_dirty_repo(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / "README.md").write_text("# Dirty\n", encoding="utf-8")

    result = virtualize_task("add smoke test", tmp_path)

    assert result["ready"] is False
    assert result["status"] == "needs_attention"
    assert "working tree has existing changes" in result["blockers"]
    assert result["next_command"] is None
