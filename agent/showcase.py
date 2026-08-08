from __future__ import annotations

"""BlackMamba showcase kit generator.

The showcase engine upgrades a portfolio packet into a safe presentation kit for
public, private, and technical audiences. It never publishes, uploads, writes
files, calls providers, runs checks, commits, pushes, or opens PRs.
"""

from dataclasses import dataclass
from typing import Any

from agent.portfolio import build_portfolio_packet


@dataclass(frozen=True)
class AudienceVariant:
    audience: str
    angle: str
    opening_line: str
    proof_points: list[str]
    avoid: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "audience": self.audience,
            "angle": self.angle,
            "opening_line": self.opening_line,
            "proof_points": self.proof_points,
            "avoid": self.avoid,
        }


@dataclass(frozen=True)
class ShowcaseKit:
    title: str
    request: str
    lane: str
    input_mode: str
    output_contract: str
    artifact_name: str
    public_summary: str
    private_review_notes: list[str]
    demo_talking_points: list[str]
    audience_variants: list[AudienceVariant]
    publish_safety_gate: list[str]
    proof_checklist: list[str]
    safety_boundary: list[str]
    next_commands: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "request": self.request,
            "lane": self.lane,
            "input_mode": self.input_mode,
            "output_contract": self.output_contract,
            "artifact_name": self.artifact_name,
            "public_summary": self.public_summary,
            "private_review_notes": self.private_review_notes,
            "demo_talking_points": self.demo_talking_points,
            "audience_variants": [variant.to_dict() for variant in self.audience_variants],
            "publish_safety_gate": self.publish_safety_gate,
            "proof_checklist": self.proof_checklist,
            "safety_boundary": self.safety_boundary,
            "next_commands": self.next_commands,
            "mutation": "none",
        }


def _public_summary(portfolio: dict[str, Any]) -> str:
    lane = portfolio["lane"].replace("_", " ")
    summary = (
        f"A BlackMamba workflow showcase for a {lane} request: human intent is routed, "
        "turned into a safe lab, expanded into a course, packaged as portfolio evidence, "
        "and presented with explicit safety and publishing boundaries."
    )
    if portfolio["lane"] == "scientist_lab":
        summary += " The showcase frames science work as simulation-first and keeps claims bounded."
    return summary


def _private_review_notes(portfolio: dict[str, Any]) -> list[str]:
    return [
        "Confirm the original request is represented accurately.",
        "Confirm no private raw session content is included without approval.",
        "Confirm simulations are labeled as simulations, not proven claims.",
        "Confirm biomedical or high-stakes language remains educational only.",
        "Confirm repository actions are not claimed unless they actually happened.",
        "Confirm the showcase can stand alone without exaggerating capabilities.",
    ]


def _talking_points(portfolio: dict[str, Any]) -> list[str]:
    return [
        "Start with the human request and why it matters.",
        "Explain how Kodex routes the request before acting.",
        "Show the lab/course/portfolio chain as a reusable learning path.",
        "Point to the evidence checklist instead of making vague claims.",
        "State the publish boundary before sharing or distributing anything.",
        "End with what the artifact proves and what remains future work.",
    ]


def _audience_variants(portfolio: dict[str, Any]) -> list[AudienceVariant]:
    lane = portfolio["lane"]
    shared_avoid = [
        "Do not claim external publishing happened automatically.",
        "Do not expose raw private sessions.",
        "Do not inflate simulation or biomedical claims.",
    ]

    variants = [
        AudienceVariant(
            audience="technical reviewer",
            angle="Architecture, determinism, tests, and mutation boundaries.",
            opening_line="This showcase demonstrates a deterministic local-first workflow from request routing to portfolio evidence.",
            proof_points=[
                "Every layer returns structured data.",
                "Commands stay non-mutating until explicit guarded write paths.",
                "Safety boundaries travel through the chain.",
            ],
            avoid=shared_avoid,
        ),
        AudienceVariant(
            audience="creative collaborator",
            angle="How a raw idea becomes a reusable artifact.",
            opening_line="This turns a creative spark into a lab, course, portfolio packet, and showcase script.",
            proof_points=[
                "Original intent is preserved.",
                "The output becomes teachable and repeatable.",
                "The artifact can support music, visual, software, or lab work.",
            ],
            avoid=shared_avoid,
        ),
        AudienceVariant(
            audience="BlackMamba University learner",
            angle="Learning path, exercises, capstone, and proof of work.",
            opening_line="This is a learning module that ends with evidence, not just an answer.",
            proof_points=[
                "The lab defines variables and deliverables.",
                "The course defines lessons and assessment.",
                "The portfolio defines what to show and what not to claim.",
            ],
            avoid=shared_avoid,
        ),
    ]

    if lane == "software_builder":
        variants.append(
            AudienceVariant(
                audience="engineering lead",
                angle="Preview, dry-run, review, and controlled mutation.",
                opening_line="This shows a product path where write actions are gated behind reviewable steps.",
                proof_points=[
                    "Preview and dry-run are separate concepts.",
                    "Apply is guarded and does not imply commit/push.",
                    "The showcase should cite actual checks only when they ran.",
                ],
                avoid=shared_avoid + ["Do not claim tests passed unless test output exists."],
            )
        )
    elif lane == "scientist_lab":
        variants.append(
            AudienceVariant(
                audience="science-minded reviewer",
                angle="Known science, simulation, hypothesis, and limits.",
                opening_line="This shows a simulation-first lab path with explicit claim boundaries.",
                proof_points=[
                    "Variables and measurable outputs are named.",
                    "Speculation is separated from known behavior.",
                    "Biomedical and physics claims remain bounded.",
                ],
                avoid=shared_avoid + ["Do not imply diagnosis, treatment, cure, antigravity, or free energy."],
            )
        )

    return variants


def _publish_gate(portfolio: dict[str, Any]) -> list[str]:
    return list(portfolio.get("publish_boundary", [])) + [
        "Human approval required before public posting.",
        "Remove personal, private, or raw-session material before sharing.",
        "Mark generated or simulated content clearly.",
        "Keep claims tied to actual evidence in the packet.",
    ]


def build_showcase_kit(request: str, repo_root: str = ".") -> dict[str, Any]:
    """Build a deterministic showcase kit from a human request."""
    portfolio = build_portfolio_packet(request, repo_root=repo_root)
    kit = ShowcaseKit(
        title="BlackMamba Showcase Kit",
        request=request,
        lane=portfolio["lane"],
        input_mode=portfolio["input_mode"],
        output_contract=portfolio["output_contract"],
        artifact_name=portfolio["artifact_name"],
        public_summary=_public_summary(portfolio),
        private_review_notes=_private_review_notes(portfolio),
        demo_talking_points=_talking_points(portfolio),
        audience_variants=_audience_variants(portfolio),
        publish_safety_gate=_publish_gate(portfolio),
        proof_checklist=list(portfolio.get("evidence_checklist", [])) + [
            "Showcase script reviewed.",
            "Audience variant selected.",
            "Publish safety gate completed.",
        ],
        safety_boundary=list(portfolio.get("safety_boundary", [])) + [
            "Showcase planning only.",
            "No publishing, uploads, repository writes, checks, commits, pushes, PRs, or external actions.",
        ],
        next_commands=[
            f"kodex guide {request!r}",
            f"kodex lab {request!r}",
            f"kodex course {request!r}",
            f"kodex portfolio {request!r}",
            "kodex modes",
        ],
    )
    return kit.to_dict()
