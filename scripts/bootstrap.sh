#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .

echo "Kodex installed locally. Try:"
echo "  source .venv/bin/activate"
echo "  kodex doctor ."
echo "  kodex task 'add smoke tests' --repo Kodex"
