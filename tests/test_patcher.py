from agent.patcher import apply_patch, propose_patch



def test_propose_patch_readme(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    proposal = propose_patch("create README", tmp_path)

    assert "README.md" in proposal["files"]
    assert proposal["mode"] == "proposal"



def test_apply_patch_smoke_test(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    result = apply_patch("add smoke test", tmp_path)

    assert result["write_result"]["allowed"] is True
    assert result["write_result"]["written"]
    written_file = result["write_result"]["written"][0]
    assert written_file.startswith("tests/test_")
    assert (tmp_path / written_file).exists()



def test_apply_patch_smoke_test_uses_new_filename_when_existing(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_demo_smoke.py").write_text("def test_demo_smoke():\n    assert True\n", encoding="utf-8")

    result = apply_patch("add smoke test", tmp_path)

    assert result["write_result"]["allowed"] is True
    assert result["write_result"]["written"] == ["tests/test_demo_smoke_2.py"]
    assert (tmp_path / "tests/test_demo_smoke_2.py").exists()
