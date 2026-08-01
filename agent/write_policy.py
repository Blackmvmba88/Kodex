from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


_DEFAULT_POLICY_PATH = Path("configs/kodex_write_policy.json")


@dataclass
class RepairPolicy:
    enabled: bool = True
    max_attempts: int = 3
    requires_diagnosis: bool = True
    requires_tests_after_each_attempt: bool = True


@dataclass
class ProviderPolicy:
    default: str = "noop"
    allowed: list[str] = field(default_factory=lambda: ["noop"])
    network_calls_enabled_by_default: bool = False


@dataclass
class WritePolicy:
    mode: str = "guarded_write"
    default_apply: bool = False
    require_clean_worktree: bool = True
    require_task_branch: bool = True
    allow_direct_main: bool = False
    require_checkpoint: bool = True
    require_write_plan_validation: bool = True
    max_files_per_write: int = 12
    max_bytes_per_file: int = 50_000
    max_total_bytes: int = 250_000
    blocked_paths: list[str] = field(default_factory=list)
    allowed_default_roots: list[str] = field(default_factory=list)
    always_stop_before: list[str] = field(default_factory=list)
    repair_loop: RepairPolicy = field(default_factory=RepairPolicy)
    providers: ProviderPolicy = field(default_factory=ProviderPolicy)

    # ------------------------------------------------------------------
    # Guard helpers
    # ------------------------------------------------------------------

    def is_blocked_path(self, relative_path: str) -> bool:
        """Return True if *relative_path* matches any entry in blocked_paths."""
        from fnmatch import fnmatch

        path_str = relative_path.replace("\\", "/")
        for pattern in self.blocked_paths:
            if fnmatch(path_str, pattern):
                return True
            # Also match path prefixes (e.g. "venv/" should block "venv/lib/x.py")
            if pattern.endswith("/") and path_str.startswith(pattern):
                return True
        return False

    def is_allowed_root(self, relative_path: str) -> bool:
        """Return True if *relative_path* starts with an allowed default root."""
        path_str = relative_path.replace("\\", "/")
        return any(path_str.startswith(root) for root in self.allowed_default_roots)


def load_write_policy(
    repo_root: str | Path = ".",
    policy_path: str | Path | None = None,
) -> WritePolicy:
    """Load *WritePolicy* from JSON; falls back to defaults if the file is absent."""
    root = Path(repo_root).expanduser().resolve()
    target = root / (policy_path or _DEFAULT_POLICY_PATH)

    if not target.exists():
        return WritePolicy()

    raw: dict = json.loads(target.read_text(encoding="utf-8"))

    repair_raw = raw.pop("repair_loop", {})
    providers_raw = raw.pop("providers", {})

    return WritePolicy(
        **{k: v for k, v in raw.items() if k in WritePolicy.__dataclass_fields__},
        repair_loop=RepairPolicy(**{k: v for k, v in repair_raw.items() if k in RepairPolicy.__dataclass_fields__}),
        providers=ProviderPolicy(**{k: v for k, v in providers_raw.items() if k in ProviderPolicy.__dataclass_fields__}),
    )
