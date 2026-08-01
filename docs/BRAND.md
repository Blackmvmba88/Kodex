# Kodex Brand System

Kodex should not feel like a generic developer tool.

Kodex is the BlackMamba engineering agent: dark, precise, controlled, dangerous only to bad workflows.

The product should feel like:

```text
terminal-native
premium
sharp
safe
local-first
agentic
```

## Brand sentence

> Kodex is the local-first engineering agent that turns specs into safe, reviewable code changes.

## Emotional target

When someone sees Kodex, they should think:

```text
I can trust this in my repo.
I understand what it will do.
I want to run the dry-run.
I want to see what it builds.
I need this between me and AI-generated code.
```

## Visual identity

### Core palette

| Role | Name | Hex | Use |
|---|---:|---:|---|
| Background | Mamba Black | `#050608` | Main UI, terminal background, docs hero |
| Surface | Scale Graphite | `#101418` | Cards, panels, code blocks |
| Primary | Venom Green | `#39FF88` | Success, active state, primary accent |
| Secondary | Cyan Fang | `#00D5FF` | Links, info, secondary actions |
| Warning | Amber Venom | `#FFB020` | Caution, review needed |
| Danger | Blood Ruby | `#FF3B5C` | Blocked, unsafe, failed checks |
| Text | Bone White | `#F4F7F8` | Primary text |
| Muted Text | Smoke Gray | `#8A949E` | Secondary text |

### Optional premium accents

| Name | Hex | Use |
|---|---:|---|
| Serpent Purple | `#8A5CFF` | AI/provider moments |
| Gold Signal | `#FFD166` | Milestones, release moments |
| Deep Emerald | `#00A86B` | Brand gradients |

## Gradients

Primary hero gradient:

```css
background: radial-gradient(circle at top left, #123524 0%, #050608 45%, #000000 100%);
```

Venom edge:

```css
background: linear-gradient(135deg, #39FF88 0%, #00D5FF 100%);
```

Dark glass card:

```css
background: rgba(16, 20, 24, 0.86);
border: 1px solid rgba(57, 255, 136, 0.18);
box-shadow: 0 0 40px rgba(57, 255, 136, 0.08);
```

## Typography direction

Kodex should use fonts that feel technical but not cheap.

Recommended pairings:

| Purpose | Style |
|---|---|
| Logo / hero | sharp geometric sans |
| UI text | clean sans |
| CLI/code | strong monospace |

Open-source-friendly options:

- `JetBrains Mono` for CLI/code screenshots
- `Inter` or `Space Grotesk` for UI/docs
- `IBM Plex Mono` for terminal-first assets

## CLI personality

The CLI should feel calm, structured, and powerful.

Avoid noisy logs.

Prefer blocks like:

```text
KODEX WRITE MODE
────────────────
status      dry_run_ready
repo        /Users/you/project
branch      kodex/implement-mvp
provider    noop
files       3 candidate changes
mutation    none

next
  kodex app-build 'Implement MVP' --path '/Users/you/project' --apply
```

## Status language

Use consistent product states:

| State | Meaning |
|---|---|
| `preview_ready` | model/context plan is ready, no mutation |
| `dry_run_ready` | full non-mutating simulation complete |
| `blocked_dirty_worktree` | refuses unsafe repo state |
| `blocked_on_main` | refuses direct main write |
| `write_plan_rejected` | generated plan violates policy |
| `ready_for_commit` | safe local work complete, human should review |
| `checks_failed` | apply happened but validation failed |

## Product screens / future UI

A future Kodex UI should have three main cards:

```text
1. Understand
   repo map, spec summary, detected stack

2. Simulate
   write plan, files, risk, policy gates

3. Apply
   checkpoint, written files, checks, repair, ready_for_commit
```

## README hero structure

The README should sell Kodex in this order:

1. What it is.
2. Why random AI codegen is dangerous.
3. What Kodex does differently.
4. The 3-command wow path.
5. Safety guarantees.
6. Real command reference.
7. Roadmap.

## Screenshots / demo assets

Needed visual assets:

- terminal screenshot: `kodex app-build "Implement MVP" --dry-run`
- terminal screenshot: `blocked_on_main`
- terminal screenshot: `ready_for_commit`
- diagram: preview → dry-run → apply → ready_for_commit
- product logo: black mamba serpent + terminal cursor
- social card: dark background + venom green command

## Logo direction

Kodex mark:

```text
black mamba head
subtle circuit/terminal geometry
small cursor/fang motif
venom green eye or accent
```

Avoid cartoon snake.
Avoid generic AI brain.
Avoid corporate blue SaaS look.

## Voice

Kodex voice should be:

```text
confident
precise
human
not hype-only
not fake magical
```

Good:

> Preview complete. No files were changed.

Good:

> Write plan rejected: generated files exceeded policy limits.

Good:

> Ready for commit. Review the diff before continuing.

Bad:

> I fixed everything automatically!

Bad:

> Pushing to main...

## Taglines

- `Build with AI. Commit with control.`
- `The safe control plane for AI-generated code.`
- `From spec to reviewable diff.`
- `Local-first. Policy-guarded. Human-approved.`
- `A careful agent for dangerous work.`

## Product promise

Kodex should be lovable because it gives power without stealing control.

It should be needed because once someone trusts this workflow, raw AI code generation feels reckless.
