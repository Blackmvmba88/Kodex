from __future__ import annotations

from agent.portfolio import build_portfolio_packet


def test_portfolio_packet_for_science_request():
    packet = build_portfolio_packet("quiero una onda sinusoidal")

    assert packet["title"] == "BlackMamba University Portfolio Artifact"
    assert packet["lane"] == "scientist_lab"
    assert packet["mutation"] == "none"
    assert "Portfolio Packet" in packet["artifact_name"]
    assert any("variables" in item.lower() for item in packet["evidence_checklist"])
    assert any("simulation" in item.lower() for item in packet["publish_boundary"])


def test_portfolio_packet_for_software_request():
    packet = build_portfolio_packet("turn this README into an app with tests")

    assert packet["lane"] == "software_builder"
    assert packet["output_contract"] == "implementation_plan"
    assert any("dry-run" in item.lower() for item in packet["evidence_checklist"])
    assert any("ready-for-review" in item.lower() for item in packet["evidence_checklist"])
    assert packet["mutation"] == "none"


def test_portfolio_packet_preserves_biomedical_safety():
    packet = build_portfolio_packet("ver la piel como malla de Blender")

    safety_text = " ".join(packet["safety_boundary"] + packet["publish_boundary"]).lower()
    assert packet["lane"] == "scientist_lab"
    assert "educational" in safety_text
    assert "diagnosis" in safety_text or "diagnóstico" in safety_text
    assert "treatment" in safety_text or "tratamiento" in safety_text
    assert packet["mutation"] == "none"


def test_portfolio_packet_contains_demo_and_readme_structure():
    packet = build_portfolio_packet("haz una portada BlackMamba premium")

    assert packet["lane"] == "visual_artist"
    assert "## Evidence and screenshots" in packet["readme_outline"]
    assert any("Open with the original human request" in step for step in packet["demo_script"])
    assert any(section["title"] == "What not to claim" for section in packet["sections"])


def test_portfolio_packet_does_not_create_runtime_artifacts(tmp_path):
    packet = build_portfolio_packet("quiero una onda sinusoidal", repo_root=str(tmp_path))

    assert packet["mutation"] == "none"
    assert not (tmp_path / ".kodex").exists()
    assert not (tmp_path / "generated").exists()
    assert not (tmp_path / ".pytest_cache").exists()
