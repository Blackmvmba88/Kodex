from agent.approval import review_write_plan


def test_approval_blocks_env_files(tmp_path):
    decision = review_write_plan(tmp_path, {".env": "SECRET=1\n"})

    assert decision.allowed is False
    assert any("sensitive" in reason for reason in decision.reasons)


def test_approval_blocks_path_escape(tmp_path):
    decision = review_write_plan(tmp_path, {"../outside.txt": "nope"})

    assert decision.allowed is False
    assert any("escapes" in reason for reason in decision.reasons)


def test_approval_allows_normal_file(tmp_path):
    decision = review_write_plan(tmp_path, {"docs/note.md": "hello"})

    assert decision.allowed is True
    assert decision.warnings
