from agent.generated_patch import prepare_generated_patch
from agent.providers.base import ProviderResult


def test_generated_patch_accepts_safe_files(tmp_path):
    generation = ProviderResult(
        ok=True,
        message="generated",
        files={"src/app.py": "print('ok')\n"},
    )

    packet = prepare_generated_patch(tmp_path, generation)

    assert packet["ready"] is True
    assert packet["allowed"] is True
    assert packet["files"] == generation.files


def test_generated_patch_blocks_sensitive_paths(tmp_path):
    generation = ProviderResult(
        ok=True,
        message="generated",
        files={".env": "SECRET=value\n"},
    )

    packet = prepare_generated_patch(tmp_path, generation)

    assert packet["ready"] is False
    assert packet["allowed"] is False
    assert any("blocked sensitive" in reason for reason in packet["reasons"])
