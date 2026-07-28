from agent.checks import run_command, run_project_checks


def test_run_command_success(tmp_path):
    result = run_command("python -c 'print(123)'", tmp_path)

    assert result["ok"] is True
    assert "123" in result["stdout"]


def test_run_project_checks_none(tmp_path):
    project = {"name": "demo", "path": str(tmp_path), "commands": {}}

    checks = run_project_checks(project)

    assert checks[0]["name"] == "none"
    assert checks[0]["ok"] is False
