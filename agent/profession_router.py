from __future__ import annotations

"""Profession-aware intent routing for Kodex.

This module turns a raw human request into a safe, reusable route:

    human request
      -> likely profession lane
      -> input mode
      -> output contract
      -> suggested experiments
      -> BlackMamba University modules

The router is intentionally lightweight and deterministic for v0.1. It does not
call a model, does not mutate files, and does not claim high-stakes outcomes.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_DEFAULT_TEMPLATE_PATH = Path("configs/profession_templates.json")

_BUNDLED_REGISTRY: dict[str, Any] = {
    "version": "0.1.0",
    "purpose": "Bundled fallback registry for installed Kodex profession-aware workflows.",
    "principles": [
        "input mode first",
        "profession lane before generation",
        "safe output contracts",
        "never repeat; always mutate; always elevate",
        "every request can become a reusable learning module",
    ],
    "professions": [
        {
            "id": "music_producer",
            "name": "Music Producer",
            "input_modes": ["prompt", "audio", "file", "creative", "demo"],
            "output_contracts": ["arrangement_plan", "lyric_sheet", "mix_notes", "cover_art_brief", "release_plan"],
            "safe_actions": ["analyze", "draft", "template", "generate_preview"],
            "blocked_actions": ["publish_without_confirmation", "overwrite_master_audio"],
            "experiments": ["flow difficulty analyzer", "BPM-to-visual generator", "release readiness checker"],
            "blackmamba_university_modules": ["Song Anatomy", "Rap Metrics Lab", "Release Pipeline"],
        },
        {
            "id": "software_builder",
            "name": "Software Builder",
            "input_modes": ["repo", "spec", "prompt", "file", "screenshot", "demo"],
            "output_contracts": ["spec", "implementation_plan", "write_plan", "patch_preview", "test_plan"],
            "safe_actions": ["scan", "plan", "dry_run", "checkpoint", "apply_guarded", "run_checks"],
            "blocked_actions": ["commit_without_approval", "push_without_approval", "write_secrets"],
            "experiments": ["profession-aware app builder", "input-mode router", "demo command"],
            "blackmamba_university_modules": ["Repo Reading", "Safe Refactoring", "Testing Rituals"],
        },
        {
            "id": "educator",
            "name": "Educator",
            "input_modes": ["prompt", "file", "profession", "course", "demo"],
            "output_contracts": ["lesson_plan", "quiz", "rubric", "project_brief", "student_path"],
            "safe_actions": ["explain", "scaffold", "quiz", "summarize", "generate_project"],
            "blocked_actions": ["fabricate_source_claims", "grade_high_stakes_work_without_context"],
            "experiments": ["request-to-course converter", "student project ladder", "skill tree builder"],
            "blackmamba_university_modules": ["Learning by Building", "Creative Math Lab", "Portfolio Education"],
        },
        {
            "id": "visual_artist",
            "name": "Visual Artist",
            "input_modes": ["image", "screenshot", "prompt", "creative", "file", "demo"],
            "output_contracts": ["art_brief", "prompt_pack", "layout_spec", "brand_tokens", "asset_checklist"],
            "safe_actions": ["describe", "brief", "template", "generate_variations", "export_specs"],
            "blocked_actions": ["claim_identity_of_real_people", "overwrite_source_art_destructively"],
            "experiments": ["cover art director", "brand palette generator", "music-to-visual mapper"],
            "blackmamba_university_modules": ["Cover Design Lab", "Visual Identity", "Prompt Direction"],
        },
        {
            "id": "scientist_lab",
            "name": "Scientist / Lab",
            "input_modes": ["prompt", "file", "data", "creative", "demo"],
            "output_contracts": ["model_explanation", "simulation_plan", "notebook_outline", "experiment_protocol", "learning_module"],
            "safe_actions": ["explain", "simulate", "visualize", "template", "generate_demo"],
            "blocked_actions": ["unsafe_lab_protocols", "medical_or_legal_claims_without_sources"],
            "experiments": ["sinusoidal waveform lab", "physics-to-audio demo", "math-to-visual module"],
            "blackmamba_university_modules": ["Creative Signals", "Waveforms and Sound", "Simulation Thinking"],
        },
    ],
}

_INPUT_MODE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "audio": ("audio", "cancion", "canción", "mp3", "wav", "bpm", "voz", "sonido", "mezcla"),
    "image": ("imagen", "portada", "cover", "foto", "visual", "dibujo", "arte"),
    "screenshot": ("screenshot", "captura", "pantalla", "terminal", "error en pantalla"),
    "repo": ("repo", "repositorio", "github", "codigo", "código", "tests", "pytest"),
    "spec": ("readme", "spec", "agents.md", "prd", "arquitectura"),
    "file": ("archivo", "csv", "json", "txt", "documento"),
    "data": ("dataset", "datos", "tabla", "csv", "medicion", "medición"),
    "creative": ("quiero", "imagina", "hazlo epico", "hazlo épico", "onda", "vibra", "concepto"),
    "demo": ("demo", "ejemplo", "showcase", "sin tocar nada"),
}

_HIGH_STAKES_KEYWORDS = (
    "diagnosticar",
    "diagnóstico",
    "curar",
    "tratamiento",
    "medicina",
    "paciente",
    "cancer",
    "cáncer",
    "herida",
    "piel",
    "tejido vivo",
    "terapia",
    "dosis",
)

_PROFESSION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "music_producer": ("cancion", "canción", "rola", "rap", "bpm", "letra", "mix", "master", "soundcloud", "suno", "distrokid", "voz", "audio"),
    "software_builder": ("repo", "codigo", "código", "app", "cli", "github", "pytest", "readme", "test", "branch", "pr", "programa"),
    "educator": ("clase", "curso", "universidad", "blackmamba university", "quiz", "rúbrica", "rubrica", "aprender", "enseñar", "modulo", "módulo"),
    "visual_artist": ("portada", "cover", "logo", "colores", "branding", "visual", "video", "diseño", "imagen", "screenshot"),
    "scientist_lab": (
        "onda", "sinusoidal", "frecuencia", "resonancia", "armonico", "armónico", "cuantico", "cuántico",
        "particula", "partícula", "campo", "magnetico", "magnético", "simulacion", "simulación", "tejido",
        "molecula", "molécula", "blender", "malla", "vertice", "vértice", "arista", "cara",
    ),
}


@dataclass(frozen=True)
class ProfessionRoute:
    profession: str
    profession_name: str
    input_mode: str
    output_contract: str
    confidence: float
    matched_keywords: list[str]
    experiments: list[str]
    blackmamba_university_modules: list[str]
    safe_actions: list[str]
    blocked_actions: list[str]
    safety_notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "profession": self.profession,
            "profession_name": self.profession_name,
            "input_mode": self.input_mode,
            "output_contract": self.output_contract,
            "confidence": self.confidence,
            "matched_keywords": self.matched_keywords,
            "experiments": self.experiments,
            "blackmamba_university_modules": self.blackmamba_university_modules,
            "safe_actions": self.safe_actions,
            "blocked_actions": self.blocked_actions,
            "safety_notes": self.safety_notes,
        }


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _load_registry(repo_root: str | Path = ".", template_path: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root).expanduser().resolve()
    path = root / (template_path or _DEFAULT_TEMPLATE_PATH)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return _BUNDLED_REGISTRY


def _score_professions(text: str) -> tuple[str, list[str], float]:
    scores: dict[str, list[str]] = {}
    for profession, keywords in _PROFESSION_KEYWORDS.items():
        matches = [kw for kw in keywords if kw in text]
        if matches:
            scores[profession] = matches

    if not scores:
        return "software_builder", [], 0.25

    profession, matches = max(scores.items(), key=lambda item: (len(item[1]), len(" ".join(item[1]))))
    confidence = min(0.95, 0.35 + (0.10 * len(matches)))
    return profession, matches, round(confidence, 2)


def _detect_input_mode(text: str, profession_entry: dict[str, Any]) -> str:
    allowed_modes = profession_entry.get("input_modes", []) or ["prompt"]
    for mode, keywords in _INPUT_MODE_KEYWORDS.items():
        if mode in allowed_modes and any(keyword in text for keyword in keywords):
            return mode
    if "creative" in allowed_modes and any(word in text for word in ("quiero", "imagina", "haz")):
        return "creative"
    return allowed_modes[0]


def _choose_output_contract(text: str, profession_entry: dict[str, Any], input_mode: str) -> str:
    contracts = profession_entry.get("output_contracts", []) or ["plan"]
    if any(word in text for word in ("simula", "simular", "simulacion", "simulación", "onda", "frecuencia")):
        for preferred in ("simulation_plan", "model_explanation", "experiment_protocol"):
            if preferred in contracts:
                return preferred
    if any(word in text for word in ("clase", "curso", "university", "universidad", "aprender")):
        for preferred in ("learning_module", "lesson_plan", "student_path"):
            if preferred in contracts:
                return preferred
    if input_mode in ("image", "screenshot"):
        for preferred in ("art_brief", "layout_spec", "model_explanation"):
            if preferred in contracts:
                return preferred
    if input_mode == "audio":
        for preferred in ("mix_notes", "arrangement_plan", "simulation_plan"):
            if preferred in contracts:
                return preferred
    return contracts[0]


def _safety_notes(text: str, profession: str) -> list[str]:
    notes: list[str] = []
    if profession == "scientist_lab":
        notes.append("Separate known physics, simulation, hypothesis, and creative speculation.")
    if any(keyword in text for keyword in _HIGH_STAKES_KEYWORDS):
        notes.extend([
            "Biomedical or medical language detected: keep this educational/simulation-only.",
            "Do not diagnose, prescribe, claim cures, or replace clinical judgment.",
            "Prefer visual models, variables, measurements, and explicit limits.",
        ])
    return notes


def route_profession(request: str, repo_root: str | Path = ".", *, template_path: str | Path | None = None) -> ProfessionRoute:
    """Route a human request into a profession-aware Kodex lane."""
    registry = _load_registry(repo_root, template_path)
    text = _normalize(request)
    profession_id, matched_keywords, confidence = _score_professions(text)

    professions = {entry["id"]: entry for entry in registry.get("professions", [])}
    profession_entry = professions.get(profession_id)
    if profession_entry is None:
        profession_entry = {entry["id"]: entry for entry in _BUNDLED_REGISTRY["professions"]}[profession_id]

    input_mode = _detect_input_mode(text, profession_entry)
    output_contract = _choose_output_contract(text, profession_entry, input_mode)
    safety_notes = _safety_notes(text, profession_id)

    return ProfessionRoute(
        profession=profession_id,
        profession_name=profession_entry.get("name", profession_id),
        input_mode=input_mode,
        output_contract=output_contract,
        confidence=confidence,
        matched_keywords=matched_keywords,
        experiments=profession_entry.get("experiments", []),
        blackmamba_university_modules=profession_entry.get("blackmamba_university_modules", []),
        safe_actions=profession_entry.get("safe_actions", []),
        blocked_actions=profession_entry.get("blocked_actions", []),
        safety_notes=safety_notes,
    )


def route_profession_dict(request: str, repo_root: str | Path = ".") -> dict[str, Any]:
    """Dict-returning helper for CLI/API callers."""
    return route_profession(request, repo_root).to_dict()
