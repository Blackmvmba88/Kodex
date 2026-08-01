from __future__ import annotations

import json
from pathlib import Path

from agent.profession_router import route_profession, route_profession_dict


def _write_registry(root: Path) -> None:
    config_dir = root / "configs"
    config_dir.mkdir()
    registry = {
        "version": "test",
        "professions": [
            {
                "id": "music_producer",
                "name": "Music Producer",
                "input_modes": ["prompt", "audio", "creative"],
                "output_contracts": ["arrangement_plan", "mix_notes", "teaching_module"],
                "safe_actions": ["analyze"],
                "blocked_actions": ["publish_without_confirmation"],
                "experiments": ["flow difficulty analyzer"],
                "blackmamba_university_modules": ["Rap Metrics Lab"],
            },
            {
                "id": "software_builder",
                "name": "Software Builder",
                "input_modes": ["repo", "spec", "prompt"],
                "output_contracts": ["implementation_plan", "write_plan"],
                "safe_actions": ["scan", "dry_run"],
                "blocked_actions": ["push_without_approval"],
                "experiments": ["input-mode router"],
                "blackmamba_university_modules": ["Repo Reading"],
            },
            {
                "id": "educator",
                "name": "Educator",
                "input_modes": ["prompt", "file", "demo"],
                "output_contracts": ["lesson_plan", "quiz", "student_path"],
                "safe_actions": ["explain"],
                "blocked_actions": ["fabricate_source_claims"],
                "experiments": ["request-to-course converter"],
                "blackmamba_university_modules": ["Learning by Building"],
            },
            {
                "id": "visual_artist",
                "name": "Visual Artist",
                "input_modes": ["image", "screenshot", "prompt", "creative"],
                "output_contracts": ["art_brief", "layout_spec"],
                "safe_actions": ["brief"],
                "blocked_actions": ["overwrite_source_art_destructively"],
                "experiments": ["cover art director"],
                "blackmamba_university_modules": ["Cover Design Lab"],
            },
            {
                "id": "scientist_lab",
                "name": "Scientist / Lab",
                "input_modes": ["prompt", "data", "creative", "demo"],
                "output_contracts": ["model_explanation", "simulation_plan", "experiment_protocol", "learning_module"],
                "safe_actions": ["simulate"],
                "blocked_actions": ["medical_or_legal_claims_without_sources"],
                "experiments": ["sinusoidal waveform lab"],
                "blackmamba_university_modules": ["Waveforms and Sound"],
            },
        ],
    }
    (config_dir / "profession_templates.json").write_text(json.dumps(registry), encoding="utf-8")


def test_routes_iyari_sine_wave_to_scientist_lab_creative_simulation(tmp_path):
    _write_registry(tmp_path)
    route = route_profession("quiero una onda sinusoidal epica", tmp_path)

    assert route.profession == "scientist_lab"
    assert route.input_mode == "creative"
    assert route.output_contract == "simulation_plan"
    assert "sinusoidal" in route.matched_keywords
    assert "Waveforms and Sound" in route.blackmamba_university_modules
    assert route.safety_notes == [
        "Separate known physics, simulation, hypothesis, and creative speculation."
    ]


def test_routes_repo_request_to_software_builder(tmp_path):
    _write_registry(tmp_path)
    data = route_profession_dict("convierte este README en una app con tests", tmp_path)

    assert data["profession"] == "software_builder"
    assert data["input_mode"] in {"repo", "spec"}
    assert data["output_contract"] in {"implementation_plan", "write_plan"}
    assert "push_without_approval" in data["blocked_actions"]


def test_routes_music_request_to_music_producer_audio(tmp_path):
    _write_registry(tmp_path)
    route = route_profession("analiza bpm flow y dificultad de esta canción mp3", tmp_path)

    assert route.profession == "music_producer"
    assert route.input_mode == "audio"
    assert route.output_contract == "mix_notes"
    assert "Rap Metrics Lab" in route.blackmamba_university_modules


def test_routes_visual_request_to_visual_artist(tmp_path):
    _write_registry(tmp_path)
    route = route_profession("haz una portada con colores premium blackmamba", tmp_path)

    assert route.profession == "visual_artist"
    assert route.input_mode in {"image", "creative"}
    assert route.output_contract == "art_brief"


def test_routes_education_request_to_educator_learning_path(tmp_path):
    _write_registry(tmp_path)
    route = route_profession("convierte esto en clase para BlackMamba University", tmp_path)

    assert route.profession == "educator"
    assert route.output_contract in {"lesson_plan", "student_path"}
    assert "Learning by Building" in route.blackmamba_university_modules


def test_biomedical_language_adds_safety_notes(tmp_path):
    _write_registry(tmp_path)
    route = route_profession(
        "ver la piel y el tejido vivo como malla de Blender con vertices aristas y caras",
        tmp_path,
    )

    assert route.profession == "scientist_lab"
    assert route.output_contract in {"model_explanation", "simulation_plan"}
    assert any("educational/simulation-only" in note for note in route.safety_notes)
    assert any("Do not diagnose" in note for note in route.safety_notes)


def test_unknown_request_falls_back_to_software_builder(tmp_path):
    _write_registry(tmp_path)
    route = route_profession("organiza esto bien", tmp_path)

    assert route.profession == "software_builder"
    assert route.confidence == 0.25
