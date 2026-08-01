# AGENTS.md

## Rules for Kodex

- Inspect before editing.
- Prefer smallest safe change.
- Write tests for new behavior.
- Never modify secrets.
- Never push without approval.
- Do not work directly on `main` unless explicitly allowed.
- Stop at `ready_for_commit`.

## Project conventions

- Python modules live under `agent/`.
- Tests live under `tests/`.
- CLI commands are wired in `agent/main.py`.
- Use JSON output for machine-readable commands.
- Commit messages use `kodex: <task>`.
