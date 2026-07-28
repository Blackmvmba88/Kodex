from __future__ import annotations

import json
from pathlib import Path

from agent.repo_scanner import scan_repo


def test_scan_python_repo(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")

    result = scan_repo(tmp_path)

    assert result["name"] == tmp_path.name
    assert "python" in result["stack"]
    assert "main.py" in result["entrypoints"]
    assert "tests" in result["tests"]
    assert result["commands"]["test"] == "pytest"


def test_scan_node_repo_detects_scripts(tmp_path: Path) -> None:
    package = {
        "scripts": {
            "dev": "vite",
            "test": "vitest run",
            "build": "vite build",
        }
    }
    (tmp_path / "package.json").write_text(json.dumps(package), encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "App.tsx").write_text("export default function App() { return null }\n", encoding="utf-8")

    result = scan_repo(tmp_path)

    assert "node" in result["stack"]
    assert "src/App.tsx" in result["entrypoints"]
    assert result["commands"]["dev"] == "npm run dev"
    assert result["commands"]["test"] == "npm run test"
    assert result["commands"]["build"] == "npm run build"
