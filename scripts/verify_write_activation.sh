#!/usr/bin/env bash
set -euo pipefail

echo "== Kodex write activation verification =="

if [ ! -f "pyproject.toml" ]; then
  echo "WARN: pyproject.toml not found. Run this from the Kodex repo root."
fi

if command -v kodex >/dev/null 2>&1; then
  echo "kodex found:"
  kodex --help >/dev/null
  echo "  ok: CLI responds"
else
  echo "WARN: kodex command not found. Activate venv and run pip install -e '.[dev]'"
fi

if [ -f "configs/kodex_write_policy.json" ]; then
  python -m json.tool configs/kodex_write_policy.json >/dev/null
  echo "  ok: write policy JSON is valid"
else
  echo "WARN: configs/kodex_write_policy.json not found"
fi

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "  ok: git repository detected"
  git status --short
else
  echo "WARN: not inside a git repository"
fi

echo "done"
