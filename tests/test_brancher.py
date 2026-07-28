from agent.brancher import prepare_branch


def _init_repo(path):
    import subprocess

    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "kodex@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Kodex"], cwd=path, check=True)
    (path / "README.md").write_text("# Demo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=path, check=True, capture_output=True, text=True)


def test_prepare_branch_creates_branch_from_clean_repo(tmp_path):
    _init_repo(tmp_path)

    result = prepare_branch("add feature", tmp_path)

    assert result["ok"] is True
    assert result["branch"] == "kodex/add-feature"
    assert result["status"] == "created_and_checked_out_branch"
    assert result["git"]["branch"] == "kodex/add-feature"
    assert result["next_commands"] == ["git push -u origin kodex/add-feature"]


def test_prepare_branch_blocks_dirty_repo(tmp_path):
    _init_repo(tmp_path)
    (tmp_path / "dirty.txt").write_text("dirty\n", encoding="utf-8")

    result = prepare_branch("add feature", tmp_path)

    assert result["ok"] is False
    assert result["status"] == "blocked_dirty_worktree"
