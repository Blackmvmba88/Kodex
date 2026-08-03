from __future__ import annotations

from typer.testing import CliRunner

from agent.main import app
from agent.modes import build_modes_catalog


runner = CliRunner()


def test_modes_catalog_contains_core_sections():
    catalog = build_modes_catalog()

    assert catalog["product"] == "Kodex"
    assert catalog["input_modes"]
    assert catalog["profession_lanes"]
    assert catalog["blackmamba_university_labs"]
    assert "kodex demo" in catalog["try_next"]


def test_modes_catalog_contains_expected_input_modes():
    catalog = build_modes_catalog()
    mode_ids = {mode["id"] for mode in catalog["input_modes"]}

    assert "prompt" in mode_ids
    assert "spec" in mode_ids
    assert "repo" in mode_ids
    assert "audio" in mode_ids
    assert "creative" in mode_ids
    assert "demo" in mode_ids


def test_modes_catalog_contains_profession_lanes():
    catalog = build_modes_catalog()
    lane_ids = {lane["id"] for lane in catalog["profession_lanes"]}

    assert "software_builder" in lane_ids
    assert "music_producer" in lane_ids
    assert "visual_artist" in lane_ids
    assert "scientist_lab" in lane_ids
    assert "educator" in lane_ids


def test_modes_catalog_contains_blackmamba_labs():
    catalog = build_modes_catalog()
    lab_ids = {lab["id"] for lab in catalog["blackmamba_university_labs"]}

    assert "waveforms_and_sound" in lab_ids
    assert "biomedical_tissue_simulation" in lab_ids
    assert "safe_ai_building" in lab_ids


def test_modes_cli_outputs_human_catalog():
    result = runner.invoke(app, ["modes"])

    assert result.exit_code == 0
    assert "Kodex" in result.output
    assert "Input Modes" in result.output
    assert "Profession Lanes" in result.output
    assert "BlackMamba University Labs" in result.output
    assert "Waveforms and Sound" in result.output


def test_modes_cli_outputs_json_catalog():
    result = runner.invoke(app, ["modes", "--json"])

    assert result.exit_code == 0
    assert '"product": "Kodex"' in result.output
    assert '"input_modes"' in result.output
    assert '"profession_lanes"' in result.output
    assert '"blackmamba_university_labs"' in result.output
