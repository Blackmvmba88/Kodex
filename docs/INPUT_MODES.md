# Input Modes

Kodex should not behave like a blank chatbot that constantly asks how to receive work.

The application should present clear input modes up front. The user chooses the mode, and Kodex adapts its interpretation, safety boundary, and output contract.

## Product Rule

```text
Do not ask for the input method inside generated code.
Expose input modes as first-class app choices.
```

The user should see options such as:

```text
Choose input mode:

1. Prompt       — describe what you want
2. Spec         — use README.md / SPEC.md / AGENTS.md
3. Repo         — inspect the whole repository
4. File         — transform one file
5. Screenshot   — understand an image or UI state
6. Audio        — analyze or generate from sound intent
7. Creative     — expand a signature idea into an artifact
8. Demo         — run a safe built-in example
```

## Why This Matters

Input mode changes the meaning of the same words.

Example:

```txt
quiero una onda sinusoidal
```

As a prompt, it may mean:

```txt
create a sine wave module
```

As creative input, it may mean:

```txt
make a beautiful BlackMamba-style math/visual/audio artifact
```

As audio input, it may mean:

```txt
generate an oscillator or WAV export
```

As demo input, it may mean:

```txt
show the user what Kodex can do without touching the repo
```

## CLI Shape

The CLI can expose input modes directly:

```bash
kodex intake --mode prompt "quiero una onda sinusoidal"
kodex intake --mode spec --source README.md --source SPEC.md
kodex intake --mode repo --path .
kodex intake --mode file --source agent/main.py "add apply flag"
kodex intake --mode creative "quiero una onda sinusoidal"
kodex intake --mode demo sine-wave
```

For app-building, modes can map into existing safety flows:

```bash
kodex app-build "Implement MVP" --mode spec --dry-run
kodex app-build "quiero una onda sinusoidal" --mode creative --dry-run
kodex app-build "quiero una onda sinusoidal" --mode creative --apply
```

## App / UI Shape

A future app should not open with an empty text box only.

It should open with a deliberate launcher:

```text
KODEX
What are we building today?

[ Prompt ] [ Spec ] [ Repo ] [ File ]
[ Screenshot ] [ Audio ] [ Creative ] [ Demo ]

Safety: Preview first · Dry-run available · Apply requires guarded branch
```

## Mode Contracts

### Prompt Mode

Use when the user gives a direct task.

```json
{
  "mode": "prompt",
  "input": "add a smoke test",
  "expected_artifact": "small code/test change",
  "safety": "preview_by_default"
}
```

### Spec Mode

Use when the repo has README/SPEC/AGENTS sources.

```json
{
  "mode": "spec",
  "sources": ["README.md", "SPEC.md", "AGENTS.md"],
  "expected_artifact": "multi-file implementation plan",
  "safety": "dry_run_before_apply"
}
```

### Repo Mode

Use when the task depends on repo structure.

```json
{
  "mode": "repo",
  "path": ".",
  "expected_artifact": "diagnosis, map, plan, or guarded patch",
  "safety": "inspect_first"
}
```

### File Mode

Use when a single file is the focus.

```json
{
  "mode": "file",
  "source": "agent/main.py",
  "expected_artifact": "targeted edit",
  "safety": "small_diff"
}
```

### Screenshot Mode

Use when the user provides an image, UI, terminal capture, or design.

```json
{
  "mode": "screenshot",
  "expected_artifact": "visual diagnosis or implementation plan",
  "safety": "no_assumptions_without_visible_context"
}
```

### Audio Mode

Use when sound, waveform, music, voice, BPM, lyrics, or signal analysis is the seed.

```json
{
  "mode": "audio",
  "expected_artifact": "audio tool, analysis, waveform, or generator",
  "safety": "explicit_export_before_write"
}
```

### Creative Mode

Use when the request is a seed, not a spec.

```json
{
  "mode": "creative",
  "input": "quiero una onda sinusoidal",
  "expected_artifact": "fresh artifact variant",
  "rule": "never repeat; always mutate; always elevate"
}
```

### Demo Mode

Use when the user wants to see Kodex without risk.

```json
{
  "mode": "demo",
  "input": "sine-wave",
  "expected_artifact": "non-mutating showcase",
  "safety": "zero writes"
}
```

## Internal Interpretation Object

Every task should normalize into one shape:

```json
{
  "input_mode": "creative",
  "literal_request": "quiero una onda sinusoidal",
  "artifact_target": "terminal oscilloscope demo",
  "sources": [],
  "repository": ".",
  "safety_mode": "dry_run",
  "variation_seed": "neon waveform",
  "expected_outputs": ["generated files preview", "tests", "next command"]
}
```

## Design Principle

A blank prompt says:

```txt
Tell me what to do.
```

Input modes say:

```txt
I know the kinds of work you do. Pick the door.
```

That is the difference between a generic agent and a product people want to live inside.
