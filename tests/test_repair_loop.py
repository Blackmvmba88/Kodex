from agent.providers.base import ProviderRequest, ProviderResult
from agent.repair_loop import run_repair_loop


class RepairingProvider:
    name = "repairing"

    def generate(self, request: ProviderRequest) -> ProviderResult:
        if request.attempt == 0:
            return ProviderResult(
                ok=True,
                message="unsafe first attempt",
                files={".env": "SECRET=value\n"},
            )

        assert request.feedback
        return ProviderResult(
            ok=True,
            message="safe repaired attempt",
            files={"src/app.py": "def main():\n    return 'ok'\n"},
        )


def test_repair_loop_retries_with_policy_feedback(tmp_path):
    result = run_repair_loop(
        task="Implement MVP",
        context={"repo": {"name": "demo"}},
        provider=RepairingProvider(),
        repo_root=tmp_path,
        max_attempts=1,
    )

    assert result["ok"] is True
    assert result["status"] == "ready_for_review"
    assert result["attempt_count"] == 2
    assert result["history"][0]["accepted"] is False
    assert result["history"][1]["accepted"] is True
    assert "src/app.py" in result["generation"]["files"]


def test_repair_loop_rejects_negative_attempts(tmp_path):
    try:
        run_repair_loop(
            task="Implement MVP",
            context={},
            provider=RepairingProvider(),
            repo_root=tmp_path,
            max_attempts=-1,
        )
    except ValueError as exc:
        assert "cannot be negative" in str(exc)
    else:
        raise AssertionError("expected ValueError")
