---
name: Bug report
about: Report a reproducible Kodex failure
title: "bug: "
labels: bug
assignees: ""
---

## What failed?

Describe the failure in one or two sentences.

## Phase

Choose one:

- [ ] INSTALL
- [ ] TEST
- [ ] CLI
- [ ] GIT
- [ ] PATCH
- [ ] CHECKS
- [ ] DIFF
- [ ] UNKNOWN

## Command

```bash
paste command here
```

## Output

```text
paste output here
```

## Diagnosis

Run:

```bash
kodex diagnose "paste short error here"
```

Or:

```bash
kodex diagnose ./error.log --file
```

Paste result:

```json
{}
```

## Expected behavior

What should have happened?

## Environment

- OS:
- Python:
- Kodex commit:
