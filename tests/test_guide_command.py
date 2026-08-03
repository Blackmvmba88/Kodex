from __future__ import annotations

from typer.testing import CliRunner

from agent.guide import build_guide
from agent.main import app


runner = CliRunner()


def test_guide_routes_sine_wave_to_science_path():
    data = build_guide("quiero una onda sinusoidal")

    assert data["route"]["profession"] == "scientist_lab"
    assert data["route"]["input_mode"] == "creative"
    assert data["route"]["output_contract"] == "simulation_plan"
    assert data["recommended_steps"][0]["command"] == "kodex profession 'quiero una onda sinusoidal'"
    assert any(step["command"].startswith("kodex demo --request") for step in data["recommended_steps"])
    assert data["mutation_policy"].startswith("Start non-mutating")


def test_guide_routes_software_to_app_build_path():
    data = build_guide("turn this README into an app with tests")

    commands = [step["command"] for step in data["recommended_steps"]]
    assert data["route"]["profession"] == "software_builder"
    assert any(command.endswith("--dry-run") for command in commands)
    assert any(command.endswith("--apply") for command in commands)
    assert any(step["mutation"] == "guarded local writes" for step in data["recommended_steps"])


def test_guide_biomedical_request_keeps_safety_notes():
    data = build_guide("ver la piel como malla de Blender con vertices aristas y caras")

    assert data["route"]["profession"] == "scientist_lab"
    assert data["safety_notes"]
    assert any("simulation-only" in note for note in data["safety_notes"])
    assert any("diagnose" in note for note in data["safety_notes"])


def test_guide_cli_human_output():
    result = runner.invoke(app, ["guide", "quiero una onda sinusoidal"])

    assert result.exit_code == 0
    assert "KODEX GUIDE" in result.output
    assert "Recommended Path" in result.output
    assert "Scientist / Lab" in result.output
    assert "kodex profession" in result.output


def test_guide_cli_json_output():
    result = runner.invoke(app, ["guide", "--json", "turn this README into an app with tests"])

    assert result.exit_code == 0
    assert '"request": "turn this README into an app with tests"' in result.output
    assert '"profession": "software_builder"' in result.output
    assert '"mutation_policy"' in result.output


def test_guide_cli_custom_path_with_missing_config_uses_fallback(tmp_path):
    result = runner.invoke(app, ["guide", "--path", str(tmp_path), "quiero una onda sinusoidal"])

    assert result.exit_code == 0
    assert "Scientist / Lab" in result.output
    assert "Recommended Path" in result.output
