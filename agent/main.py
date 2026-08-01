from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.json import JSON
from rich.table import Table

from agent.app_builder import build_app
from agent.autonomous import autonomous_run, resume_run
from agent.brancher import prepare_branch
from agent.checks import run_project_checks
from agent.cleaner import clean_repo
from agent.diagnostics import diagnose_file, diagnose_text
from agent.diff_guard import inspect_diff
from agent.executor import execute_task
from agent.git_ops import git_status
from agent.memory import find_project, load_projects, save_project
from agent.orchestrator import orchestrate_task
from agent.patcher import apply_patch, propose_patch
from agent.pr_summary import build_pr_summary
from agent.profession_router import route_profession_dict
from agent.release_check import release_check
from agent.repo_scanner import scan_repo
from agent.shipper import ship_task
from agent.snapshot import build_snapshot
from agent.task_planner import build_plan
from agent.virtualizer import virtualize_task

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


@app.command()
def checks(path: str = typer.Argument(".", help="Repository path"), timeout: int = 120) -> None:
    """Run detected project checks."""
    project = scan_repo(path)
    console.print(JSON.from_data(run_project_checks(project, timeout=timeout)))


@app.command("diff")
def diff_guard(path: str = typer.Argument(".", help="Repository path")) -> None:
    """Inspect current diff for risky changes."""
    console.print(JSON.from_data(inspect_diff(path)))


@app.command()
def run(
    description: str,
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    apply: bool = typer.Option(False, "--apply", help="Run checks and diff guard after planning"),
) -> None:
    """Prepare a safe execution packet for a task."""
    packet = execute_task(description, Path(path), dry_run=not apply)
    console.print(JSON.from_data(packet))


@app.command()
def patch(
    description: str,
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    apply: bool = typer.Option(False, "--apply", help="Write proposed files"),
    force: bool = typer.Option(False, "--force", help="Allow larger write plans while keeping hard path checks"),
) -> None:
    """Propose or apply a guarded file patch."""
    if apply:
        console.print(JSON.from_data(apply_patch(description, path, force=force)))
    else:
        console.print(JSON.from_data(propose_patch(description, path)))


@app.command()
def ship(
    description: str,
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    force: bool = typer.Option(False, "--force", help="Allow larger write plans while keeping hard path checks"),
    branch: bool = typer.Option(False, "--branch", help="Create/check out a safe task branch before shipping"),
) -> None:
    """Apply patch, run checks, inspect diff, and prepare commit instructions."""
    console.print(JSON.from_data(ship_task(description, path, force=force, use_branch=branch)))


@app.command()
def clean(
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    apply: bool = typer.Option(False, "--apply", help="Remove detected generated artifacts"),
) -> None:
    """Preview or remove generated local artifacts safely."""
    console.print(JSON.from_data(clean_repo(path, apply=apply)))


@app.command()
def snapshot(path: str = typer.Option(".", "--path", "-p", help="Repository path")) -> None:
    """Show a compact readiness snapshot for a repository."""
    console.print(JSON.from_data(build_snapshot(path)))


@app.command()
def branch(
    description: str,
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    no_checkout: bool = typer.Option(False, "--no-checkout", help="Create branch without checking it out"),
) -> None:
    """Create a safe task branch from a clean working tree."""
    console.print(JSON.from_data(prepare_branch(description, path, checkout=not no_checkout)))


@app.command()
def virtualize(
    description: str,
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    no_branch: bool = typer.Option(False, "--no-branch", help="Simulate shipping without a task branch"),
) -> None:
    """Simulate a task without writing files, creating branches, committing, or pushing."""
    console.print(JSON.from_data(virtualize_task(description, path, use_branch=not no_branch)))


@app.command()
def orchestrate(
    description: str,
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    no_branch: bool = typer.Option(False, "--no-branch", help="Plan without a task branch"),
) -> None:
    """Decide the safest next step for a task without mutating the repository."""
    console.print(JSON.from_data(orchestrate_task(description, path, use_branch=not no_branch)))


@app.command()
def diagnose(
    log: Optional[str] = typer.Argument(None, help="Raw log text or path to a log file"),
    file: bool = typer.Option(False, "--file", help="Treat the argument as a path to a log file"),
) -> None:
    """Classify terminal/test/git output into a readable failure diagnosis."""
    if log is None:
        console.print(JSON.from_data(diagnose_text("")))
    elif file:
        console.print(JSON.from_data(diagnose_file(log)))
    else:
        console.print(JSON.from_data(diagnose_text(log)))


@app.command("pr-summary")
def pr_summary(
    title: str,
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    test_log: Optional[str] = typer.Option(None, "--test-log", help="Optional inline test/check output"),
    test_log_file: Optional[str] = typer.Option(None, "--test-log-file", help="Optional path to test/check output"),
    summary: Optional[str] = typer.Option(None, "--summary", help="Optional human summary override"),
) -> None:
    """Generate a structured pull request summary from repo state."""
    log_text = test_log
    if test_log_file:
        log_text = Path(test_log_file).expanduser().read_text(encoding="utf-8")
    console.print(JSON.from_data(build_pr_summary(title, path, test_output=log_text, extra_summary=summary)))


@app.command("release-check")
def release_check_command(path: str = typer.Option(".", "--path", "-p", help="Repository path")) -> None:
    """Evaluate whether the repository has release-ready infrastructure."""
    console.print(JSON.from_data(release_check(path)))


@app.command("profession")
def profession(
    request: str = typer.Argument(..., help="Human request to route into a profession-aware lane"),
    path: str = typer.Option(".", "--path", "-p", help="Repository path containing profession templates"),
) -> None:
    """Route a human request into profession, input mode, and output contract."""
    console.print(JSON.from_data(route_profession_dict(request, path)))


@app.command("app-build")
def app_build(
    task: str = typer.Argument("Implement MVP", help="Product/task goal to build from specs"),
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    provider: str = typer.Option("noop", "--provider", help="Model provider name"),
    source: list[str] = typer.Option(None, "--source", help="Spec source file; can be passed multiple times"),
    max_repair_attempts: int = typer.Option(0, "--max-repair-attempts", help="Repair attempts reserved for future execution mode"),
    apply: bool = typer.Option(False, "--apply", help="Run the full guarded write pipeline (checkpoint → apply → checks)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate and checkpoint without writing files (implies --apply path)"),
) -> None:
    """Preview or apply the README/SPEC-driven app-building pipeline.

    Without --apply: compiles spec, builds context, calls provider, validates
    write plan, and returns a preview — no files are written.

    With --apply: runs the full guarded write pipeline including checkpoint
    creation, atomic file application, check execution, optional repair loop,
    and stops at ready_for_commit. Never auto-commits or pushes.
    """
    if apply or dry_run:
        from agent.write_mode import run_write_mode
        console.print(
            JSON.from_data(
                run_write_mode(
                    path,
                    task=task,
                    provider=provider,
                    sources=source or None,
                    dry_run=dry_run,
                )
            )
        )
    else:
        console.print(
            JSON.from_data(
                build_app(
                    path,
                    sources=source or None,
                    task=task,
                    provider=provider,
                    max_repair_attempts=max_repair_attempts,
                )
            )
        )


@app.command("auto")
def auto_run(
    description: str,
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    apply: bool = typer.Option(False, "--apply", help="Execute the guarded local ship phase"),
    force: bool = typer.Option(False, "--force", help="Allow larger write plans while keeping hard path checks"),
    no_branch: bool = typer.Option(False, "--no-branch", help="Run without a task branch"),
) -> None:
    """Run the persisted autonomous loop through the safe local boundary."""
    console.print(
        JSON.from_data(
            autonomous_run(description, path, apply=apply, force=force, use_branch=not no_branch)
        )
    )


@app.command("resume")
def resume(
    run_id: str,
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
) -> None:
    """Inspect a persisted run and determine the safest recovery action."""
    console.print(JSON.from_data(resume_run(run_id, path)))


if __name__ == "__main__":
    app()
