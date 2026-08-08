from __future__ import annotations

"""BlackMamba showcase review gate.

The review gate evaluates whether a showcase kit is ready to share, demo, or
hold for more evidence. It is deterministic and non-mutating: no repository
scan, provider call, file write, checks, commits, pushes, PRs, uploads, or
publishing actions.
"""

from dataclasses import dataclass
from typing import Any

from agent.showcase import build_showcase_kit


@dataclass(frozen=True)
class GateCheck:
    name: str
    status: str
    reason: str
    weight: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "reason": self.reason,
            "weight": self.weight,
        }


@dataclass(frozen=True)
class ReviewGate:
    title: str
    request: str
    lane: str
    readiness_score: int
    decision: str
    checks: list[GateCheck]
    missing_evidence: list[str]
    risk_flags: list[str]
    recommended_actions: list[str]
    safety_boundary: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "request": self.request,
            "lane": self.lane,
            "readiness_score": self.readiness_score,
            "decision": self.decision,
            "checks": [check.to_dict() for check in self.checks],
            "missing_evidence": self.missing_evidence,
            "risk_flags": self.risk_flags,
            "recommended_actions": self.recommended_actions,
            "safety_boundary": self.safety_boundary,
            "mutation": "none",
        }


def _contains_any(values: list[str], needles: list[str]) -> bool:
    text = "\n".join(values).lower()
    return any(needle.lower() in text for needle in needles)


def _build_checks(showcase: dict[str, Any]) -> list[GateCheck]:
    proof = showcase.get("proof_checklist", [])
    gate = showcase.get("publish_safety_gate", [])
    variants = showcase.get("audience_variants", [])
    private_notes = showcase.get("private_review_notes", [])

    checks = [
        GateCheck(
            name="Intent route visible",
            status="pass" if showcase.get("lane") and showcase.get("input_mode") else "hold",
            reason="Showcase includes lane/input mode routing metadata.",
            weight=20,
        ),
        GateCheck(
            name="Proof checklist present",
            status="pass" if len(proof) >= 4 else "hold",
            reason="Proof checklist gives reviewers concrete evidence to inspect.",
            weight=20,
        ),
        GateCheck(
            name="Audience variants present",
            status="pass" if len(variants) >= 2 else "hold",
            reason="Showcase can be adapted for public, technical, or private review audiences.",
            weight=15,
        ),
        GateCheck(
            name="Publish safety gate present",
            status="pass" if len(gate) >= 4 else "hold",
            reason="Publishing is blocked behind explicit safety criteria.",
            weight=20,
        ),
        GateCheck(
            name="Private review notes present",
            status="pass" if private_notes else "hold",
            reason="Private notes preserve nuance before external sharing.",
            weight=10,
        ),
    ]

    if _contains_any(gate + proof + private_notes, ["diagnosis", "treatment", "biomedical", "medical"]):
        checks.append(
            GateCheck(
                name="High-stakes safety language present",
                status="pass",
                reason="Medical/biomedical language is explicitly bounded as educational or simulation-only.",
                weight=15,
            )
        )
    else:
        checks.append(
            GateCheck(
                name="High-stakes safety language not required",
                status="pass",
                reason="No biomedical/high-stakes terms were detected in the showcase gate.",
                weight=15,
            )
        )

    return checks


def _score(checks: list[GateCheck]) -> int:
    possible = sum(check.weight for check in checks)
    earned = sum(check.weight for check in checks if check.status == "pass")
    return round((earned / possible) * 100) if possible else 0


def _decision(score: int, risks: list[str], missing: list[str]) -> str:
    if any("medical" in risk.lower() or "biomedical" in risk.lower() for risk in risks):
        return "hold_until_safety_review"
    if any("raw private" in risk.lower() for risk in risks):
        return "hold_private_review"
    if score >= 90 and not missing:
        return "ready_for_private_demo"
    if score >= 75:
        return "revise_then_demo"
    return "hold_for_evidence"


def _missing_evidence(showcase: dict[str, Any], checks: list[GateCheck]) -> list[str]:
    missing = [check.name for check in checks if check.status != "pass"]
    proof = showcase.get("proof_checklist", [])
    if not _contains_any(proof, ["screenshot", "demo", "evidence", "proof"]):
        missing.append("Concrete visual/demo evidence")
    if not showcase.get("demo_talking_points"):
        missing.append("Demo talking points")
    return missing


def _risk_flags(showcase: dict[str, Any]) -> list[str]:
    gate = showcase.get("publish_safety_gate", [])
    notes = showcase.get("private_review_notes", [])
    proof = showcase.get("proof_checklist", [])
    combined = gate + notes + proof
    risks: list[str] = []

    if _contains_any(combined, ["raw private", "private session", "private sessions"]):
        risks.append("Raw private sessions must stay private unless explicitly approved.")
    if _contains_any(combined, ["medical", "biomedical", "diagnosis", "treatment"]):
        risks.append("Biomedical/medical language requires educational-only framing and safety review.")
    if _contains_any(combined, ["merge", "commit", "push", "tested"]):
        risks.append("Engineering claims must match verified actions and test evidence.")
    if _contains_any(combined, ["publish", "upload", "public"]):
        risks.append("Public sharing is blocked until publish gate criteria are satisfied.")

    return risks


def _recommended_actions(score: int, decision: str, missing: list[str], risks: list[str]) -> list[str]:
    actions = [
        "Run the showcase through private review before public sharing.",
        "Attach only evidence that actually exists.",
        "Keep claims aligned with completed actions and verified outputs.",
    ]

    if missing:
        actions.append("Fill missing evidence: " + ", ".join(missing[:4]) + ".")
    if risks:
        actions.append("Resolve risk flags before publishing or presenting externally.")
    if score >= 90 and decision == "ready_for_private_demo":
        actions.append("Record a short private demo using the talking points.")
    return actions


def build_review_gate(request: str, repo_root: str = ".") -> dict[str, Any]:
    """Build a deterministic review gate from a human request."""
    showcase = build_showcase_kit(request, repo_root=repo_root)
    checks = _build_checks(showcase)
    missing = _missing_evidence(showcase, checks)
    risks = _risk_flags(showcase)
    score = _score(checks)
    decision = _decision(score, risks, missing)

    gate = ReviewGate(
        title="BlackMamba Showcase Review Gate",
        request=request,
        lane=showcase["lane"],
        readiness_score=score,
        decision=decision,
        checks=checks,
        missing_evidence=missing,
        risk_flags=risks,
        recommended_actions=_recommended_actions(score, decision, missing, risks),
        safety_boundary=showcase.get("safety_boundary", []) + [
            "Review gate only.",
            "No publishing, uploads, repository writes, checks, commits, pushes, PRs, or external actions.",
        ],
    )
    return gate.to_dict()
