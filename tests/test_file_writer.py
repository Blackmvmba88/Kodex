from agent.file_writer import write_files


def test_write_files_creates_file(tmp_path):
    result = write_files(tmp_path, {"docs/hello.md": "hello\n"})

    assert result["allowed"] is True
    assert result["written"] == ["docs/hello.md"]
    assert (tmp_path / "docs" / "hello.md").read_text() == "hello\n"


def test_write_files_does_not_write_blocked_file(tmp_path):
    result = write_files(tmp_path, {".env": "SECRET=1\n"})

    assert result["allowed"] is False
    assert result["written"] == []
    assert not (tmp_path / ".env").exists()
