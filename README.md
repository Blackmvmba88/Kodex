# Kodex

**Kodex is a local-first engineering agent that can inspect a repository, plan a change, preview the work, safely write files, run checks, attempt repair, and stop before commit for human review.**

It is not a random code generator. It is the missing control plane between “AI can write code” and “I trust this thing inside my repo.”

```text
spec / README / task
        ↓
inspect repo
        ↓
preview plan
        ↓
dry-run without touching disk
        ↓
apply with checkpoint
        ↓
run configured checks
        ↓
repair loop if needed
        ↓
ready_for_commit
        ↓
human decides
```

Kodex exists for the moment when you want AI help, but you do **not** want an agent trashing your project, pushing broken code, or pretending it knows better than your workflow.

## Why you want this

Most coding agents optimize for output.

Kodex optimizes for **trust**.

It gives you a repeatable way to ask for changes while keeping the important boundaries intact:

- preview before mutation
- dry-run that does not write repo metadata
- guarded apply with policy limits
- checkpoints before real writes
- configurable checks
- repair loop hooks
- human approval before commit, push, PR, or merge

That makes Kodex useful both as a solo-dev superpower and as the safety layer for larger autonomous coding systems.

## The feeling

The ideal Kodex session should feel like this:

```bash
kodex app-build "Implement MVP" --dry-run
```

Kodex answers:

```text
I understand the repo.
I found the spec.
I know what files I would create.
I validated the write plan.
I touched nothing.
Run this when ready:
  kodex app-build 'Implement MVP' --path '/your/repo' --apply
```

Then:

```bash
kodex app-build "Implement MVP" --apply
```

Kodex writes safely, checks itself, and stops at:

```text
ready_for_commit
```

Not “surprise, I pushed to main.”

Not “good luck reading this diff.”

Not “I rewrote your whole app.”

A controlled builder. A careful engineer. A useful serpent.

## Input modes

Kodex should not feel like an empty chatbot box.

The product should give you clear doors into the work:

```text
Prompt       — describe what you want
Spec         — build from README.md / SPEC.md / AGENTS.md
Repo         — inspect the whole repository
File         — transform one focused file
Screenshot   — understand a UI, terminal, or visual state
Audio        — work from sound, waveform, BPM, voice, or signal intent
Creative     — expand a signature idea into a fresh artifact
Demo         — run a zero-risk built-in showcase
```

So a request like:

```text
quiero una onda sinusoidal
```

is not forced into one generic answer. Kodex can interpret it through a chosen mode:

```text
Prompt   → create a sine-wave module
Creative → make a fresh math/visual/audio artifact
Audio    → generate an oscillator or WAV export
Demo     → show a safe waveform showcase
```

The rule for signature creative requests:

```text
Never repeat.
Always mutate.
Always elevate.
```

## Command loop

Kodex now has a full non-mutating product loop from first-touch demo to final review gate:

```text
kodex demo
  → kodex modes
  → kodex guide
  → kodex lab
  → kodex course
  → kodex portfolio
  → kodex showcase
  → kodex review-gate
```

Read the full guide in [docs/COMMAND_LOOP.md](docs/COMMAND_LOOP.md).

## Quickstart

Install in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Preview a repo:

```bash
kodex scan .
kodex snapshot
kodex app-build "Implement MVP"
```

Run a non-mutating simulation:

```bash
kodex app-build "Implement MVP" --dry-run
```

Apply only from a safe task branch:

```bash
git checkout -b kodex/implement-mvp
kodex app-build "Implement MVP" --apply
```

Review before committing:

```bash
git status
git diff
pytest
git add <files>
git commit -m "kodex: implement mvp"
```

## Core commands

```bash
kodex scan .
kodex status .
kodex doctor .
kodex checks .
kodex virtualize "add smoke test"
kodex orchestrate "add smoke test"
kodex app-build "Implement MVP"
kodex app-build "Implement MVP" --dry-run
kodex app-build "Implement MVP" --apply
kodex auto "add smoke test"
kodex resume <run-id>
kodex release-check
kodex pr-summary "feat: add guarded write mode"
```

Existing guarded write flow:

```bash
kodex patch "create README"
kodex ship "add smoke test" --branch
```

## Write mode

Write mode is the heart of Kodex.

It follows this boundary:

```text
compile spec
→ build context
→ generate candidate files
→ validate write plan
→ checkpoint
→ apply files atomically
→ run configured checks
→ repair if allowed
→ stop before commit/push
```

Configuration lives in:

```text
configs/kodex_write_policy.json
```

Example checks block:

```json
{
  "checks": {
    "commands": [
      "python -m pytest -x -q --tb=short"
    ],
    "stop_on_failure": true,
    "timeout_seconds": 120
  }
}
```

## Safety model

Kodex follows hard rules:

- do not write from a dirty worktree
- do not write directly on `main` unless explicitly allowed
- do not touch blocked paths like `.git/`, `.env`, keys, virtualenvs, or generated caches
- validate write size and file count before applying
- checkpoint before real writes
- never auto-commit
- never auto-push
- never merge itself
- preserve human approval as the final authority

## Persistent run state

Autonomous runs are stored under:

```text
.kodex/runs/run-<id>.json
```

Write checkpoints are stored under:

```text
.kodex/checkpoints/ckpt-<id>.json
```

Both are local runtime artifacts and ignored by git.

## What Kodex is becoming

Today Kodex is a safe, orquestable engineering agent.

The next evolution is a full application factory:

```text
README.md + SPEC.md + AGENTS.md
        ↓
Spec Compiler
        ↓
Context Builder
        ↓
Provider
        ↓
Code Generator
        ↓
Guarded Write Mode
        ↓
Repair Loop
        ↓
ready_for_commit
```

The goal is simple:

> Make AI coding powerful enough to build real software, and disciplined enough to trust.

## Stack

- Python
- Typer CLI
- Rich JSON output
- Pydantic-ready architecture
- pytest
- GitHub Actions

## Development

```bash
pytest
```

For the product path, read:

```text
docs/QUICKSTART.md
docs/COMMAND_LOOP.md
docs/WHY_KODEX.md
docs/INPUT_MODES.md
docs/SIGNATURE_REQUESTS.md
docs/WRITE_MODE.md
```