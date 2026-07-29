from agent.orchestrator import orchestrate_task


def test_orchestrator_recommends_ship_when_ready(tmp_path):
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

    result = orchestrate_task("add smoke test", tmp_path)

    assert result["ready"] is True
    assert result["decision"] == "ready"
    assert result["next_action"] == "ship_with_branch"
    assert result["next_command"] == "kodex ship 'add smoke test' --branch"
    assert result["branch"] == "kodex/add-smoke-test"
    assert result["predicted_files"]


def test_orchestrator_blocks_dirty_repo(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / "README.md").write_text("# Dirty\n", encoding="utf-8")

    result = orchestrate_task("add smoke test", tmp_path)

    assert result["ready"] is False
    assert result["decision"] == "blocked"
    assert result["next_action"] == "resolve_blockers"
    assert result["next_command"] is None
    assert result["blockers"]
