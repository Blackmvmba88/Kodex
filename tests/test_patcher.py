from pathlib import Path

from agent.patcher import apply_patch, propose_patch


def _is_smoke_test_path(path: str) -> bool:
    candidate = Path(path)
    return (
        len(candidate.parts) == 2
        and candidate.parts[0] == "tests"
        and candidate.name.startswith("test_")
        and "_smoke" in candidate.stem
        and candidate.suffix == ".py"
    )


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
    assert _is_smoke_test_path(written_file)
    assert (tmp_path / written_file).exists()


def test_apply_patch_smoke_test_uses_new_filename_when_existing(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    first = apply_patch("add smoke test", tmp_path)
    second = apply_patch("add smoke test", tmp_path)

    first_file = first["write_result"]["written"][0]
    second_file = second["write_result"]["written"][0]

    assert first_file != second_file
    assert _is_smoke_test_path(second_file)
    assert (tmp_path / second_file).exists()
