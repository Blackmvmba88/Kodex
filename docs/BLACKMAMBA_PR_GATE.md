# BlackMamba PR Gate

BlackMamba PR Gate is the first automation layer for turning a noisy GitHub queue into a small set of human decisions.

## Contract

The gate may automatically:

- inspect open pull requests and changed files;
- read CI/check status;
- read review decisions and unresolved review threads;
- classify PRs as docs, tests, dependency maintenance, or code;
- compare open PRs for high file/title overlap;
- create and maintain `bm:*` labels;
- maintain one sticky PR status comment;
- reconcile all open PRs on a schedule.

The gate does **not** automatically:

- merge PRs;
- close PRs;
- push commits;
- rewrite branches;
- resolve review threads;
- dismiss reviews;
- modify PR code.

That boundary is deliberate. V1 automates movement and visibility, not important decisions.

## States

| State | Meaning | Default next action |
| --- | --- | --- |
| `READY` | Safe, low-risk candidate with no active blocker | Human may merge |
| `READY_FOR_APPROVAL` | Clean code/policy-sensitive change | Human review/approval |
| `WAITING_CI` | Checks are still running | Wait/reconcile |
| `BLOCKED_CI` | One or more checks failed/cancelled/timed out | Fix CI/root cause |
| `BLOCKED_REVIEW` | Unresolved review thread or requested changes | Address feedback |
| `BLOCKED_CONFLICT` | GitHub reports merge conflict/unmergeable state | Rebase/resolve conflict |
| `CONSOLIDATE` | Another open PR has high file/title overlap | Compare and keep best path |
| `DRAFT` | PR is still draft | Finish or close |

## Labels

The gate owns only labels prefixed with `bm:`. Existing project labels are preserved.

Examples:

- `bm:ready`
- `bm:approval`
- `bm:blocked-ci`
- `bm:blocked-review`
- `bm:blocked-conflict`
- `bm:waiting-ci`
- `bm:consolidate`
- `bm:draft`
- `bm:docs`
- `bm:tests`
- `bm:dependency`
- `bm:code`

## Duplicate / superseded PR detection

V1 treats overlap as an advisory signal, never as permission to close anything.

Two open PRs become consolidation candidates when both conditions pass configured thresholds:

1. a high percentage of the smaller PR's changed files also appear in the other PR;
2. their normalized titles share enough meaningful tokens.

The thresholds live in `.github/blackmamba/pr-gate.json`.

## Security boundary

The workflow uses `pull_request_target` because it needs write permission for labels/comments. Therefore it **must never execute code from the PR head**.

The workflow explicitly checks out the trusted base branch and runs the gate implementation from that branch. Do not change this to checkout an untrusted PR head while write-capable `GITHUB_TOKEN` permissions are enabled.

## Execution

Automatic triggers:

- PR opened/reopened/updated/edited;
- draft/ready transitions;
- PR review submitted/edited/dismissed;
- reconciliation every six hours.

Manual reconciliation is also available with `workflow_dispatch`, for one PR or all open PRs.

## Roadmap

Once V1 proves stable across real repositories, the portable layer can add opt-in policies for:

- safe docs auto-merge;
- dependency-update policy;
- cross-repository dashboard summaries;
- superseded-PR recommendations;
- approval commands;
- repository-specific hardware/manual-test gates.

Any mutation beyond labels/comments should remain explicitly configurable and auditable.
