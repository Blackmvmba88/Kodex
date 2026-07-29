#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== Kodex verify =="
echo "repo: $ROOT"

echo "\n== Python package =="
python -m pip install -e ".[dev]"

echo "\n== Tests =="
pytest

echo "\n== Kodex snapshot =="
kodex snapshot

echo "\n== Kodex clean preview =="
kodex clean

echo "\n== Kodex diff guard =="
kodex diff .

echo "\n== Git status =="
git status --short --untracked-files=all

echo "\n== Verify complete =="
