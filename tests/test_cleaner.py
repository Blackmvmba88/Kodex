from agent.cleaner import clean_repo, find_clean_targets


def test_find_clean_targets_detects_generated_artifacts(tmp_path):
    (tmp_path / "agent" / "__pycache__").mkdir(parents=True)
    (tmp_path / ".pytest_cache").mkdir()
    (tmp_path / "blackmamba_kodex.egg-info").mkdir()
    (tmp_path / ".venv").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "src.py").write_text("print('keep')\n", encoding="utf-8")

    targets = find_clean_targets(tmp_path)

    assert "agent/__pycache__" in targets
    assert ".pytest_cache" in targets
    assert "blackmamba_kodex.egg-info" in targets
    assert ".venv" not in targets
    assert "node_modules" not in targets
    assert "src.py" not in targets


def test_clean_repo_preview_does_not_remove(tmp_path):
    cache = tmp_path / "__pycache__"
    cache.mkdir()

    result = clean_repo(tmp_path)

    assert result["mode"] == "preview"
    assert result["targets"] == ["__pycache__"]
    assert result["removed"] == []
    assert cache.exists()


def test_clean_repo_apply_removes_only_targets(tmp_path):
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    keep = tmp_path / "src.py"
    keep.write_text("print('keep')\n", encoding="utf-8")

    result = clean_repo(tmp_path, apply=True)

    assert result["mode"] == "apply"
    assert result["removed"] == ["__pycache__"]
    assert not cache.exists()
    assert keep.exists()
