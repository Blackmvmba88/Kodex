from __future__ import annotations

"""Non-mutating product demos for Kodex.

The demo command is intentionally safe and deterministic. It does not scan a
real repository, write files, create checkpoints, call providers, or run checks.
It shows the product contract in a way a human can understand quickly.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent.profession_router import route_profession_dict


_DEFAULT_REQUESTS: dict[str, str] = {
    "sine": "quiero una onda sinusoidal",
    "app": "turn this README into an app with tests",
    "music": "analiza esta cancion por BPM flow silabas y dificultad",
    "biomed": "ver la piel como malla de Blender con vertices aristas y caras",
}


@dataclass(frozen=True)
class DemoPacket:
    name: str
    title: str
    request: str
    mutation: str
    route: dict[str, Any]
    flow: list[dict[str, str]]
    commands: list[str]
    promise: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "title": self.title,
            "request": self.request,
            "mutation": self.mutation,
            "route": self.route,
            "flow": self.flow,
            "commands": self.commands,
            "promise": self.promise,
        }


def available_demos() -> list[str]:
    """Return the stable list of bundled demo names."""
    return sorted(_DEFAULT_REQUESTS)


def build_demo_packet(
    name: str = "sine",
    *,
    repo_root: str | Path = ".",
    request: str | None = None,
) -> dict[str, Any]:
    """Build a non-mutating demo packet.

    Args:
        name: Bundled demo key. Use ``available_demos()`` to inspect options.
        repo_root: Repository path containing the profession template registry.
        request: Optional custom request. When supplied, it overrides the bundled
            request while preserving the demo shape.
    """
    demo_name = name.strip().lower()
    if request is None and demo_name not in _DEFAULT_REQUESTS:
        raise KeyError(f"unknown demo: {name}. available demos: {', '.join(available_demos())}")

    selected_request = request or _DEFAULT_REQUESTS[demo_name]
    route = route_profession_dict(selected_request, repo_root)
    command_request = selected_request.replace("'", "'\\''")

    packet = DemoPacket(
        name=demo_name,
        title="Kodex Product Demo — no mutation, pure intent routing",
        request=selected_request,
        mutation="none",
        route=route,
        flow=[
            {
                "step": "input",
                "status": "received",
                "meaning": "A human asks in natural language.",
            },
            {
                "step": "profession_route",
                "status": route["profession"],
                "meaning": "Kodex chooses a human lane before generating output.",
            },
            {
                "step": "input_mode",
                "status": route["input_mode"],
                "meaning": "Kodex selects how the request should be treated.",
            },
            {
                "step": "output_contract",
                "status": route["output_contract"],
                "meaning": "Kodex returns a safe contract instead of a generic answer.",
            },
            {
                "step": "mutation_boundary",
                "status": "none",
                "meaning": "Demo mode never writes files, checkpoints, or run metadata.",
            },
        ],
        commands=[
            f"kodex profession '{command_request}'",
            f"kodex demo --name {demo_name}",
            "kodex app-build 'Implement MVP' --dry-run",
        ],
        promise=[
            "local-first",
            "input-mode aware",
            "profession-aware",
            "preview before mutation",
            "dry-run means no writes",
            "human decides before commit/push",
        ],
    )
    return packet.to_dict()
