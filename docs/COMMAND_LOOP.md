# Kodex command loop

Kodex now has a full non-mutating product loop that turns a human request into a routed intent, a guide packet, a lab packet, a course module, a portfolio artifact, a showcase kit, and a review gate.

This document explains the command order, what each command produces, and what it never does by default.

## Loop overview

```text
kodex demo
  -> kodex modes
  -> kodex guide
  -> kodex lab
  -> kodex course
  -> kodex portfolio
  -> kodex showcase
  -> kodex review-gate
```

In product language:

```text
first-touch product moment
  -> capability map
  -> safe next-step route
  -> teachable lab packet
  -> reusable course module
  -> portfolio evidence packet
  -> demo-ready showcase kit
  -> publish/review readiness gate
```

## Safety model

The command loop is intentionally non-mutating. These commands render deterministic packets and terminal views. They do not, by themselves:

- scan a repository
- call model providers
- write files
- run checks
- commit changes
- push branches
- open pull requests
- publish or upload content

Commands that can mutate a repository remain separate and explicit, such as guarded write/apply paths.

## Command map

| Command | Purpose | Output type | Default mutation |
| --- | --- | --- | --- |
| `kodex demo` | Show the premium first-touch product view. | Human terminal presentation | none |
| `kodex demo --json` | Render the demo packet for machines/tests. | JSON | none |
| `kodex modes` | Show input modes, profession lanes, and BlackMamba University labs. | Human terminal tables | none |
| `kodex modes --json` | Render the capability catalog. | JSON | none |
| `kodex guide "..."` | Route a request to a safe next command path. | Human terminal plan | none |
| `kodex guide "..." --json` | Render the guide packet. | JSON | none |
| `kodex lab "..."` | Turn a request into a teachable lab packet. | Human terminal packet | none |
| `kodex lab "..." --json` | Render the lab packet. | JSON | none |
| `kodex course "..."` | Expand the lab into lessons, capstone, and assessment. | Human terminal course | none |
| `kodex course "..." --json` | Render the course module. | JSON | none |
| `kodex portfolio "..."` | Package the course as presentable evidence. | Human terminal evidence packet | none |
| `kodex portfolio "..." --json` | Render the portfolio packet. | JSON | none |
| `kodex showcase "..."` | Turn portfolio evidence into audience-ready demo material. | Human terminal showcase kit | none |
| `kodex showcase "..." --json` | Render the showcase kit. | JSON | none |
| `kodex review-gate "..."` | Evaluate readiness, missing evidence, risks, and next actions. | Human terminal review gate | none |
| `kodex review-gate "..." --json` | Render the review gate packet. | JSON | none |

## Recommended walkthrough

### 1. Start with the product moment

```bash
kodex demo
```

Use this to confirm the human-friendly first-touch view still works.

### 2. Inspect the capability map

```bash
kodex modes
```

Use this to see available input modes, profession lanes, and BlackMamba University paths.

### 3. Route a real request

```bash
kodex guide "quiero una onda sinusoidal"
```

The guide should recommend a safe path without acting on the repository.

### 4. Build the learning packet

```bash
kodex lab "quiero una onda sinusoidal"
kodex course "quiero una onda sinusoidal"
```

The lab defines objectives, variables, deliverables, rubric, safety notes, and next commands. The course turns that packet into lessons, exercises, assessment, and a capstone.

### 5. Package evidence

```bash
kodex portfolio "quiero una onda sinusoidal"
```

Portfolio output is for proof-of-work: README outline, demo script, evidence checklist, publish boundary, and safety boundary.

### 6. Prepare the showcase

```bash
kodex showcase "quiero una onda sinusoidal"
```

Showcase output is for audience-aware presentation. It includes public summary, private review notes, talking points, audience variants, publish safety gate, proof checklist, and next commands.

### 7. Run the review gate

```bash
kodex review-gate "quiero una onda sinusoidal"
```

The review gate produces readiness score, decision, checks, missing evidence, risk flags, recommended actions, and safety boundary.

## High-stakes and biomedical language

For biomedical, medical, or high-stakes phrasing, the loop must stay educational and simulation-only. It should not produce diagnosis, treatment, cure, dosing, procedural instructions, or medical-device claims.

Recommended smoke request:

```bash
kodex review-gate "ver la piel como malla de Blender"
```

Expected behavior:

- route remains bounded
- safety language stays visible
- public claims stay behind a review gate
- no diagnosis or treatment claim is made

## Software build language

For software requests, the loop may describe architecture, preview paths, dry-run paths, and evidence requirements, but it should not claim that tests passed, files changed, commits happened, pushes happened, or PRs were opened unless those actions actually happened.

Recommended smoke request:

```bash
kodex review-gate "turn this README into an app with tests"
```

Expected behavior:

- engineering claims stay tied to evidence
- test claims require actual test output
- mutation remains `none`
- next actions remain explicit

## Local validation checklist

Run this after merging command-loop changes:

```bash
pytest
kodex demo
kodex demo --json
kodex modes
kodex modes --json
kodex guide "quiero una onda sinusoidal"
kodex lab "quiero una onda sinusoidal"
kodex course "quiero una onda sinusoidal"
kodex portfolio "quiero una onda sinusoidal"
kodex showcase "quiero una onda sinusoidal"
kodex review-gate "quiero una onda sinusoidal"
kodex review-gate "ver la piel como malla de Blender" --json
kodex review-gate "turn this README into an app with tests" --json
```

## Working rule

When adding future commands, keep the product loop readable:

1. Add a pure engine first.
2. Add tests for the engine.
3. Expose the CLI only after the engine is stable.
4. Preserve `--json` for machine-readable output.
5. Keep mutation explicit and separate.
6. Update this document when the loop changes.
