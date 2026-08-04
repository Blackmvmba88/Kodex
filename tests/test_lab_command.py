from __future__ import annotations

from typer.testing import CliRunner

from agent.lab import build_lab_packet
from agent.main import app


runner = CliRunner()


def test_lab_packet_for_sine_wave_is_science_lab():
    data = build_lab_packet("quiero una onda sinusoidal")

    assert data["route"]["profession"] == "scientist_lab"
    assert data["route"]["output_contract"] == "simulation_plan"
    assert data["mutation_policy"].startswith("Non-mutating")
    assert any(section["title"] == "Learning Objectives" for section in data["sections"])
    assert "Waveforms and Sound" in data["blackmamba_university_modules"]


def test_lab_packet_for_software_request_includes_safe_build_path():
    data = build_lab_packet("turn this README into an app with tests")

    assert data["route"]["profession"] == "software_builder"
    assert any("dry-run" in command for command in data["next_commands"])
    assert any(section["title"] == "Simulation or Project Path" for section in data["sections"])


def test_lab_packet_for_biomedical_request_keeps_safety_notes():
    data = build_lab_packet("ver la piel como malla de Blender con vertices aristas y caras")

    assert data["route"]["profession"] == "scientist_lab"
    assert any("medical" in note.lower() or "biomedical" in note.lower() for note in data["safety_notes"])
    assert any("No diagnosis" in item or "diagnosis" in item for section in data["sections"] for item in section["items"] + data["safety_notes"])


def test_lab_cli_outputs_human_view():
    result = runner.invoke(app, ["lab", "quiero una onda sinusoidal"])

    assert result.exit_code == 0
    assert "BlackMamba University Lab" in result.output
    assert "Learning Objectives" in result.output
    assert "Mutation policy" in result.output
    assert "Waveforms and Sound" in result.output


def test_lab_cli_outputs_json_view():
    result = runner.invoke(app, ["lab", "quiero una onda sinusoidal", "--json"])

    assert result.exit_code == 0
    assert '"route"' in result.output
    assert '"sections"' in result.output
    assert '"mutation_policy"' in result.output


def test_lab_cli_software_route_has_next_commands():
    result = runner.invoke(app, ["lab", "turn this README into an app with tests", "--json"])

    assert result.exit_code == 0
    assert '"software_builder"' in result.output
    assert "app-build" in result.output
