from __future__ import annotations

from typer.testing import CliRunner

from agent.main import app


runner = CliRunner()


def test_course_cli_outputs_human_course_module():
    result = runner.invoke(app, ["course", "quiero una onda sinusoidal"])

    assert result.exit_code == 0
    assert "BlackMamba University" in result.output
    assert "Lessons" in result.output
    assert "Capstone" in result.output
    assert "Portfolio artifact" in result.output
    assert "none" in result.output


def test_course_cli_outputs_json_course_module():
    result = runner.invoke(app, ["course", "turn this README into an app with tests", "--json"])

    assert result.exit_code == 0
    assert '"lane": "software_builder"' in result.output
    assert '"mutation": "none"' in result.output
    assert '"lessons"' in result.output
    assert '"capstone_project"' in result.output


def test_course_cli_preserves_biomedical_safety_boundary():
    result = runner.invoke(app, ["course", "ver la piel como malla de Blender", "--json"])

    assert result.exit_code == 0
    assert "educational" in result.output.lower()
    assert "diagnose" in result.output.lower() or "diagnóstico" in result.output.lower()
    assert '"mutation": "none"' in result.output
