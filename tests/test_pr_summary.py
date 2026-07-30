from agent.pr_summary import build_pr_summary


def test_build_pr_summary_includes_sections(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "kodex@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Kodex"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / "README.md").write_text("# Demo\n\nUpdated\n", encoding="utf-8")

    summary = build_pr_summary("Update README", tmp_path, test_output="1 passed")

    assert summary["title"] == "Update README"
    assert summary["changed_files"] == ["README.md"]
    assert summary["tests_status"] == "passed"
    assert "## Summary" in summary["body"]
    assert "## Changed files" in summary["body"]
    assert "README.md" in summary["body"]
    assert "Human approval checklist" in summary["body"]


def test_build_pr_summary_marks_failed_test_log(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / "README.md").write_text("# Dirty\n", encoding="utf-8")

    summary = build_pr_summary(
        "Broken change",
        tmp_path,
        test_output="FAILED tests/test_demo.py::test_demo - assert False",
    )

    assert summary["tests_status"] == "needs_review"
    assert summary["risk_level"] == "medium"
    assert summary["diagnosis"]["phase"] == "TEST"
    assert "tests/test_demo.py" in summary["body"]
