from agent.spec_compiler import compile_spec


def test_compile_spec_reads_sources_and_requirements(tmp_path):
    (tmp_path / "README.md").write_text("# Demo App\n\n- Build CLI\n- Add tests\n", encoding="utf-8")
    (tmp_path / "SPEC.md").write_text("# Spec\n\n- Persist runs\n", encoding="utf-8")

    spec = compile_spec(tmp_path, task="Implement MVP")

    assert spec.task == "Implement MVP"
    assert spec.title == "Source: README.md"
    assert "README.md" in spec.sources
    assert "SPEC.md" in spec.sources
    assert "AGENTS.md" in spec.missing_sources
    assert "Build CLI" in spec.requirements
    assert "Persist runs" in spec.requirements


def test_compile_spec_handles_missing_sources(tmp_path):
    spec = compile_spec(tmp_path, task="Build from empty repo")

    assert spec.sources == []
    assert spec.missing_sources == ["README.md", "SPEC.md", "AGENTS.md"]
    assert spec.body == ""
