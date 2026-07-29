# Kodex

Kodex is the BlackMamba Dev Agent: a safety-first Python CLI for inspecting repositories, planning changes, virtualizing execution, applying guarded patches, running checks, and preparing work for human-reviewed commits.

## Autonomous Loop v0.1

Kodex can now persist an execution run and recover its safe next action:

```text
task
  -> inspect / virtualize
  -> orchestrate
  -> optional guarded ship
  -> persist state in .kodex/runs
  -> stop at ready_for_commit
  -> review / resume
```

The v0.1 boundary is intentional: Kodex does not commit, push, open pull requests, or merge by itself. External integrations can perform those actions after review.

## Commands

```bash
kodex scan .
kodex status .
kodex doctor .
kodex checks .
kodex virtualize "add smoke test"
kodex orchestrate "add smoke test"
kodex auto "add smoke test"
kodex auto "add smoke test" --apply
kodex resume <run-id>
```

Existing guarded write flow:

```bash
kodex patch "create README"
kodex ship "add smoke test" --branch
```

## Persistent Run State

Each autonomous run is stored under:

```text
.kodex/runs/run-<id>.json
```

State records include the task, phase, status, branch, changed files, checks, commit/PR placeholders, timestamps, and any captured error.

Recovery is conservative. A run interrupted during a mutating phase is never blindly replayed; Kodex asks the caller to inspect the worktree before retrying.

## Safety Model

Kodex follows a few hard rules:

- keep changes small and reversible
- block shipping from a dirty worktree
- virtualize before mutating when possible
- run detected project checks
- inspect diffs for risky changes
- persist execution state before and after major phases
- stop before external GitHub actions unless an integration explicitly performs them

## Stack

- Python
- Typer CLI
- pytest
- GitHub Actions

## Development

```bash
pytest
```

The autonomous-loop implementation lives in `agent/autonomous.py`; persisted state is handled by `agent/run_state.py`.
