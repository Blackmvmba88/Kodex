from __future__ import annotations

"""BlackMamba University lab packet builder.

A lab packet turns a routed human request into an educational, non-mutating
project/lab scaffold. It does not run simulations, call providers, write files,
or claim high-stakes outcomes. It gives the user a structured path to learn,
measure, simulate, and build safely.
"""

from dataclasses import dataclass
from typing import Any

from agent.guide import build_guide


@dataclass(frozen=True)
class LabSection:
    title: str
    items: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "items": self.items}


def _lab_title(route: dict[str, Any]) -> str:
    profession = route["profession"]
    output = route["output_contract"]
    if profession == "scientist_lab" and output == "simulation_plan":
        return "BlackMamba University Lab — Simulation Thinking"
    if profession == "software_builder":
        return "BlackMamba University Lab — Safe AI Building"
    if profession == "music_producer":
        return "BlackMamba University Lab — Audio-to-Artifact Pipeline"
    if profession == "visual_artist":
        return "BlackMamba University Lab — Visual Briefing System"
    if profession == "educator":
        return "BlackMamba University Lab — Lesson Builder"
    return "BlackMamba University Lab — Guided Build"


def _learning_objectives(route: dict[str, Any]) -> list[str]:
    profession = route["profession"]
    if profession == "scientist_lab":
        return [
            "Identify the phenomenon without overstating what is known.",
            "Separate known physics, simulation assumptions, hypotheses, and creative speculation.",
            "Define measurable variables before proposing any experiment.",
            "Produce a safe simulation-first artifact.",
        ]
    if profession == "software_builder":
        return [
            "Read intent and source context before generating code.",
            "Preview and dry-run before applying changes.",
            "Keep checkpoints, checks, and human review as hard boundaries.",
            "Turn the result into a reviewable diff, not an automatic push.",
        ]
    if profession == "music_producer":
        return [
            "Route music intent into lyric, mix, release, or visual artifact lanes.",
            "Preserve user format and avoid repeated generic structures.",
            "Generate useful packets before publishing or overwriting assets.",
        ]
    if profession == "visual_artist":
        return [
            "Translate visual intent into reusable direction before generation.",
            "Name color, composition, format, and safety boundaries clearly.",
            "Avoid destructive edits to source assets by default.",
        ]
    return [
        "Convert a human request into a clear learning path.",
        "Define output contract, rubric, and safe next action.",
    ]


def _variables(route: dict[str, Any]) -> list[str]:
    profession = route["profession"]
    input_mode = route["input_mode"]
    base = [
        f"profession_lane = {profession}",
        f"input_mode = {input_mode}",
        f"output_contract = {route['output_contract']}",
        f"confidence = {route['confidence']}",
    ]
    if profession == "scientist_lab":
        base.extend([
            "known_physics",
            "simulation_assumptions",
            "measurable_variables",
            "safe_experiment_boundary",
        ])
    elif profession == "software_builder":
        base.extend(["repo_state", "source_files", "write_plan", "check_commands"])
    elif profession == "music_producer":
        base.extend(["tempo", "format", "emotional_direction", "release_target"])
    elif profession == "visual_artist":
        base.extend(["palette", "composition", "aspect_ratio", "source_asset_policy"])
    return base


def _simulation_or_project(route: dict[str, Any], request: str) -> list[str]:
    profession = route["profession"]
    if profession == "scientist_lab":
        return [
            "Create a simplified model before discussing physical-world claims.",
            "State assumptions and limits explicitly.",
            "Sketch a visualization or notebook plan.",
            "Keep medical/biomedical requests educational and simulation-only.",
        ]
    if profession == "software_builder":
        return [
            f"Run: kodex profession {request!r}",
            f"Run: kodex app-build {request!r}",
            f"Run: kodex app-build {request!r} --dry-run",
            "Only apply on a task branch after review.",
        ]
    return [
        f"Run: kodex guide {request!r}",
        f"Run: kodex demo --request {request!r}",
        "Decide whether this becomes a draft, brief, simulation, or guarded build.",
    ]


def _deliverables(route: dict[str, Any]) -> list[str]:
    output = route["output_contract"]
    return [
        f"Primary artifact: {output}",
        "One-page explanation of assumptions and boundaries.",
        "A reusable template for a future similar request.",
        "A BlackMamba University portfolio artifact.",
    ]


def _rubric(route: dict[str, Any]) -> list[str]:
    return [
        "Intent was routed into the correct profession lane.",
        "Input mode and output contract are explicit.",
        "Safety notes and mutation boundaries are visible.",
        "The artifact is reusable, not a one-off answer.",
        "The work can be taught, tested, or reviewed by another person.",
    ]


def build_lab_packet(request: str, repo_root: str = ".") -> dict[str, Any]:
    """Build a deterministic BlackMamba University lab packet."""
    guide = build_guide(request, repo_root)
    route = guide["route"]
    sections = [
        LabSection("Learning Objectives", _learning_objectives(route)),
        LabSection("Variables / Inputs", _variables(route)),
        LabSection("Simulation or Project Path", _simulation_or_project(route, request)),
        LabSection("Deliverables", _deliverables(route)),
        LabSection("Rubric", _rubric(route)),
    ]

    return {
        "title": _lab_title(route),
        "request": request,
        "route": route,
        "mode_note": guide["mode_note"],
        "blackmamba_university_modules": guide["blackmamba_university_modules"],
        "sections": [section.to_dict() for section in sections],
        "safety_notes": guide["safety_notes"],
        "mutation_policy": "Non-mutating lab packet. It teaches, plans, and scopes. It does not execute or claim outcomes.",
        "next_commands": [step["command"] for step in guide["recommended_steps"][:3]],
    }
