# Profession Intent System

Kodex should not wait for users to explain every workflow from scratch.

A serious creative/technical agent should arrive with a map of human professions, common requests, preferred inputs, safe outputs, and experimental paths already half-formed.

This is the **Profession Intent System**.

It is designed for Kodex and BlackMamba University.

## Core idea

Most users do not ask like software engineers.

They ask like:

```text
make this song hit harder
turn this idea into an app
explain this like a class
make this image usable for a cover
analyze this waveform
help me sell this product
build me a dashboard
make it look expensive
```

Kodex should understand the profession behind the request before deciding the workflow.

## Why this matters

Traditional tools wait for explicit instructions.

Kodex should infer a working lane:

```text
request
  -> detect profession lane
  -> select input mode
  -> choose output contract
  -> pick safety rules
  -> generate experiment plan
  -> create reusable template
  -> mutate, never repeat
```

This creates a product that feels intelligent before it writes code.

## Profession lanes

Initial lanes:

| Lane | User type | Typical input | Kodex output |
|---|---|---|---|
| Music Producer | producer, songwriter, DJ, audio engineer | lyric, audio, BPM, vibe, reference | arrangement plan, lyrics, mix notes, visual idea, release checklist |
| Software Builder | developer, founder, maker | README, task, repo, feature idea | spec, files, tests, guarded write plan |
| Educator | teacher, course creator, tutor | topic, lesson goal, student level | lesson, quiz, project, rubric, BlackMamba University module |
| Visual Artist | designer, cover artist, VJ | image, style, format, brand | art brief, prompt pack, layout, social assets |
| Scientist / Lab | student, researcher, experimenter | question, formula, data, observation | model, simulation, notebook plan, experiment protocol |
| Business Operator | seller, agency, manager | offer, customer, product, metric | pitch, landing copy, CRM flow, automation checklist |
| Content Creator | YouTuber, streamer, social media artist | idea, clip, song, audience | hook, script, caption, thumbnail brief, posting plan |
| Maker / Hardware | Arduino, Raspberry Pi, robotics, DMX | device, sensor, goal, constraints | wiring plan, code skeleton, test checklist, safety notes |

## Input mode first, not chatbot guessing

The app should expose the possible entrances up front:

```text
Prompt
Spec
Repo
File
Screenshot
Audio
Creative
Demo
Profession
Course
Experiment
```

The user chooses a doorway. Kodex activates the right contract.

Example:

```text
Profession: Music Producer
Input mode: Audio
Request: make this hit harder
```

Kodex should not answer like a generic assistant. It should produce:

```text
- listening checklist
- structure diagnosis
- hook strength notes
- mix/arrangement interventions
- visual/release suggestions
- safe next files/actions
```

## The Iyari rule

Some requests are signature requests.

Example:

```text
quiero una onda sinusoidal
```

For Kodex, this should not become a repeated generic sine-wave script.

It should detect a creative-math/audio/visual lane and generate a fresh variant:

```text
- visual waveform
- audio oscillator
- mathematical explanation
- interactive demo
- synth patch
- BlackMamba styled asset
```

Rule:

```text
Never repeat.
Always mutate.
Always elevate.
```

## BlackMamba University angle

Every profession lane can become a learning path.

BlackMamba University should turn real requests into reusable modules:

```text
request
  -> profession lane
  -> task template
  -> guided explanation
  -> experiment
  -> project
  -> assessment
  -> portfolio artifact
```

This means the same engine can:

- help build software
- teach the workflow
- generate exercises
- create demos
- preserve style
- improve the next run

## Template anatomy

Every profession template should define:

```text
id
name
who_it_serves
common_requests
input_modes
output_contracts
safe_actions
blocked_actions
experiments
teaching_modules
signature_variations
```

## Product principle

Kodex should feel like it already studied the human world.

Not because it knows everything.

Because it arrives with respectful defaults, clear doors, and enough structure to help a person move from idea to artifact without getting trapped in blank-prompt hell.
