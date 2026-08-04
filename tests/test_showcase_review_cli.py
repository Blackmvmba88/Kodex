from __future__ import annotations

from typer.testing import CliRunner

from agent.main import app
from agent.review_gate import build_review_gate
from agent.showcase import build_showcase_kit

runner = CliRunner()


def test_showcase_packet_carries_route_metadata() -> None:
    kit = build_showcase_kit("quiero una onda sinusoidal")

    assert kit["title"] == "BlackMamba Showcase Kit"
    assert kit["input_mode"]
    assert kit["output_contract"]
    assert kit["mutation"] == "none"
    assert "safety_boundary" in kit


def test_review_gate_intent_route_check_passes() -> None:
    gate = build_review_gate("quiero una onda sinusoidal")

    route_check = next(check for check in gate["checks"] if check["name"] == "Intent route visible")
    assert route_check["status"] == "pass"
    assert gate["mutation"] == "none"


def test_showcase_cli_outputs_human_kit() -> None:
    result = runner.invoke(app, ["showcase", "quiero una onda sinusoidal"])

    assert result.exit_code == 0
    assert "BlackMamba Showcase Kit" in result.output
    assert "Audience Variants" in result.output
    assert "Publish Safety Gate" in result.output


def test_showcase_cli_json_outputs_kit() -> None:
    result = runner.invoke(app, ["showcase", "turn this README into an app with tests", "--json"])

    assert result.exit_code == 0
    assert '"public_summary"' in result.output
    assert '"audience_variants"' in result.output
    assert '"mutation": "none"' in result.output


def test_review_gate_cli_outputs_human_gate() -> None:
    result = runner.invoke(app, ["review-gate", "ver la piel como malla de Blender"])

    assert result.exit_code == 0
    assert "BlackMamba Showcase Review Gate" in result.output
    assert "Readiness" in result.output
    assert "Decision" in result.output
    assert "Review Checks" in result.output


def test_review_gate_cli_json_outputs_gate() -> None:
    result = runner.invoke(app, ["review-gate", "turn this README into an app with tests", "--json"])

    assert result.exit_code == 0
    assert '"readiness_score"' in result.output
    assert '"decision"' in result.output
    assert '"mutation": "none"' in result.output
