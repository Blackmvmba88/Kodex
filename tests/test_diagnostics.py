from agent.diagnostics import diagnose_file, diagnose_text


def test_diagnose_text_detects_pytest_failure():
    log = """
FAILED tests/test_shipper.py::test_ship_task_prepares_commit_when_safe - assert False
================================ short test summary info =================================
"""

    result = diagnose_text(log)

    assert result["phase"] == "TEST"
    assert result["failed_file"] == "tests/test_shipper.py"
    assert "FAILED" in result["reason"]
    assert "test contract" in result["suggested_fix"]


def test_diagnose_text_detects_cli_failure():
    result = diagnose_text("No such command 'ship'.")

    assert result["phase"] == "CLI"
    assert result["failed_file"] is None
    assert "agent/main.py" in result["suggested_fix"]


def test_diagnose_file_handles_missing_file(tmp_path):
    result = diagnose_file(tmp_path / "missing.log")

    assert result["phase"] == "FILE"
    assert result["ok"] is False
    assert "does not exist" in result["reason"]
