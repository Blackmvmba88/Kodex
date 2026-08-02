from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agent.demo import available_demos, build_demo_packet
from agent.main import app
from agent.profession_router import route_profession_dict


runner = CliRunner()


def test_available_demos_are_stable():
    assert available_demos() == ["app", "biomed", "music", "sine"]


def test_build_demo_packet_is_non_mutating_sine_demo():
    data = build_demo_packet("sine")

    assert data["name"] == "sine"
    assert data["mutation"] == "none"
    assert data["request"] == "quiero una onda sinusoidal"
    assert data["route"]["profession"] == "scientist_lab"
    assert data["route"]["input_mode"] == "creative"
    assert data["route"]["output_contract"] == "simulation_plan"
    assert "dry-run means no writes" in data["promise"]


def test_build_demo_packet_accepts_custom_request():
    data = build_demo_packet("sine", request="haz una portada con colores BlackMamba")

    assert data["name"] == "sine"
    assert data["request"] == "haz una portada con colores BlackMamba"
    assert data["route"]["profession"] == "visual_artist"
    assert data["mutation"] == "none"


def test_demo_packet_does_not_create_runtime_artifacts(tmp_path):
    repo = tmp_path
+    (repo / "configs").mkdir()
    source = Path("configs/profession_templates.json")
    (repo / "configs" / "profession_templates.json").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    data = build_demo_packet("biomed", repo_root=repo)

    assert data["mutation"] == "none"
    assert data["route"]["profession"] == "scientist_lab"
    assert not (repo / ".kodex").exists()
    assert not (repo / "generated").exists()
    assert not (repo / ".pytest_cache").exists()


def test_demo_uses_bundled_registry_when_run_outside_repo(tmp_path):
    outside_repo = tmp_path / "some-target-project"
    outside_repo.mkdir()

    data = build_demo_packet("sine", repo_root=outside_repo)

    assert data["route"]["profession"] == "scientist_lab"
    assert data["mutation"] == "none"
    assert not (outside_repo / ".kodex").exists()
    assert not (outside_repo / "generated").exists()


def test_profession_router_uses_bundled_registry_when_config_missing(tmp_path):
    data = route_profession_dict("quiero una onda sinusoidal", tmp_path)

    assert data["profession"] == "scientist_lab"
    assert data["input_mode"] == "creative"
    assert data["output_contract"] == "simulation_plan"


def test_demo_cli_lists_available_demos():
    result = runner.invoke(app, ["demo", "--list"])

    assert result.exit_code == 0
    assert '"demos"' in result.output
    assert '"sine"' in result.output
    assert '"biomed"' in result.output


def test_demo_cli_outputs_human_default_demo():
    result = runner.invoke(app, ["demo"])

    assert result.exit_code == 0
    assert "KODEX" in result.output
    assert "Intent Route" in result.output
    assert "Scientist / Lab" in result.output
    assert "Mutation" in result.output
    assert "none" in result.output


def test_demo_cli_json_outputs_default_demo_packet():
    result = runner.invoke(app, ["demo", "--json"])

    assert result.exit_code == 0
    assert '"name": "sine"' in result.output
    assert '"mutation": "none"' in result.output
    assert '"profession": "scientist_lab"' in result.output


def test_demo_cli_accepts_custom_request_in_human_mode():
    result = runner.invoke(app, ["demo", "--request", "turn this README into an app with tests"])

    assert result.exit_code == 0
    assert "Software Builder" in result.output
    assert "none" in result.output


def test_demo_cli_accepts_custom_request_in_json_mode():
    result = runner.invoke(app, ["demo", "--json", "--request", "turn this README into an app with tests"])

    assert result.exit_code == 0
    assert '"profession": "software_builder"' in result.output
    assert '"mutation": "none"' in result.output
