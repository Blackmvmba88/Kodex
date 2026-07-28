from agent.snapshot import build_snapshot


def test_build_snapshot_reports_ready_repo(tmp_path):
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

    snapshot = build_snapshot(tmp_path)

    assert snapshot["project"] == tmp_path.name
    assert snapshot["git"]["is_git_repo"] is True
    assert snapshot["git"]["dirty"] is False
    assert snapshot["diff"]["safe"] is True
    assert snapshot["ready"] is True
    assert snapshot["status"] == "ready"


def test_build_snapshot_reports_dirty_repo(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / "README.md").write_text("# Dirty\n", encoding="utf-8")

    snapshot = build_snapshot(tmp_path)

    assert snapshot["git"]["dirty"] is True
    assert snapshot["ready"] is False
    assert snapshot["status"] == "needs_attention"
