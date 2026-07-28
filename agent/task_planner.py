from __future__ import annotations

from typing import Any

from agent.git_ops import commit_message, suggest_branch_name


def infer_likely_files(project: dict[str, Any], task: str) -> list[str]:
    task_lower = task.lower()
    likely: list[str] = []

    if "readme" in task_lower or "doc" in task_lower:
        likely.extend(["README.md", "docs/"])

    if "test" in task_lower or "pytest" in task_lower or "smoke" in task_lower:
        likely.extend(project.get("tests", []))
        if "python" in project.get("stack", []):
            likely.append("tests/")

    if "cli" in task_lower or "command" in task_lower:
        likely.extend(project.get("entrypoints", []))
        likely.append("agent/main.py")

    if "github" in task_lower or "ci" in task_lower or "workflow" in task_lower:
        likely.append(".github/workflows/")

    for entrypoint in project.get("entrypoints", []):
        if entrypoint not in likely:
            likely.append(entrypoint)

    return list(dict.fromkeys(likely))


def build_plan(task: str, project: dict[str, Any] | None = None) -> dict[str, Any]:
    project = project or {}
    risks = list(project.get("risks", []))

    steps = [
        "Inspect current git status before editing.",
        "Read the project map and local conventions.",
        "Identify the smallest file set required for the task.",
        "Implement the smallest safe change.",
        "Run available tests/checks.",
        "Review diff for accidental changes or secrets.",
        "Prepare commit and PR summary.",
    ]

    checks = []
    commands = project.get("commands", {})
    for key in ["lint", "test", "build"]:
        if key in commands:
            checks.append(commands[key])

    if not checks:
        checks.append("No project checks detected; add a smoke test or run a manual sanity check.")

    return {
        "task": task,
        "repo": project.get("name"),
        "suggested_branch": suggest_branch_name(task),
        "suggested_commit": commit_message(task),
        "likely_files": infer_likely_files(project, task),
        "steps": steps,
        "checks": checks,
        "known_risks": risks,
    }
