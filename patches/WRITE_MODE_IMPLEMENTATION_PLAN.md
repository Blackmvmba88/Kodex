# Write Mode Implementation Plan

## New modules

```txt
agent/write_policy.py
agent/checkpoint.py
agent/generated_patcher.py
agent/write_mode.py
tests/test_write_policy.py
tests/test_checkpoint.py
tests/test_generated_patcher.py
tests/test_write_mode.py
```

## Proposed command

```bash
kodex app-build "Implement MVP" --apply
```

## Required behavior

- Refuse dirty worktree.
- Refuse direct `main` unless override is explicit.
- Validate generated files through approval rules.
- Save checkpoint under `.kodex/checkpoints/`.
- Apply files.
- Run checks.
- Diagnose failures.
- Attempt repair loop if configured.
- Stop at ready_for_commit.

## Output contract

```json
{
  "status": "ready_for_commit",
  "ok": true,
  "checkpoint": ".kodex/checkpoints/<id>.json",
  "written": [],
  "checks": [],
  "diagnosis": null,
  "repair_attempts": [],
  "next_commands": []
}
```
