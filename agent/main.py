from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.json import JSON
from rich.table import Table

from agent.git_ops import git_status
from agent.memory import find_project, load_projects, save_project
from agent.repo_scanner import scan_repo
from agent.task_planner import build_plan

app = typer.Typer(help="Kodex — BlackMamba Dev Agent")
console = Console()


@app.command()
def scan(path: str = typer.Argument(".", help="Repository path to scan"), save: bool = True) -> None:
    """Scan a repository and optionally save it to memory."""
    project = scan_repo(path)
    console.print(JSON.from_data(project))

    if save:
        save_project(project)
        console.print(f"[green]Saved project memory:[/green] {project['name']}")


@app.command("map")
def show_map() -> None:
    """Show scanned project memory."""
    projects = load_projects()
    if not projects:
        console.print("[yellow]No projects scanned yet.[/yellow]")
        raise typer.Exit(0)

    table = Table(title="Kodex Project Map")
    table.add_column("Project")
    table.add_column("Stack")
    table.add_column("Entrypoints")
    table.add_column("Risks")

    for project in projects:
        table.add_row(
            project.get("name", "unknown"),
            ", ".join(project.get("stack", [])) or "unknown",
            ", ".join(project.get("entrypoints", [])) or "none",
            ", ".join(project.get("risks", [])) or "none",
        )

    console.print(table)


@app.command()
def status(path: str = typer.Argument(".", help="Repository path")) -> None:
    """Show safe git status summary."""
    console.print(JSON.from_data(git_status(path)))


@app.command()
def task(description: str, repo: Optional[str] = None) -> None:
    """Create a safe implementation plan for a task."""
    project = find_project(repo) if repo else None
    plan = build_plan(description, project)
    console.print(JSON.from_data(plan))


@app.command()
def doctor(path: str = typer.Argument(".", help="Repository path")) -> None:
    """Scan repo and combine project map with git state."""
    project = scan_repo(path)
    state = git_status(path)
    console.print(JSON.from_data({"project": project, "git": state}))


if __name__ == "__main__":
    app()
