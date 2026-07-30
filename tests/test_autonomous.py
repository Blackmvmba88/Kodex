import subprocess

from agent.autonomous import autonomous_run, resume_run
from agent.git_ops import git_status


def _init_repo(tmp_path):
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


def test_git_status_ignores_internal_runtime_state(tmp_path):
    _init_repo(tmp_path)
    run_dir = tmp_path / ".kodex" / "runs"
    run_dir.mkdir(parents=True)
    (run_dir / "run-test.json").write_text("{}\n", encoding="utf-8")

    status = git_status(tmp_path)

    assert status["dirty"] is False
    assert status["changed_files"] == []


def test_git_status_keeps_real_changes_visible(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "README.md").write_text("# Changed\n", encoding="utf-8")

    status = git_status(tmp_path)

    assert status["dirty"] is True
    assert any("README.md" in entry for entry in status["changed_files"])


def test_autonomous_run_persists_planned_state(tmp_path):
    _init_repo(tmp_path)

    result = autonomous_run("add smoke test", tmp_path)

    assert result["orchestration"]["ready"] is True
    assert result["ship"] is None
    assert result["run"]["phase"] == "planned"
    assert result["run"]["status"] == "paused"
    run_id = result["run"]["run_id"]
    assert (tmp_path / ".kodex" / "runs" / f"{run_id}.json").exists()


def test_resume_planned_run_requests_review(tmp_path):
    _init_repo(tmp_path)
    result = autonomous_run("add smoke test", tmp_path)

    resumed = resume_run(result["run"]["run_id"], tmp_path)

    assert resumed["next_action"] == "review"
    assert resumed["run"]["phase"] == "planned"


def test_autonomous_run_persists_blocked_state(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / "README.md").write_text("# Dirty\n", encoding="utf-8")

    result = autonomous_run("add smoke test", tmp_path)

    assert result["orchestration"]["decision"] == "blocked"
    assert result["run"]["phase"] == "blocked"
    assert result["run"]["status"] == "blocked"
