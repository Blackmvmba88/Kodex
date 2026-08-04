from __future__ import annotations

from agent.review_gate import build_review_gate


def test_review_gate_builds_non_mutating_packet():
    gate = build_review_gate("quiero una onda sinusoidal")

    assert gate["title"] == "BlackMamba Showcase Review Gate"
    assert gate["mutation"] == "none"
    assert gate["readiness_score"] >= 75
    assert gate["checks"]
    assert gate["recommended_actions"]


def test_review_gate_has_decision_and_missing_evidence():
    gate = build_review_gate("quiero una onda sinusoidal")

    assert gate["decision"] in {
        "ready_for_private_demo",
        "revise_then_demo",
        "hold_for_evidence",
        "hold_private_review",
        "hold_until_safety_review",
    }
    assert isinstance(gate["missing_evidence"], list)
    assert isinstance(gate["risk_flags"], list)


def test_review_gate_flags_software_claim_risk_boundary():
    gate = build_review_gate("turn this README into an app with tests")

    assert gate["lane"] == "software_builder"
    joined = "\n".join(gate["risk_flags"] + gate["safety_boundary"]).lower()
    assert "commit" in joined or "push" in joined or "tested" in joined
    assert gate["mutation"] == "none"


def test_review_gate_preserves_biomedical_safety_review():
    gate = build_review_gate("ver la piel como malla de Blender")

    joined = "\n".join(gate["risk_flags"] + gate["safety_boundary"]).lower()
    assert "biomedical" in joined or "medical" in joined or "diagnosis" in joined
    assert gate["decision"] in {"hold_until_safety_review", "revise_then_demo", "hold_for_evidence"}
    assert gate["mutation"] == "none"


def test_review_gate_blocks_external_actions():
    gate = build_review_gate("publica este showcase")

    joined = "\n".join(gate["recommended_actions"] + gate["safety_boundary"] + gate["risk_flags"]).lower()
    assert "publishing" in joined or "public" in joined or "upload" in joined
    assert "no publishing" in joined or "blocked" in joined
    assert gate["mutation"] == "none"
