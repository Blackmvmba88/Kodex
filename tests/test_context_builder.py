from agent.context_builder import build_context
from agent.spec_compiler import compile_spec


def test_build_context_includes_repo_git_and_spec(tmp_path):
    import subprocess

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    (tmp_path / "README.md").write_text("# Demo\n\n- Build CLI\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

    spec = compile_spec(tmp_path, task="Implement MVP")
    context = build_context(tmp_path, spec)

    assert context["repo"]["name"] == tmp_path.name
    assert "python" in context["repo"]["stack"]
    assert context["git"]["is_git_repo"] is True
    assert context["spec"]["task"] == "Implement MVP"
    assert "Build CLI" in context["spec"]["requirements"]
