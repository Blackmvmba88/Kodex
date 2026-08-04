from __future__ import annotations

from agent.showcase import build_showcase_kit


def test_showcase_engine_builds_public_and_private_layers():
    kit = build_showcase_kit("quiero una onda sinusoidal")

    assert kit["title"] == "BlackMamba Showcase Kit"
    assert kit["mutation"] == "none"
    assert "public_summary" in kit
    assert kit["private_review_notes"]
    assert kit["demo_talking_points"]
    assert kit["audience_variants"]
    assert any("publish" in item.lower() for item in kit["publish_safety_gate"])


def test_showcase_engine_carries_software_specific_review_angle():
    kit = build_showcase_kit("turn this README into an app with tests")

    assert kit["lane"] == "software_builder"
    assert any(variant["audience"] == "engineering lead" for variant in kit["audience_variants"])
    assert any("tests passed" in avoid.lower() for variant in kit["audience_variants"] for avoid in variant["avoid"])
    assert any("Preview" in point or "dry-run" in point for point in kit["proof_checklist"] + kit["public_summary"].split())


def test_showcase_engine_preserves_scientist_safety_claim_boundaries():
    kit = build_showcase_kit("ver la piel como malla de Blender")

    assert kit["lane"] == "scientist_lab"
    gate = " ".join(kit["publish_safety_gate"]).lower()
    variants = " ".join(
        avoid for variant in kit["audience_variants"] for avoid in variant["avoid"]
    ).lower()
    assert "diagnosis" in gate or "diagnóstico" in gate or "treatment" in gate
    assert "diagnosis" in variants or "treatment" in variants or "cure" in variants
    assert "simulation" in kit["public_summary"].lower()


def test_showcase_engine_keeps_private_raw_sessions_private():
    kit = build_showcase_kit("make a showcase from my BlackMamba creative workflow")

    gate = " ".join(kit["publish_safety_gate"]).lower()
    notes = " ".join(kit["private_review_notes"]).lower()
    assert "raw" in gate or "raw" in notes
    assert "private" in gate
    assert "approval" in gate


def test_showcase_engine_does_not_mutate_or_publish():
    kit = build_showcase_kit("quiero una onda sinusoidal")

    assert kit["mutation"] == "none"
    gate = " ".join(kit["publish_safety_gate"]).lower()
    assert "approval" in gate
    assert "before public" in gate or "before sharing" in gate
    assert all("git push" not in command for command in kit["next_commands"])
