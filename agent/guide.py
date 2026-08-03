from __future__ import annotations

"""Guided next-step planner for Kodex human requests."""

from dataclasses import dataclass
from typing import Any

from agent.modes import build_modes_catalog
from agent.profession_router import route_profession_dict


@dataclass(frozen=True)
class GuideStep:
    title: str
    command: str
    purpose: str
    mutation: str

    def to_dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "command": self.command,
            "purpose": self.purpose,
            "mutation": self.mutation,
        }


def _shell_single_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def _primary_mode_note(input_mode: str) -> str:
    notes = {
        "creative": "Treat this as a signature creative request: do not repeat generic templates.",
        "repo": "Read the repository before planning changes.",
        "spec": "Use README/SPEC style documents as source of truth.",
        "audio": "Route audio/music intent before producing release or mix artifacts.",
        "image": "Turn visual intent into a brief before generation or edits.",
        "screenshot": "Observe and diagnose before suggesting actions.",
        "demo": "Stay non-mutating and educational.",
        "prompt": "Start with intent routing before generating work.",
    }
    return notes.get(input_mode, "Start with intent routing before generating work.")


def _recommended_steps(request: str, route: dict[str, Any]) -> list[GuideStep]:
    quoted = _shell_single_quote(request)
    profession = route["profession"]
    input_mode = route["input_mode"]

    steps = [
        GuideStep(
            title="Route intent",
            command=f"kodex profession {quoted}",
            purpose="Confirm profession lane, input mode, output contract, experiments, and safety notes.",
            mutation="none",
        )
    ]

    if profession == "software_builder":
        steps.extend(
            [
                GuideStep(
                    title="Preview app build",
                    command=f"kodex app-build {quoted}",
                    purpose="Compile context and preview the candidate write plan without applying files.",
                    mutation="none",
                ),
                GuideStep(
                    title="Dry-run guarded build",
                    command=f"kodex app-build {quoted} --dry-run",
                    purpose="Run the full guarded simulation while keeping disk untouched.",
                    mutation="none",
                ),
                GuideStep(
                    title="Apply only from task branch",
                    command=f"kodex app-build {quoted} --apply",
                    purpose="Apply with checkpoint/checks and stop before commit.",
                    mutation="guarded local writes",
                ),
            ]
        )
    elif profession == "scientist_lab":
        steps.extend(
            [
                GuideStep(
                    title="Open product demo",
                    command=f"kodex demo --request {quoted}",
                    purpose="Show the concept as a safe, non-mutating simulation/product packet.",
                    mutation="none",
                ),
                GuideStep(
                    title="Map available labs",
                    command="kodex modes",
                    purpose="Find the relevant BlackMamba University lab and safety boundary.",
                    mutation="none",
                ),
            ]
        )
    elif profession == "music_producer":
        steps.extend(
            [
                GuideStep(
                    title="Demo music route",
                    command=f"kodex demo --request {quoted}",
                    purpose="Convert song/audio intent into a safe producer workflow packet.",
                    mutation="none",
                ),
                GuideStep(
                    title="Map modes",
                    command="kodex modes",
                    purpose="Choose whether this should become lyrics, mix notes, release plan, or visual brief.",
                    mutation="none",
                ),
            ]
        )
    elif profession == "visual_artist":
        steps.extend(
            [
                GuideStep(
                    title="Demo visual route",
                    command=f"kodex demo --request {quoted}",
                    purpose="Turn the visual intent into a brief-shaped product packet.",
                    mutation="none",
                ),
                GuideStep(
                    title="Map visual modes",
                    command="kodex modes",
                    purpose="Choose image, screenshot, creative, or file mode before generation/editing.",
                    mutation="none",
                ),
            ]
        )
    else:
        steps.extend(
            [
                GuideStep(
                    title="Demo route",
                    command=f"kodex demo --request {quoted}",
                    purpose="Show the request as a safe, non-mutating product packet.",
                    mutation="none",
                ),
                GuideStep(
                    title="Explore modes",
                    command="kodex modes",
                    purpose="Pick the correct input mode, profession lane, and learning lab.",
                    mutation="none",
                ),
            ]
        )

    if input_mode not in ("repo", "spec") and profession != "software_builder":
        steps.append(
            GuideStep(
                title="Escalate carefully",
                command="kodex app-build 'Implement MVP' --dry-run",
                purpose="Only move toward generated files through dry-run and guarded write mode.",
                mutation="none",
            )
        )

    return steps


def build_guide(request: str, repo_root: str = ".") -> dict[str, Any]:
    """Build a deterministic guided next-step packet for a human request."""
    route = route_profession_dict(request, repo_root)
    catalog = build_modes_catalog()
    steps = _recommended_steps(request, route)

    return {
        "request": request,
        "route": route,
        "mode_note": _primary_mode_note(route["input_mode"]),
        "recommended_steps": [step.to_dict() for step in steps],
        "blackmamba_university_modules": route.get("blackmamba_university_modules", []),
        "safety_notes": route.get("safety_notes", []),
        "catalog_try_next": catalog["try_next"],
        "mutation_policy": "Start non-mutating. Escalate only through dry-run, checkpoint, checks, and human review.",
    }
