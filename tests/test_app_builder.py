from agent.app_builder import build_app


def test_build_app_preview_uses_noop_provider(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / "README.md").write_text("# Demo App\n\n- Build CLI\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    result = build_app(tmp_path, task="Implement MVP", provider="noop")

    assert result["mode"] == "app_builder_preview"
    assert result["provider"] == "noop"
    assert result["ok"] is True
    assert result["status"] == "ready_for_review"
    assert "generated/implement-mvp.md" in result["generation"]["files"]
    assert result["write_plan"]["allowed"] is True


def test_build_app_rejects_unknown_provider(tmp_path):
    try:
        build_app(tmp_path, provider="missing")
    except ValueError as exc:
        assert "unknown provider" in str(exc)
    else:
        raise AssertionError("expected ValueError")
