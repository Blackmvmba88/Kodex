# Kodex Architecture

Kodex is a local-first development agent for BlackMamba workflows. It is designed to inspect a repository, plan a safe change, simulate the work, execute guarded local changes, and leave a human-readable commit or PR path.

## Core principle

Kodex does not start by writing code. It starts by reading the repository state.

```text
repo -> scan -> snapshot -> virtualize -> orchestrate -> branch -> ship -> review
```

## Main layers

### 1. Repository scanner

Module: `agent/repo_scanner.py`

Detects stack, entrypoints, tests, commands, and risks.

### 2. Memory

Module: `agent/memory.py`

Stores known project maps so Kodex can reuse previous repository context.

### 3. Planning

Module: `agent/task_planner.py`

Builds a safe implementation plan, suggested branch, commit message, likely files, and checks.

### 4. Snapshot

Module: `agent/snapshot.py`

Creates a compact readiness report:

- Git repository state
- dirty/clean worktree
- detected stack
- available checks
- diff safety
- readiness status

### 5. Virtualization

Module: `agent/virtualizer.py`

Simulates work without changing files, creating branches, committing, or pushing.

### 6. Orchestration

Module: `agent/orchestrator.py`

Decides the safest next step based on snapshot and virtualization results.

### 7. Branching

Module: `agent/brancher.py`

Creates safe task branches from a clean working tree.

### 8. Patching

Modules:

- `agent/approval.py`
- `agent/file_writer.py`
- `agent/patcher.py`

Proposes and applies guarded file writes. Blocks dangerous paths, secrets, virtualenvs, build artifacts, and traversal outside the repository.

### 9. Checks and diff guard

Modules:

- `agent/checks.py`
- `agent/diff_guard.py`

Runs detected test/build commands and reviews current changes for risky patterns.

### 10. Shipping

Module: `agent/shipper.py`

Applies the guarded patch, runs checks, inspects diff, and prepares commit/push commands. It does not push without human approval.

### 11. Diagnostics

Module: `agent/diagnostics.py`

Turns raw errors into structured reports with phase, reason, failed file, and suggested fix.

## Safety boundaries

Kodex should never:

- push without explicit approval
- commit secrets
- write outside the repository
- delete source files without explicit approval
- work directly on dirty state
- hide failing checks
- silently ignore diff warnings

## Current maturity

Kodex is currently a guarded local development assistant. It is not yet a fully autonomous production deployer.

The correct posture is:

```text
assist -> simulate -> explain -> prepare -> wait for approval
```
