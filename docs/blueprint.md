# Kodex — BlackMamba Dev Agent Blueprint

Kodex is a personal programming agent designed to help manage, understand, and improve BlackMamba repositories.

It is not just a chatbot. It is a local-first engineering assistant that maps repos, remembers architecture, plans tasks, edits code safely, runs checks, and prepares commits or pull requests.

## Mission

Build a private Codex-like workflow for BlackMamba projects:

- scan existing GitHub/local repositories
- detect stacks, entrypoints, tests, and run commands
- generate project maps
- keep persistent engineering memory
- plan small safe implementation steps
- execute code changes locally
- prepare commits and PR summaries
- avoid destructive actions unless explicitly approved

## Core Philosophy

Observer first. Builder second.

Kodex must inspect before editing, plan before changing, test before committing, and summarize before handing control back.

## Architecture

```txt
GitHub repositories / local repos
        ↓
repo scanner
        ↓
project memory
        ↓
task planner
        ↓
executor
        ↓
git operator
        ↓
commit / branch / PR
```

## Initial Modules

```txt
agent/
  main.py          CLI entrypoint
  repo_scanner.py  repository inspection
  memory.py        persistent project memory
  task_planner.py  task decomposition
  git_ops.py       git status/branch/commit helpers

memory/
  rules.md         agent operating rules
  projects.json    scanned repository registry
  decisions.log    architectural decisions

scripts/
  bootstrap.sh     local setup
  scan_repo.py     direct scanner runner
```

## MVP Commands

```bash
kodex scan ./path/to/repo
kodex map
kodex task "add healthcheck and tests"
kodex plan
kodex status
```

## Safety Rules

- Never delete files without explicit confirmation.
- Never commit secrets.
- Never push directly to main unless explicitly requested.
- Prefer small branches and small commits.
- Always run available tests before proposing completion.
- If no tests exist, create or recommend a smoke test.

## Recommended First Target Repos

1. `Blackmvmba88/Kodex` — core agent brain.
2. `Blackmvmba88/gk-cli` — reference for multi-repo work item workflow.
3. `Blackmvmba88/gemini-cli` — reference for terminal AI agent patterns.
4. `Blackmvmba88/blackmamba` — future private umbrella repo.

## First Milestone

Create a local Python CLI that can scan a repo and produce a structured project map.

Output example:

```json
{
  "name": "example-repo",
  "stack": ["python", "react"],
  "entrypoints": ["main.py", "src/App.tsx"],
  "tests": ["pytest"],
  "commands": {
    "test": "pytest",
    "dev": "npm run dev"
  },
  "risks": ["no CI detected"],
  "next_tasks": ["add smoke tests", "document local setup"]
}
```
