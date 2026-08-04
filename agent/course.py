from __future__ import annotations

"""BlackMamba University course module generator.

The course engine upgrades a non-mutating lab packet into a reusable course
module. It does not scan repositories, write files, call providers, run checks,
or perform high-stakes assessment. It only shapes a safe educational path.
"""

from dataclasses import dataclass
from typing import Any

from agent.lab import build_lab_packet


@dataclass(frozen=True)
class Lesson:
    title: str
    focus: str
    exercise: str
    artifact: str

    def to_dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "focus": self.focus,
            "exercise": self.exercise,
            "artifact": self.artifact,
        }


@dataclass(frozen=True)
class CourseModule:
    title: str
    request: str
    lane: str
    input_mode: str
    output_contract: str
    course_goal: str
    lessons: list[Lesson]
    capstone_project: str
    assessment: list[str]
    portfolio_artifact: str
    safety_boundary: list[str]
    next_commands: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "request": self.request,
            "lane": self.lane,
            "input_mode": self.input_mode,
            "output_contract": self.output_contract,
            "course_goal": self.course_goal,
            "lessons": [lesson.to_dict() for lesson in self.lessons],
            "capstone_project": self.capstone_project,
            "assessment": self.assessment,
            "portfolio_artifact": self.portfolio_artifact,
            "safety_boundary": self.safety_boundary,
            "next_commands": self.next_commands,
            "mutation": "none",
        }


def _course_title(route: dict[str, Any], lab: dict[str, Any]) -> str:
    lane = route["profession_name"]
    module = lab.get("module") or lab.get("title") or "BlackMamba University Module"
    return f"{module} — {lane} Track"


def _course_goal(route: dict[str, Any], lab: dict[str, Any]) -> str:
    contract = route["output_contract"].replace("_", " ")
    return (
        f"Turn the request into a safe, teachable {contract} pathway with a visible project artifact, "
        "clear measurements, and explicit mutation boundaries."
    )


def _lessons_for_lane(route: dict[str, Any], lab: dict[str, Any]) -> list[Lesson]:
    lane = route["profession"]
    variables = ", ".join(lab.get("variables", [])[:4]) or "inputs, constraints, and observable outputs"

    if lane == "software_builder":
        return [
            Lesson(
                title="Read the Product Intent",
                focus="Identify source documents, user goal, and safe output contract.",
                exercise="Run the request through guide/lab and describe the expected implementation path.",
                artifact="Intent summary packet",
            ),
            Lesson(
                title="Preview Before Mutation",
                focus="Use preview and dry-run as separate safety stages.",
                exercise="Compare app-build preview vs dry-run output and list what is allowed to write.",
                artifact="Dry-run safety report",
            ),
            Lesson(
                title="Guarded Apply Boundary",
                focus="Understand checkpoints, checks, and human review before commit.",
                exercise="Draft a ready-for-review checklist for the generated change.",
                artifact="Ready-for-review packet",
            ),
        ]

    if lane == "scientist_lab":
        return [
            Lesson(
                title="Name the Phenomenon",
                focus="Separate known physics/biology, simulation, hypothesis, and speculation.",
                exercise=f"List the key variables: {variables}.",
                artifact="Phenomenon map",
            ),
            Lesson(
                title="Build the Simulation Model",
                focus="Define a simple model before proposing experiments.",
                exercise="Write a minimal simulation plan with inputs, outputs, and measurable limits.",
                artifact="Simulation plan",
            ),
            Lesson(
                title="Explain the Boundary",
                focus="State what the model can and cannot claim.",
                exercise="Create safety notes and avoid medical, miracle, or reactionless-force claims.",
                artifact="Safety boundary card",
            ),
        ]

    if lane == "music_producer":
        return [
            Lesson(
                title="Route the Musical Intent",
                focus="Separate lyrics, audio analysis, release planning, and visual direction.",
                exercise="Convert the request into a producer packet with output contract and constraints.",
                artifact="Producer brief",
            ),
            Lesson(
                title="Measure the Work",
                focus="Use BPM, flow, syllables, arrangement, or mood as observable variables.",
                exercise=f"Define measurable variables: {variables}.",
                artifact="Music analysis grid",
            ),
            Lesson(
                title="Prepare the Release Boundary",
                focus="Keep publishing and overwrites behind explicit approval.",
                exercise="Draft a release/readiness checklist.",
                artifact="Release safety packet",
            ),
        ]

    if lane == "visual_artist":
        return [
            Lesson(
                title="Decode the Visual Ask",
                focus="Convert style, format, mood, and brand language into a visual brief.",
                exercise="Write one square-cover brief and one panoramic variant.",
                artifact="Visual brief pack",
            ),
            Lesson(
                title="Create Design Tokens",
                focus="Translate the idea into palette, typography, layout, and composition constraints.",
                exercise="Build a reusable visual token card.",
                artifact="Design token card",
            ),
            Lesson(
                title="Protect Source Assets",
                focus="Avoid destructive edits and preserve approvals.",
                exercise="Draft an asset-safe revision protocol.",
                artifact="Revision protocol",
            ),
        ]

    return [
        Lesson(
            title="Understand the Request",
            focus="Route the request into a profession lane and input mode.",
            exercise="Summarize the request, output contract, and safe boundary.",
            artifact="Intent packet",
        ),
        Lesson(
            title="Turn It Into a Project",
            focus="Define variables, deliverables, and a small buildable artifact.",
            exercise="Draft the project path and rubric.",
            artifact="Project brief",
        ),
        Lesson(
            title="Reflect and Reuse",
            focus="Convert the result into a repeatable template.",
            exercise="Write a reusable checklist for future requests.",
            artifact="Reusable template",
        ),
    ]


def _capstone_for_lane(route: dict[str, Any], lab: dict[str, Any]) -> str:
    lane = route["profession"]
    if lane == "software_builder":
        return "Produce a non-mutating implementation plan, dry-run packet, and ready-for-review checklist."
    if lane == "scientist_lab":
        return "Build a safe simulation brief with variables, measurable outputs, limits, and visualization plan."
    if lane == "music_producer":
        return "Create a producer-ready packet with analysis, creative direction, and release boundary."
    if lane == "visual_artist":
        return "Create a reusable visual brief with format variants, design tokens, and approval boundary."
    return "Create a reusable project packet that can become a portfolio artifact."


def build_course_module(request: str, repo_root: str = ".") -> dict[str, Any]:
    """Build a deterministic course module for a human request."""
    lab = build_lab_packet(request, repo_root=repo_root)
    route = lab["route"]
    lessons = _lessons_for_lane(route, lab)
    title = _course_title(route, lab)

    module = CourseModule(
        title=title,
        request=request,
        lane=route["profession"],
        input_mode=route["input_mode"],
        output_contract=route["output_contract"],
        course_goal=_course_goal(route, lab),
        lessons=lessons,
        capstone_project=_capstone_for_lane(route, lab),
        assessment=[
            "Can the student explain the intent route?",
            "Can the student identify variables, outputs, and limits?",
            "Can the student describe the safe mutation boundary?",
            "Can the student produce a reusable portfolio artifact?",
        ],
        portfolio_artifact=f"Portfolio packet: {title}",
        safety_boundary=lab.get("safety_notes", []) + [
            "Educational course planning only.",
            "No provider calls, file writes, checks, commits, pushes, or PRs.",
        ],
        next_commands=[
            f"kodex guide {request!r}",
            f"kodex lab {request!r}",
            "kodex modes",
        ],
    )
    return module.to_dict()
