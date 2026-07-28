from agent.executor import execute_task


def test_execute_task_dry_run(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    packet = execute_task("add smoke test", tmp_path, dry_run=True)

    assert packet["task"] == "add smoke test"
    assert packet["dry_run"] is True
    assert packet["project"]["name"] == tmp_path.name
    assert packet["model"]["mode"] == "dry-run"
    assert "checks" not in packet


def test_execute_task_apply_runs_checks_packet(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")

    packet = execute_task("inspect repo", tmp_path, dry_run=False)

    assert packet["dry_run"] is False
    assert "checks" in packet
    assert "diff" in packet
