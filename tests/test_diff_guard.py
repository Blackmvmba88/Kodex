from agent.diff_guard import inspect_diff


def test_inspect_diff_without_git_repo_does_not_crash(tmp_path):
    result = inspect_diff(tmp_path)

    assert result["path"] == str(tmp_path.resolve())
    assert "warnings" in result
    assert "safe" in result
