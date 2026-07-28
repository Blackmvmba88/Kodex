from agent.shipper import ship_task


def test_ship_task_blocks_dirty_worktree(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / "README.md").write_text("# Dirty\n", encoding="utf-8")

    result = ship_task("add smoke test", tmp_path)

    assert result["ok"] is False
    assert result["status"] == "blocked_dirty_worktree"


def test_ship_task_prepares_commit_when_safe(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "kodex@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Kodex"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True, text=True)

    result = ship_task("add smoke test", tmp_path)

    assert result["ok"] is True
    assert result["status"] == "ready_for_commit"
    assert "tests/test_kodex_smoke.py" in result["changed_files"]
    assert result["checks_ok"] is True
    assert result["diff_safe"] is True
    assert result["suggested_commit"] == "kodex: add smoke test"
    assert result["next_commands"]
