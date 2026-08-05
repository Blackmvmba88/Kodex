from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from agent.app_builder import build_app
from agent.autonomous import autonomous_run, resume_run
from agent.brancher import prepare_branch
from agent.checks import run_project_checks
from agent.cleaner import clean_repo
from agent.course import build_course_module
from agent.demo import available_demos, build_demo_packet
from agent.diagnostics import diagnose_file, diagnose_text
from agent.diff_guard import inspect_diff
from agent.executor import execute_task
from agent.git_ops import git_status
from agent.guide import build_guide
from agent.lab import build_lab_packet
from agent.memory import find_project, load_projects, save_project
from agent.modes import build_modes_catalog
from agent.orchestrator import orchestrate_task
from agent.patcher import apply_patch, propose_patch
from agent.portfolio import build_portfolio_packet
from agent.pr_summary import build_pr_summary
from agent.profession_router import route_profession_dict
from agent.release_check import release_check
from agent.repo_scanner import scan_repo
from agent.review_gate import build_review_gate
from agent.shipper import ship_task
from agent.showcase import build_showcase_kit
from agent.snapshot import build_snapshot
from agent.task_planner import build_plan
from agent.virtualizer import virtualize_task

app = typer.Typer(help="Kodex — BlackMamba Dev Agent")
console = Console()


def _print_demo_human(packet: dict) -> None:
    """Render a premium, non-JSON demo view for first-touch users."""
    route = packet["route"]

    title = Text("KODEX", style="bold green")
    title.append("  BlackMamba local-first builder agent", style="dim")
    console.print(
        Panel(
            title,
            subtitle="no mutation · no provider calls · no repo writes",
            border_style="green",
        )
    )

    summary = Table(show_header=False, box=None, padding=(0, 2))
    summary.add_column("Key", style="bold cyan")
    summary.add_column("Value")
    summary.add_row("Request", packet["request"])
    summary.add_row("Profession", f"{route['profession_name']} ({route['profession']})")
    summary.add_row("Input Mode", route["input_mode"])
    summary.add_row("Output", route["output_contract"])
    summary.add_row("Mutation", packet["mutation"])
    summary.add_row("Confidence", str(route["confidence"]))
    console.print(Panel(summary, title="Intent Route", border_style="cyan"))

    flow = Table(title="Flow", show_header=True)
    flow.add_column("Step", style="bold")
    flow.add_column("Status", style="green")
    flow.add_column("Meaning")
    for item in packet["flow"]:
        flow.add_row(item["step"], item["status"], item["meaning"])
    console.print(flow)

    commands = "\n".join(f"  {command}" for command in packet["commands"])
    console.print(Panel(commands, title="Try Next", border_style="magenta"))

    promise = " · ".join(packet["promise"])
    console.print(Panel(promise, title="Product Promise", border_style="green"))


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


@app.command("modes")
def modes(json_output: bool = typer.Option(False, "--json", help="Render raw JSON capability catalog")) -> None:
    """Show Kodex input modes, profession lanes, and BlackMamba University labs."""
    catalog = build_modes_catalog()
    if json_output:
        console.print(JSON.from_data(catalog))
        return

    console.print(f"[bold green]{catalog['product']}[/bold green] [dim]{catalog['tagline']}[/dim]")

    for title, key in (
        ("Input Modes", "input_modes"),
        ("Profession Lanes", "profession_lanes"),
        ("BlackMamba University Labs", "blackmamba_university_labs"),
    ):
        table = Table(title=title)
        table.add_column("Name", style="bold cyan")
        table.add_column("Purpose")
        table.add_column("Example", style="green")
        table.add_column("Safe Boundary", style="magenta")
        for item in catalog[key]:
            table.add_row(item["name"], item["purpose"], item["example"], item["safe_boundary"])
        console.print(table)

    console.print("[bold]Try next:[/bold]")
    for command in catalog["try_next"]:
        console.print(f"  [green]{command}[/green]")


@app.command("guide")
def guide(
    request: str = typer.Argument(..., help="Human request to guide through Kodex"),
    path: str = typer.Option(".", "--path", "-p", help="Repository path containing profession templates"),
    json_output: bool = typer.Option(False, "--json", help="Render raw JSON guide packet"),
) -> None:
    """Guide a human request into the safest next Kodex commands."""
    packet = build_guide(request, repo_root=path)
    if json_output:
        console.print(JSON.from_data(packet))
        return

    route = packet["route"]
    console.print(f"[bold green]KODEX GUIDE[/bold green] [dim]{packet['mutation_policy']}[/dim]")
    console.print(f"[bold cyan]Request:[/bold cyan] {packet['request']}")
    console.print(f"[bold cyan]Lane:[/bold cyan] {route['profession_name']} / {route['input_mode']} → {route['output_contract']}")
    console.print(f"[bold cyan]Mode note:[/bold cyan] {packet['mode_note']}")

    table = Table(title="Recommended Path")
    table.add_column("Step", style="bold cyan")
    table.add_column("Command", style="green")
    table.add_column("Purpose")
    table.add_column("Mutation", style="magenta")
    for step in packet["recommended_steps"]:
        table.add_row(step["title"], step["command"], step["purpose"], step["mutation"])
    console.print(table)

    if packet["blackmamba_university_modules"]:
        console.print("[bold]BlackMamba University:[/bold]")
        for module in packet["blackmamba_university_modules"]:
            console.print(f"  [cyan]{module}[/cyan]")

    if packet["safety_notes"]:
        console.print("[bold yellow]Safety notes:[/bold yellow]")
        for note in packet["safety_notes"]:
            console.print(f"  [yellow]{note}[/yellow]")


@app.command("lab")
def lab(
    request: str = typer.Argument(..., help="Human request to turn into a BlackMamba University lab"),
    path: str = typer.Option(".", "--path", "-p", help="Repository path containing profession templates"),
    json_output: bool = typer.Option(False, "--json", help="Render raw JSON lab packet"),
) -> None:
    """Turn a request into a non-mutating BlackMamba University lab packet."""
    packet = build_lab_packet(request, repo_root=path)
    if json_output:
        console.print(JSON.from_data(packet))
        return

    route = packet["route"]
    console.print(f"[bold green]{packet['title']}[/bold green]")
    console.print(f"[bold cyan]Request:[/bold cyan] {packet['request']}")
    console.print(f"[bold cyan]Lane:[/bold cyan] {route['profession_name']} / {route['input_mode']} → {route['output_contract']}")
    console.print(f"[bold cyan]Mutation policy:[/bold cyan] {packet['mutation_policy']}")

    for section in packet["sections"]:
        table = Table(title=section["title"])
        table.add_column("Item", style="green")
        for item in section["items"]:
            table.add_row(item)
        console.print(table)

    if packet["blackmamba_university_modules"]:
        console.print("[bold]BlackMamba University modules:[/bold]")
        for module in packet["blackmamba_university_modules"]:
            console.print(f"  [cyan]{module}[/cyan]")

    if packet["safety_notes"]:
        console.print("[bold yellow]Safety notes:[/bold yellow]")
        for note in packet["safety_notes"]:
            console.print(f"  [yellow]{note}[/yellow]")

    console.print("[bold]Try next:[/bold]")
    for command in packet["next_commands"]:
        console.print(f"  [green]{command}[/green]")


@app.command("course")
def course(
    request: str = typer.Argument(..., help="Human request to turn into a BlackMamba University course"),
    path: str = typer.Option(".", "--path", "-p", help="Repository path containing profession templates"),
    json_output: bool = typer.Option(False, "--json", help="Render raw JSON course module"),
) -> None:
    """Turn a request into a non-mutating BlackMamba University course module."""
    module = build_course_module(request, repo_root=path)
    if json_output:
        console.print(JSON.from_data(module))
        return

    console.print(f"[bold green]{module['title']}[/bold green]")
    console.print(f"[bold cyan]Request:[/bold cyan] {module['request']}")
    console.print(f"[bold cyan]Lane:[/bold cyan] {module['lane']} / {module['input_mode']} → {module['output_contract']}")
    console.print(f"[bold cyan]Goal:[/bold cyan] {module['course_goal']}")
    console.print(f"[bold cyan]Mutation:[/bold cyan] {module['mutation']}")

    lessons = Table(title="Lessons")
    lessons.add_column("Lesson", style="bold cyan")
    lessons.add_column("Focus")
    lessons.add_column("Exercise", style="green")
    lessons.add_column("Artifact", style="magenta")
    for lesson in module["lessons"]:
        lessons.add_row(lesson["title"], lesson["focus"], lesson["exercise"], lesson["artifact"])
    console.print(lessons)

    console.print(f"[bold]Capstone:[/bold] {module['capstone_project']}")
    console.print(f"[bold]Portfolio artifact:[/bold] {module['portfolio_artifact']}")

    assessment = Table(title="Assessment")
    assessment.add_column("Criterion", style="green")
    for item in module["assessment"]:
        assessment.add_row(item)
    console.print(assessment)

    if module["safety_boundary"]:
        console.print("[bold yellow]Safety boundary:[/bold yellow]")
        for note in module["safety_boundary"]:
            console.print(f"  [yellow]{note}[/yellow]")

    console.print("[bold]Try next:[/bold]")
    for command in module["next_commands"]:
        console.print(f"  [green]{command}[/green]")


@app.command("portfolio")
def portfolio(
    request: str = typer.Argument(..., help="Human request to turn into a portfolio evidence packet"),
    path: str = typer.Option(".", "--path", "-p", help="Repository path containing profession templates"),
    json_output: bool = typer.Option(False, "--json", help="Render raw JSON portfolio packet"),
) -> None:
    """Turn a request into a non-mutating BlackMamba University portfolio packet."""
    packet = build_portfolio_packet(request, repo_root=path)
    if json_output:
        console.print(JSON.from_data(packet))
        return

    console.print(f"[bold green]{packet['title']}[/bold green]")
    console.print(f"[bold cyan]Request:[/bold cyan] {packet['request']}")
    console.print(f"[bold cyan]Lane:[/bold cyan] {packet['lane']} / {packet['input_mode']} → {packet['output_contract']}")
    console.print(f"[bold cyan]Artifact:[/bold cyan] {packet['artifact_name']}")
    console.print(f"[bold cyan]Pitch:[/bold cyan] {packet['elevator_pitch']}")
    console.print(f"[bold cyan]Mutation:[/bold cyan] {packet['mutation']}")

    for title, key in (
        ("README Outline", "readme_outline"),
        ("Demo Script", "demo_script"),
        ("Evidence Checklist", "evidence_checklist"),
        ("Publish Boundary", "publish_boundary"),
        ("Safety Boundary", "safety_boundary"),
    ):
        table = Table(title=title)
        table.add_column("Item", style="green")
        for item in packet[key]:
            table.add_row(item)
        console.print(table)

    for section in packet["sections"]:
        table = Table(title=section["title"])
        table.add_column("Item", style="cyan")
        for item in section["items"]:
            table.add_row(item)
        console.print(table)

    console.print("[bold]Try next:[/bold]")
    for command in packet["next_commands"]:
        console.print(f"  [green]{command}[/green]")


@app.command("showcase")
def showcase(
    request: str = typer.Argument(..., help="Human request to turn into a safe showcase kit"),
    path: str = typer.Option(".", "--path", "-p", help="Repository path containing profession templates"),
    json_output: bool = typer.Option(False, "--json", help="Render raw JSON showcase kit"),
) -> None:
    """Turn a request into a non-mutating BlackMamba showcase kit."""
    kit = build_showcase_kit(request, repo_root=path)
    if json_output:
        console.print(JSON.from_data(kit))
        return

    console.print(f"[bold green]{kit['title']}[/bold green]")
    console.print(f"[bold cyan]Request:[/bold cyan] {kit['request']}")
    console.print(f"[bold cyan]Lane:[/bold cyan] {kit['lane']} / {kit['input_mode']} → {kit['output_contract']}")
    console.print(f"[bold cyan]Artifact:[/bold cyan] {kit['artifact_name']}")
    console.print(f"[bold cyan]Summary:[/bold cyan] {kit['public_summary']}")
    console.print(f"[bold cyan]Mutation:[/bold cyan] {kit['mutation']}")

    for title, key in (
        ("Private Review Notes", "private_review_notes"),
        ("Demo Talking Points", "demo_talking_points"),
        ("Proof Checklist", "proof_checklist"),
        ("Publish Safety Gate", "publish_safety_gate"),
        ("Safety Boundary", "safety_boundary"),
    ):
        table = Table(title=title)
        table.add_column("Item", style="green")
        for item in kit[key]:
            table.add_row(item)
        console.print(table)

    variants = Table(title="Audience Variants")
    variants.add_column("Audience", style="bold cyan")
    variants.add_column("Angle")
    variants.add_column("Opening", style="green")
    for variant in kit["audience_variants"]:
        variants.add_row(variant["audience"], variant["angle"], variant["opening_line"])
    console.print(variants)

    console.print("[bold]Try next:[/bold]")
    for command in kit["next_commands"]:
        console.print(f"  [green]{command}[/green]")


@app.command("review-gate")
def review_gate(
    request: str = typer.Argument(..., help="Human request to evaluate through the showcase review gate"),
    path: str = typer.Option(".", "--path", "-p", help="Repository path containing profession templates"),
    json_output: bool = typer.Option(False, "--json", help="Render raw JSON review gate packet"),
) -> None:
    """Evaluate whether a showcase packet is ready to demo or needs more evidence."""
    gate = build_review_gate(request, repo_root=path)
    if json_output:
        console.print(JSON.from_data(gate))
        return

    console.print(f"[bold green]{gate['title']}[/bold green]")
    console.print(f"[bold cyan]Request:[/bold cyan] {gate['request']}")
    console.print(f"[bold cyan]Lane:[/bold cyan] {gate['lane']}")
    console.print(f"[bold cyan]Readiness:[/bold cyan] {gate['readiness_score']}")
    console.print(f"[bold cyan]Decision:[/bold cyan] {gate['decision']}")
    console.print(f"[bold cyan]Mutation:[/bold cyan] {gate['mutation']}")

    checks = Table(title="Review Checks")
    checks.add_column("Check", style="bold cyan")
    checks.add_column("Status", style="green")
    checks.add_column("Weight", style="magenta")
    checks.add_column("Reason")
    for check in gate["checks"]:
        checks.add_row(check["name"], check["status"], str(check["weight"]), check["reason"])
    console.print(checks)

    for title, key in (
        ("Missing Evidence", "missing_evidence"),
        ("Risk Flags", "risk_flags"),
        ("Recommended Actions", "recommended_actions"),
        ("Safety Boundary", "safety_boundary"),
    ):
        table = Table(title=title)
        table.add_column("Item", style="yellow" if key == "risk_flags" else "green")
        for item in gate[key]:
            table.add_row(item)
        console.print(table)


@app.command("profession")
def profession(
    request: str = typer.Argument(..., help="Human request to route into a profession-aware lane"),
    path: str = typer.Option(".", "--path", "-p", help="Repository path containing profession templates"),
) -> None:
    """Route a human request into profession, input mode, and output contract."""
    console.print(JSON.from_data(route_profession_dict(request, path)))


@app.command("demo")
def demo(
    name: str = typer.Option("sine", "--name", "-n", help="Bundled demo name"),
    request: Optional[str] = typer.Option(None, "--request", "-r", help="Optional custom request to route"),
    path: str = typer.Option(".", "--path", "-p", help="Optional repository path containing profession templates"),
    list_demos: bool = typer.Option(False, "--list", help="List bundled demos and exit"),
    json_output: bool = typer.Option(False, "--json", help="Render raw JSON instead of human demo view"),
) -> None:
    """Show a non-mutating Kodex product demo."""
    if list_demos:
        console.print(JSON.from_data({"demos": available_demos()}))
        return
    packet = build_demo_packet(name, repo_root=path, request=request)
    if json_output:
        console.print(JSON.from_data(packet))
    else:
        _print_demo_human(packet)


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
