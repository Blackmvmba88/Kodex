from __future__ import annotations

"""Capability catalog for Kodex input modes and profession lanes."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModeInfo:
    id: str
    name: str
    purpose: str
    example: str
    safe_boundary: str

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "purpose": self.purpose,
            "example": self.example,
            "safe_boundary": self.safe_boundary,
        }


_INPUT_MODES: tuple[ModeInfo, ...] = (
    ModeInfo(
        id="prompt",
        name="Prompt",
        purpose="Route a direct natural-language request into a safe output contract.",
        example="kodex profession 'quiero una onda sinusoidal'",
        safe_boundary="No mutation; intent routing only.",
    ),
    ModeInfo(
        id="spec",
        name="Spec",
        purpose="Use README/SPEC/AGENTS style documents as the source of truth.",
        example="kodex app-build 'Implement MVP' --dry-run",
        safe_boundary="Preview/dry-run before write mode.",
    ),
    ModeInfo(
        id="repo",
        name="Repo",
        purpose="Inspect a repository before planning or applying changes.",
        example="kodex scan .",
        safe_boundary="Read-only scan unless a guarded command is explicitly used.",
    ),
    ModeInfo(
        id="file",
        name="File",
        purpose="Use one artifact as focused context for a change or explanation.",
        example="kodex patch 'update this README'",
        safe_boundary="Write plans are validated before applying.",
    ),
    ModeInfo(
        id="screenshot",
        name="Screenshot",
        purpose="Turn a terminal/UI/image capture into diagnosis, design notes, or a plan.",
        example="kodex profession 'screenshot de error en terminal'",
        safe_boundary="Observation first; no destructive action.",
    ),
    ModeInfo(
        id="audio",
        name="Audio",
        purpose="Route music/audio/BPM/voice requests into producer or science workflows.",
        example="kodex profession 'analiza esta cancion por BPM y flow'",
        safe_boundary="No publishing or overwriting masters without explicit approval.",
    ),
    ModeInfo(
        id="creative",
        name="Creative",
        purpose="Handle signature BlackMamba requests without repeating generic templates.",
        example="kodex profession 'hazlo epico, quiero una onda sinusoidal'",
        safe_boundary="Never repeat; always mutate; always elevate, while staying explicit about safety.",
    ),
    ModeInfo(
        id="demo",
        name="Demo",
        purpose="Show Kodex safely before touching a real project.",
        example="kodex demo",
        safe_boundary="No repo scan, no writes, no providers, no checks.",
    ),
)

_PROFESSION_LANES: tuple[ModeInfo, ...] = (
    ModeInfo(
        id="software_builder",
        name="Software Builder",
        purpose="Build, test, patch, repair, and prepare software changes safely.",
        example="kodex app-build 'Implement MVP' --dry-run",
        safe_boundary="Stops before commit/push/PR unless explicitly handled elsewhere.",
    ),
    ModeInfo(
        id="music_producer",
        name="Music Producer",
        purpose="Transform song, lyric, audio, release, and visual-music requests into useful packets.",
        example="kodex profession 'haz una letra en mi formato'",
        safe_boundary="No publish/overwrite actions without confirmation.",
    ),
    ModeInfo(
        id="visual_artist",
        name="Visual Artist",
        purpose="Convert image, cover, brand, and video ideas into reusable visual briefs.",
        example="kodex profession 'portada BlackMamba con colores premium'",
        safe_boundary="No destructive edits to source art by default.",
    ),
    ModeInfo(
        id="scientist_lab",
        name="Scientist / Lab",
        purpose="Turn physics, math, simulation, resonance, waveform, and biomedical ideas into safe labs.",
        example="kodex profession 'ver la piel como malla de Blender'",
        safe_boundary="Educational/simulation-only for medical or high-stakes domains.",
    ),
    ModeInfo(
        id="educator",
        name="Educator",
        purpose="Convert work into lessons, quizzes, rubrics, student projects, and portfolio artifacts.",
        example="kodex profession 'convierte esto en clase BlackMamba University'",
        safe_boundary="Avoid fabricated sources or high-stakes grading without context.",
    ),
)

_BMU_LABS: tuple[ModeInfo, ...] = (
    ModeInfo(
        id="waveforms_and_sound",
        name="Waveforms and Sound",
        purpose="Sine waves, harmonics, resonance, audio, Fourier thinking, and visual simulation.",
        example="quiero una onda sinusoidal",
        safe_boundary="Separate known physics, simulation, hypothesis, and creative speculation.",
    ),
    ModeInfo(
        id="biomedical_tissue_simulation",
        name="Biomedical Tissue Simulation",
        purpose="Model skin/tissue as educational mesh geometry: vertices, edges, faces, modules.",
        example="ver la piel como malla de Blender",
        safe_boundary="No diagnosis, treatment, or cure claims.",
    ),
    ModeInfo(
        id="safe_ai_building",
        name="Safe AI Building",
        purpose="Teach preview, dry-run, checkpoints, checks, and human approval boundaries.",
        example="turn this README into an app with tests",
        safe_boundary="Never auto-commit, auto-push, or merge without human review.",
    ),
)


def build_modes_catalog() -> dict[str, Any]:
    """Return the stable Kodex capability catalog."""
    return {
        "product": "Kodex",
        "tagline": "BlackMamba local-first builder agent",
        "input_modes": [mode.to_dict() for mode in _INPUT_MODES],
        "profession_lanes": [lane.to_dict() for lane in _PROFESSION_LANES],
        "blackmamba_university_labs": [lab.to_dict() for lab in _BMU_LABS],
        "try_next": [
            "kodex demo",
            "kodex profession 'quiero una onda sinusoidal'",
            "kodex app-build 'Implement MVP' --dry-run",
        ],
    }
