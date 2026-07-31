from agent.providers.noop_provider import NoopProvider
from agent.repair_loop import run_repair_loop


def test_repair_loop_returns_candidate_repair_with_noop_provider():
    result = run_repair_loop(
        task="Implement MVP",
        context={"project": {"name": "demo"}},
        provider=NoopProvider(),
        failure_log="FAILED tests/test_demo.py::test_demo - assert False",
        max_attempts=1,
    )

    payload = result.to_context()
    assert payload["ok"] is True
    assert payload["status"] == "candidate_repair_ready"
    assert payload["attempts"][0]["diagnosis"]["phase"] == "TEST"
    assert payload["final_files"]


def test_repair_loop_can_be_disabled():
    result = run_repair_loop(
        task="Implement MVP",
        context={},
        provider=NoopProvider(),
        failure_log="FAILED tests/test_demo.py::test_demo - assert False",
        max_attempts=0,
    )

    assert result.ok is False
    assert result.status == "disabled"
    assert result.attempts == []
