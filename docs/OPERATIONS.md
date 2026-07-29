# Kodex Operations Manual

This document describes the safe day-to-day workflow for using Kodex.

## Golden workflow

Use this order when working on a task:

```bash
kodex clean
kodex snapshot
kodex virtualize "task description"
kodex orchestrate "task description"
kodex ship "task description" --branch
```

## Readiness rules

Kodex is ready to work when:

- `git` is clean
- `kodex snapshot` returns `ready: true`
- `kodex diff .` returns `safe: true`
- project checks are detected
- no blockers appear in `kodex virtualize`

## Human approval boundary

Kodex may prepare changes, but the human approves external actions.

Allowed before approval:

- scan
- snapshot
- virtualize
- orchestrate
- patch proposal
- local guarded ship
- diagnostics

Requires human approval:

- commit
- push
- PR creation
- merge
- destructive cleanup beyond generated artifacts
- any network publication

## Normal task flow

### 1. Check readiness

```bash
kodex snapshot
```

Expected result:

```json
{
  "ready": true,
  "status": "ready"
}
```

### 2. Simulate the task

```bash
kodex virtualize "create task note"
```

Use this to inspect predicted files, checks, branch, commit message, and blockers.

### 3. Ask the orchestrator

```bash
kodex orchestrate "create task note"
```

Use this to decide the safest next action.

### 4. Ship locally in a branch

```bash
kodex ship "create task note" --branch
```

If the result is `ready_for_commit`, review the generated `next_commands`.

### 5. Commit only after review

```bash
git add <files>
git commit -m "kodex: task message"
git push -u origin <branch>
```

## Failure reading guide

Do not read failures as panic. Read the phase.

```text
INSTALL -> pip, pyproject, dependencies
TEST    -> tests or contract mismatch
CLI     -> command not wired, reinstall needed
GIT     -> dirty tree, branch, push, checkout
PATCH   -> file path, blocked write, generated content
CHECKS  -> pytest, lint, build
DIFF    -> risky diff or suspicious content
```

Use diagnostics:

```bash
kodex diagnose "paste error text here"
```

Or from a log file:

```bash
kodex diagnose ./error.log --file
```

## Cleanup

Preview cleanup:

```bash
kodex clean
```

Apply cleanup:

```bash
kodex clean --apply
```

Only generated local artifacts should be removed.

## Recovery

If a run gets interrupted, inspect it:

```bash
kodex resume <run_id>
```

If Git is dirty, inspect first:

```bash
git status
kodex diff .
```

Do not force-reset unless the human explicitly approves it.
