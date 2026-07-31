from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.git_ops import git_status
from agent.repo_scanner import scan_repo
from agent.spec_compiler import CompiledSpec


DEFAULT_CONTEXT_LIMITS = {
    "max_requirements": 30,
    "max_changed_files": 50,
}


def build_context(repo_root: str | Path, spec: CompiledSpec) -> dict[str, Any]:
    """Build the bounded repository context sent to code-generation providers."""
    root = Path(repo_root).expanduser().resolve()
    project = scan_repo(root)
    git = git_status(root)

    requirements = spec.requirements[: DEFAULT_CONTEXT_LIMITS["max_requirements"]]
    changed_files = git.get("changed_files", [])[: DEFAULT_CONTEXT_LIMITS["max_changed_files"]]

    return {
        "repo": {
            "name": project.get("name"),
            "path": str(root),
            "stack": project.get("stack", []),
            "entrypoints": project.get("entrypoints", []),
            "tests": project.get("tests", []),
            "commands": project.get("commands", {}),
            "risks": project.get("risks", []),
        },
        "git": {
            "is_git_repo": git.get("is_git_repo"),
            "branch": git.get("branch"),
            "dirty": git.get("dirty"),
            "changed_files": changed_files,
        },
        "spec": {
            "task": spec.task,
            "title": spec.title,
            "sources": spec.sources,
            "requirements": requirements,
            "missing_sources": spec.missing_sources,
        },
    }
