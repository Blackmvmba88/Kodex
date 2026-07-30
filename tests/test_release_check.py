from agent.release_check import release_check


def _init_repo(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "kodex@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Kodex"], cwd=tmp_path, check=True)


def _write_release_ready_repo(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname='demo'\n\n[tool.pytest.ini_options]\ntestpaths=['tests']\n",
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_demo.py").write_text("def test_demo():\n    assert True\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "ARCHITECTURE.md").write_text("# Architecture\n", encoding="utf-8")
    (tmp_path / "docs" / "OPERATIONS.md").write_text("# Operations\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "verify.sh").write_text("#!/usr/bin/env bash\npytest\n", encoding="utf-8")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")
    (tmp_path / ".github" / "pull_request_template.md").write_text("# PR\n", encoding="utf-8")
    (tmp_path / ".github" / "ISSUE_TEMPLATE").mkdir()
    (tmp_path / ".github" / "ISSUE_TEMPLATE" / "bug_report.md").write_text("# Bug\n", encoding="utf-8")
    (tmp_path / ".github" / "ISSUE_TEMPLATE" / "feature_request.md").write_text("# Feature\n", encoding="utf-8")


def test_release_check_reports_ready_repo(tmp_path):
    import subprocess

    _init_repo(tmp_path)
    _write_release_ready_repo(tmp_path)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True, text=True)

    result = release_check(tmp_path)

    assert result["ready"] is True
    assert result["status"] == "release_ready"
    assert result["score"] == {"passed": 7, "total": 7}
    assert result["missing_files"] == []
    assert result["blockers"] == []


def test_release_check_reports_missing_infrastructure(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "README.md").write_text("# Minimal\n", encoding="utf-8")

    result = release_check(tmp_path)

    assert result["ready"] is False
    assert result["status"] == "needs_attention"
    assert "docs/ARCHITECTURE.md" in result["missing_files"]
    assert result["blockers"]
    assert result["next_actions"]
