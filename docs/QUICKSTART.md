# Kodex Quickstart

This is the shortest path to feel why Kodex matters.

## 1. Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 2. Ask Kodex to understand the repo

```bash
kodex scan .
kodex snapshot
```

You are not asking it to write yet.

You are asking:

```text
Do you understand where you are?
Do you know the stack?
Do you know the risks?
```

## 3. Preview an app build

```bash
kodex app-build "Implement MVP"
```

This should produce a candidate build plan without writing files.

Expected feeling:

```text
Kodex understands the task.
Kodex found project context.
Kodex generated candidate files.
Kodex validated the write plan.
Nothing changed yet.
```

## 4. Run a real dry-run

```bash
kodex app-build "Implement MVP" --dry-run
```

Dry-run means zero repo mutation.

No generated files.
No checkpoints.
No run-state files.
No pytest cache.
No hidden metadata.

Just a simulation and a safe next command.

## 5. Apply from a task branch

Kodex should not write directly on `main`.

Create a task branch:

```bash
git checkout -b kodex/implement-mvp
```

Then apply:

```bash
kodex app-build "Implement MVP" --apply
```

Kodex should now:

```text
validate worktree
validate branch
compile spec
build context
generate files
validate write plan
create checkpoint
apply files
run configured checks
attempt repair if allowed
stop at ready_for_commit
```

## 6. Review like a human

```bash
git status
git diff
pytest
```

Then decide:

```bash
git add <files>
git commit -m "kodex: implement mvp"
```

Kodex does not steal the final decision.

That is the point.

## Common outcomes

### `blocked_on_main`

Kodex refused to write directly on `main`.

Fix:

```bash
git checkout -b kodex/my-task
kodex app-build "Implement MVP" --apply
```

### `blocked_dirty_worktree`

Kodex refused to write because uncommitted files already exist.

Fix:

```bash
git status
```

Then commit, stash, or clean intentionally.

### `dry_run_ready`

Kodex completed a non-mutating simulation.

This is good.

### `ready_for_commit`

Kodex completed local guarded write mode and stopped before commit.

This is the golden path.

## The 3-command demo

```bash
kodex app-build "Implement MVP"
kodex app-build "Implement MVP" --dry-run
git checkout -b kodex/implement-mvp && kodex app-build "Implement MVP" --apply
```

That is the Kodex ritual:

```text
preview
simulate
apply safely
```
