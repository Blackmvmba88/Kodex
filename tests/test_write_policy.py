from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from agent.write_policy import WritePolicy, load_write_policy, RepairPolicy, ProviderPolicy


def _write_policy_json(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "configs" / "kodex_write_policy.json"
    p.parent.mkdir(parents=True)
    p.write_text(json.dumps(data), encoding="utf-8")
    return tmp_path


class TestWritePolicyDefaults:
    def test_default_policy_is_guarded(self):
        policy = WritePolicy()
        assert policy.mode == "guarded_write"
        assert policy.default_apply is False
        assert policy.require_clean_worktree is True
        assert policy.require_task_branch is True
        assert policy.allow_direct_main is False

    def test_default_max_files(self):
        policy = WritePolicy()
        assert policy.max_files_per_write == 12

    def test_blocked_path_dot_env(self):
        policy = WritePolicy(blocked_paths=[".env", "venv/"])
        assert policy.is_blocked_path(".env")
        assert policy.is_blocked_path("venv/lib/python3.12/site.py")
        assert not policy.is_blocked_path("agent/main.py")

    def test_allowed_root(self):
        policy = WritePolicy(allowed_default_roots=["agent/", "tests/"])
        assert policy.is_allowed_root("agent/foo.py")
        assert policy.is_allowed_root("tests/test_bar.py")
        assert not policy.is_allowed_root("secrets/token.txt")


class TestLoadWritePolicy:
    def test_loads_from_file(self, tmp_path):
        _write_policy_json(
            tmp_path,
            {
                "mode": "guarded_write",
                "default_apply": False,
                "require_clean_worktree": True,
                "require_task_branch": True,
                "allow_direct_main": False,
                "require_checkpoint": True,
                "require_write_plan_validation": True,
                "max_files_per_write": 5,
                "max_bytes_per_file": 1000,
                "max_total_bytes": 5000,
                "blocked_paths": [".env"],
                "allowed_default_roots": ["agent/"],
                "always_stop_before": ["git commit"],
                "repair_loop": {"enabled": True, "max_attempts": 2},
                "providers": {"default": "noop", "allowed": ["noop"]},
            },
        )
        policy = load_write_policy(tmp_path)
        assert policy.max_files_per_write == 5
        assert policy.repair_loop.max_attempts == 2
        assert policy.providers.default == "noop"

    def test_falls_back_to_defaults_when_missing(self, tmp_path):
        policy = load_write_policy(tmp_path)
        assert policy.mode == "guarded_write"
