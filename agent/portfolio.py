from __future__ import annotations

"""BlackMamba University portfolio artifact generator.

The portfolio engine converts a course module into a presentation-ready evidence
packet. It does not write files, publish anything, call providers, run checks,
or perform external actions. It only describes what a strong portfolio artifact
should contain and how it should be demonstrated safely.
"""

from dataclasses import dataclass
from typing import Any

from agent.course import build_course_module


@dataclass(frozen=True)
class PortfolioSection:
    title: str
    items: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "items": self.items}


@dataclass(frozen=True)
class PortfolioPacket:
    title: str
    request: str
    lane: str
    input_mode: str
    output_contract: str
    artifact_name: str
    elevator_pitch: str
    readme_outline: list[str]
    demo_script: list[str]
    evidence_checklist: list[str]
    publish_boundary: list[str]
    safety_boundary: list[str]
    sections: list[PortfolioSection]
    next_commands: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "request": self.request,
            "lane": self.lane,
            "input_mode": self.input_mode,
            "output_contract": self.output_contract,
            "artifact_name": self.artifact_name,
            "elevator_pitch": self.elevator_pitch,
            "readme_outline": self.readme_outline,
            "demo_script": self.demo_script,
            "evidence_checklist": self.evidence_checklist,
            "publish_boundary": self.publish_boundary,
            "safety_boundary": self.safety_boundary,
            "sections": [section.to_dict() for section in self.sections],
            "next_commands": self.next_commands,
            "mutation": "none",
        }


def _artifact_name(course: dict[str, Any]) -> str:
    title = course["title"].replace(" — ", " - ")
    return f"{title} Portfolio Packet"


def _elevator_pitch(course: dict[str, Any]) -> str:
    lane = course["lane"].replace("_", " ")
    return (
        f"A BlackMamba University portfolio artifact for a {lane} request, "
        "showing the route from human intent to safe lab, course module, capstone, "
        "assessment, and reusable evidence."
    )


def _readme_outline(course: dict[str, Any]) -> list[str]:
    return [
        "# Project Title",
        "## What this demonstrates",
        "## Human request and intent route",
        "## Course goal",
        "## Lab / simulation / build path",
        "## Evidence and screenshots",
        "## Safety boundary",
        "## How to reproduce the demo",
        "## What I would improve next",
    ]


def _demo_script(course: dict[str, Any]) -> list[str]:
    return [
        "Open with the original human request.",
        "Show the profession lane, input mode, and output contract.",
        "Walk through the lab/course path in less than two minutes.",
        "Show the capstone artifact and explain what is measured or validated.",
        "State the safety boundary before discussing next steps.",
        "Close with the portfolio artifact and what it proves about the workflow.",
    ]


def _evidence_for_lane(course: dict[str, Any]) -> list[str]:
    lane = course["lane"]
    base = [
        "Original request captured exactly.",
        "Profession route and input mode recorded.",
        "Course goal and capstone included.",
        "Assessment criteria included.",
        "Safety boundary visible in the artifact.",
    ]

    if lane == "software_builder":
        return base + [
            "Preview or dry-run output included.",
            "No auto-commit or auto-push claim made.",
            "Ready-for-review checklist included.",
        ]
    if lane == "scientist_lab":
        return base + [
            "Variables and measurable outputs named.",
            "Known science, simulation, and speculation separated.",
            "No medical, miracle, or reactionless-force claim included.",
        ]
    if lane == "music_producer":
        return base + [
            "Producer brief or analysis grid included.",
            "Release boundary and approval step included.",
            "No overwrite or publishing claim made without approval.",
        ]
    if lane == "visual_artist":
        return base + [
            "Visual brief and format variants included.",
            "Design token or style card included.",
            "Source asset protection boundary included.",
        ]
    return base + ["Reusable checklist included."]


def _publish_boundary(course: dict[str, Any]) -> list[str]:
    return [
        "Do not publish raw private sessions without explicit approval.",
        "Do not present simulations as proven claims.",
        "Do not present educational biomedical content as diagnosis or treatment.",
        "Do not claim files were written, tested, committed, pushed, or merged unless that actually happened.",
        "Use the portfolio artifact as evidence of process, not as inflated marketing.",
    ]


def build_portfolio_packet(request: str, repo_root: str = ".") -> dict[str, Any]:
    """Build a deterministic portfolio packet from a human request."""
    course = build_course_module(request, repo_root=repo_root)
    artifact_name = _artifact_name(course)

    sections = [
        PortfolioSection(
            title="What to show",
            items=[
                course["request"],
                course["course_goal"],
                course["capstone_project"],
                course["portfolio_artifact"],
            ],
        ),
        PortfolioSection(
            title="What to prove",
            items=[
                "The system routed intent before acting.",
                "The artifact has a clear output contract.",
                "The safety boundary is visible and testable.",
                "The result can be reused as a lesson, demo, or case study.",
            ],
        ),
        PortfolioSection(
            title="What not to claim",
            items=_publish_boundary(course),
        ),
    ]

    packet = PortfolioPacket(
        title="BlackMamba University Portfolio Artifact",
        request=request,
        lane=course["lane"],
        input_mode=course["input_mode"],
        output_contract=course["output_contract"],
        artifact_name=artifact_name,
        elevator_pitch=_elevator_pitch(course),
        readme_outline=_readme_outline(course),
        demo_script=_demo_script(course),
        evidence_checklist=_evidence_for_lane(course),
        publish_boundary=_publish_boundary(course),
        safety_boundary=course.get("safety_boundary", []) + [
            "Portfolio planning only.",
            "No external publishing, uploads, repository writes, commits, pushes, or PRs.",
        ],
        sections=sections,
        next_commands=[
            f"kodex guide {request!r}",
            f"kodex lab {request!r}",
            f"kodex course {request!r}",
            "kodex modes",
        ],
    )
    return packet.to_dict()
