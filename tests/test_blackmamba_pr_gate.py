from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "blackmamba_pr_gate.py"
SPEC = importlib.util.spec_from_file_location("blackmamba_pr_gate", MODULE_PATH)
assert SPEC and SPEC.loader
pr_gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pr_gate)


def test_classify_docs_only():
    pr = {"title": "docs: explain command loop", "user": {"login": "Blackmvmba88"}}
    assert pr_gate.classify_kind(pr, ["README.md", "docs/COMMAND_LOOP.md"]) == "docs"


def test_classify_tests_only():
    pr = {"title": "add regression coverage", "user": {"login": "Blackmvmba88"}}
    assert pr_gate.classify_kind(pr, ["tests/test_one.py", "tests/test_two.py"]) == "tests"


def test_classify_dependency_from_dependabot():
    pr = {"title": "Bump requests", "user": {"login": "dependabot[bot]"}}
    assert pr_gate.classify_kind(pr, ["requirements.txt"]) == "dependency"


def test_classify_runtime_change_as_code():
    pr = {"title": "improve supervisor", "user": {"login": "Blackmvmba88"}}
    assert pr_gate.classify_kind(pr, ["agent/supervisor.py", "tests/test_supervisor.py"]) == "code"


def test_file_overlap_uses_smaller_change_as_denominator():
    left = {"a.py", "b.py"}
    right = {"a.py", "b.py", "c.py", "d.py"}
    assert pr_gate.file_overlap(left, right) == 1.0


def test_file_overlap_zero_without_shared_files():
    assert pr_gate.file_overlap({"a.py"}, {"b.py"}) == 0.0


def test_title_similarity_ignores_generic_change_words():
    left = pr_gate.normalized_title_tokens("Optimize cosmetic slot validation")
    right = pr_gate.normalized_title_tokens("Improve cosmetic slot validation")
    assert pr_gate.jaccard(left, right) >= 0.5


def test_labels_for_ready_docs():
    result = pr_gate.Assessment(
        number=1,
        title="docs",
        kind="docs",
        state="READY",
        ci="none",
        unresolved_threads=0,
        review_decision=None,
        duplicate_prs=[],
        files=["README.md"],
        reasons=[],
    )
    assert pr_gate.labels_for(result) == ["bm:docs", "bm:ready"]


def test_labels_for_blocked_code():
    result = pr_gate.Assessment(
        number=2,
        title="runtime",
        kind="code",
        state="BLOCKED_CI",
        ci="failed",
        unresolved_threads=0,
        review_decision=None,
        duplicate_prs=[],
        files=["agent/runtime.py"],
        reasons=["tests: failure"],
    )
    assert pr_gate.labels_for(result) == ["bm:code", "bm:blocked-ci"]
