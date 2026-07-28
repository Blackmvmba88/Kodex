from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.json import JSON
from rich.table import Table

from agent.memory import load_projects, save_project
from agent.repo_scanner import scan_repo

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
def task(description: str, repo: Optional[str] = None) -> None:
    """Create a safe implementation plan for a task."""
    console.print("[bold]Task:[/bold]", description)
    if repo:
        console.print("[bold]Repo:[/bold]", repo)

    console.print("\n[bold]Plan[/bold]")
    steps = [
        "Inspect repository map and current git status.",
        "Identify files likely affected by the task.",
        "Make the smallest safe change.",
        "Run available tests/checks.",
        "Summarize diff and risks.",
        "Prepare commit/PR text only after review.",
    ]
    for index, step in enumerate(steps, start=1):
        console.print(f"{index}. {step}")


if __name__ == "__main__":
    app()
