from __future__ import annotations

from agent.task_planner import build_plan


def test_build_plan_suggests_branch_and_commit() -> None:
    project = {
        "name": "Kodex",
        "stack": ["python"],
        "entrypoints": ["agent/main.py"],
        "commands": {"test": "pytest"},
        "risks": ["no CI workflow detected yet"],
    }

    plan = build_plan("add smoke tests", project)

    assert plan["repo"] == "Kodex"
    assert plan["suggested_branch"].startswith("kodex/")
    assert plan["suggested_commit"].startswith("kodex:")
    assert "pytest" in plan["checks"]
    assert "no CI workflow detected yet" in plan["known_risks"]


def test_build_plan_handles_missing_checks() -> None:
    plan = build_plan("document setup", {"name": "empty"})

    assert plan["repo"] == "empty"
    assert plan["checks"] == ["No project checks detected; add a smoke test or run a manual sanity check."]
