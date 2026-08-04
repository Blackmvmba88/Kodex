from __future__ import annotations

from typer.testing import CliRunner

from agent.main import app


runner = CliRunner()


def test_portfolio_cli_outputs_human_packet():
    result = runner.invoke(app, ["portfolio", "quiero una onda sinusoidal"])

    assert result.exit_code == 0
    assert "BlackMamba University Portfolio Artifact" in result.output
    assert "README Outline" in result.output
    assert "Demo Script" in result.output
    assert "Evidence Checklist" in result.output
    assert "Publish Boundary" in result.output
    assert "none" in result.output


def test_portfolio_cli_outputs_json_packet():
    result = runner.invoke(app, ["portfolio", "turn this README into an app with tests", "--json"])

    assert result.exit_code == 0
    assert '"lane": "software_builder"' in result.output
    assert '"mutation": "none"' in result.output
    assert '"artifact_name"' in result.output
    assert '"readme_outline"' in result.output
    assert '"evidence_checklist"' in result.output


def test_portfolio_cli_preserves_biomedical_publish_boundary():
    result = runner.invoke(app, ["portfolio", "ver la piel como malla de Blender", "--json"])

    assert result.exit_code == 0
    assert "biomedical" in result.output.lower()
    assert "diagnosis" in result.output.lower() or "diagnóstico" in result.output.lower()
    assert "treatment" in result.output.lower() or "tratamiento" in result.output.lower()
    assert '"mutation": "none"' in result.output
