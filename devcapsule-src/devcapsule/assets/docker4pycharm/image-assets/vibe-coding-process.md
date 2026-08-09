# Vibe-Coding Process Bootstrap

This file is a reusable bootstrap template baked into the Dockerized IDE image.
It is not the target project's source of truth. Use it to create or update the
target project's own process documentation.

Expected image path:

```text
/usr/local/share/docker4ide/vibe-coding-process.md
```

## User Prompt

When starting work in a project that does not already have this process
documented, the user can ask:

```text
Bootstrap the vibe-coding process documentation from
/usr/local/share/docker4ide/vibe-coding-process.md into this project.
Create or update AGENTS.md, README.md, CURRENT-STATUS.md, REQUIREMENTS.md,
docs/, and engineering-docs/ as appropriate. Preserve existing project docs
and adapt the process to this repository. Set workflow-type in
.devcapsule/devcapsule.toml to single-stream or multiple-streams; use
single-stream when the project does not need independently resumable efforts.
```

## Agent Instructions

If you are the agent receiving that prompt:

1. Inspect the current repository before editing.
2. Preserve existing project documentation and conventions.
3. Record `workflow-type` in `.devcapsule/devcapsule.toml`; default to
   `single-stream` unless the project needs independently resumable efforts.
4. Create or update `AGENTS.md` so future agents read the project brief,
   workflow type, root status, and selected handoff.
5. Ensure `README.md` is a stable developer welcome page. Use
   `CURRENT-STATUS.md` as the detailed handoff for `single-stream` and the open
   workstream registry for `multiple-streams`.
6. Create or update `REQUIREMENTS.md` as the overview and index for the
   project's root requirements, and create or update canonical detailed
   requirement files under `engineering-docs/requirements/`.
7. Keep stable user and adopter guidance under `docs/`.
8. Create the relevant categories under `engineering-docs/`: requirements,
   specifications, decisions, design notes, implementation notes, WIP and
   archive workstream state when selected, bugs, completed tasks, and
   explicitly requested session records.
9. Add a short design or implementation note if useful, but do not duplicate
   large boilerplate into multiple places.
10. Keep active tasks separate from historical context.
11. Add explicit requirement IDs, done criteria, and verification notes for
    active tasks.
12. Run a cheap validation check if available.
13. Report exactly what changed and what remains uncommitted.

## Recommended AGENTS.md

Adapt this to the target project:

````markdown
# Agent Instructions

Before starting work in this repository, read the project brief at:

```text
README.md
```

Read `.devcapsule/devcapsule.toml` and select the declared workflow type. A
missing field means `single-stream`. Then read `CURRENT-STATUS.md`. Treat it as
the detailed handoff for `single-stream` and the open-workstream registry for
`multiple-streams`; in multiple-stream mode, select one workstream and read
`engineering-docs/wip/MNEMONIC/CURRENT-STATUS.md`.

After reading the required documents, acknowledge that you understand the
project purpose, requirement overview, current state, and planned next step
before proceeding.

If the brief defines a planned next step, state that next step to the user
before proceeding.

If the brief does not define a planned next step, ask the user to choose the
next step to work on.

When completing a stage, retiring a task, changing project state materially, or
ending a session, update the selected handoff. In multiple-stream mode, update
root `CURRENT-STATUS.md` only when the set or lifecycle of open workstreams
changes.
````

If the target project already has an `AGENTS.md`, merge these instructions
without deleting project-specific constraints.

## Recommended REQUIREMENTS.md

Create or adapt this file at the repository root:

````markdown
# Requirements Overview

This file is the project-level overview and index for root requirements. It
does not replace the active task list in `README.md`; it gives tasks, bugs, and
implementation notes stable requirement IDs to reference and links to the
canonical detailed records under `engineering-docs/requirements/`.

## Status Values

- `proposed`: captured, but not yet accepted as a project requirement.
- `accepted`: accepted, but not yet implemented.
- `implemented`: code or docs exist, but validation is incomplete.
- `repo-validated`: static checks, smoke tests, or automated checks passed.
- `manually validated`: the user or agent validated behavior in the running
  product.
- `deferred`: accepted direction, but intentionally outside the current target.
- `rejected`: considered and intentionally not pursued.

## Priority Bands

- `MVP`: required for the first useful version.
- `current stabilization`: required before closing the current stabilization
  pass.
- `later`: useful, but not required for the current target.

## Requirement Types

```markdown
- high-level goals: judged against accumulated evidence and project direction;
- concrete requirements: testable in principle, even when some validation is
  manual.
```

Every active task, bug, or completed-task record should include a
`Requirements:` line when it materially implements, validates, changes, defers,
or reinterprets a requirement.

## Requirement File Template

Each detailed file under `engineering-docs/requirements/` should be the canonical record
for one requirement:

```markdown
---
id: R-AREA-000
title: Short Name
type: requirement
kind: high-level-goal | concrete-requirement
status: proposed | accepted | implemented | repo-validated | manually validated | deferred | rejected
priority: MVP | current stabilization | later
verification:
  - ...
external_refs: []
---

# R-AREA-000: Short Name

## Statement

...

## Verification or Evaluation

...
```

## Current Requirements

- `R-BOOT-001` — [Define Initial Requirements](engineering-docs/requirements/r-boot-001-define-initial-requirements.md)
````

## Recommended README.md Handoff Section

Add or adapt this near the end of `README.md`:

````markdown
# Current Status And Next Step

This file is the project handoff point. Future agents should update it when
completing a stage, changing the project state materially, retiring a task, or
ending a session.

Current stage: ...

Current status: ...

Important decisions:

- ...

Retired or historical issues:

- ...

When resuming the project, read these files in order:

1. `README.md`
2. `REQUIREMENTS.md`
3. `engineering-docs/requirements/` for relevant canonical detail files
4. `engineering-docs/bugs/` for active bug records, if relevant
5. `engineering-docs/implementation-notes/...`

Planned next items:

1. ...
   Requirements: R-...
   Done means: ...
   Verification: ...
   Reopen if: ...
2. ...
````

The active next-task list should contain only tasks the next agent should
actually consider doing.

## Recommended Engineering Documentation Use

Use `engineering-docs/design-notes/` for proposals, alternatives, research,
and unsettled architecture. Use `engineering-docs/implementation-notes/` for
execution plans, validation evidence, debugging history, and checklists that
should not stay in the active task list:

- Manual validation results.
- Retired bugs that may recur.
- Log signatures and command transcripts.
- External constraints such as credentials, services, datasets, deployment
  targets, or host setup.
- Risk and security notes.

Use `engineering-docs/bugs/` for one file per active or recently
investigated bug. Each bug file should capture affected requirements, symptom,
environment, reproduction, evidence such as logs or stack traces, current
hypothesis, verification target, fix notes, and close criteria. Keep secrets
out of bug records.

Use `engineering-docs/decisions/` for adopted durable choices and
`engineering-docs/specifications/` for normative technical contracts. Use
`engineering-docs/wip/MNEMONIC/` and
`engineering-docs/archive/MNEMONIC/` only when the project selects
`multiple-streams`. Create session records only when explicitly requested.

Use `engineering-docs/completed-tasks/` for one file per task that was
completed, manually validated, retired, or no longer reproduced.

When a task is completed, manually validated, no longer reproduced, or
intentionally deferred:

1. Remove it from the active task list.
2. Add a dated status note if future agents need to know why it disappeared.
3. Preserve useful evidence in `engineering-docs/completed-tasks/`.
4. State when the task should be reopened.

Recommended completed-task file:

````markdown
# Completed Task: ...

Date: ...

Status: completed | retired | manually validated | no longer reproduced

## Original Task

...

## Requirements

R-...

## Done Means

...

## Verification

...

## Environment Provenance

- Image: ...
- Launcher mode: ...
- Project mount: ...
- Important host-side assumptions: ...

## Retrospective Notes

...

## Reopen If

...
````

Recommended bug file:

````markdown
# Bug: Short Title

Date opened:

Status: open | reproduced | fixed | cannot reproduce | retired

Requirements:

- R-...

## Symptom

What the user or agent observed.

## Environment

- Image:
- Launcher command:
- Project path/mount:
- Host assumptions:
- Relevant package/app versions:

## Reproduction

Manual steps:

1. ...

Expected:

Actual:

Reproducibility: always | intermittent | once | unknown

## Evidence

Logs, stack traces, screenshots, commands, timestamps.
Do not include secrets.

## Hypothesis

Current best explanation, with uncertainty.

## Verification Target

Cheapest check that should catch this later:

- Automated test:
- Script/check:
- Manual validation:

## Fix Notes

Files changed, decision made, tradeoffs.

## Close Criteria

Done means:
Verification:
Reopen if:
````

## Session Close Checklist

At the end of a meaningful session, update the project handoff with:

```text
Changed:
- ...

Requirements:
- ...

Validated:
- ...

Not validated:
- ...

External state:
- ...

Uncommitted changes:
- ...

Next task:
- ...
```

Record external state without secrets. Useful examples include local image tags,
manual GUI login state, host services, credentials being available only through
an agent or secret file, and pushes that must be performed by the user.

## Decision Notes

For decisions that may be revisited, create a small note under
`engineering-docs/design-notes/`:

````markdown
# Decision: ...

Date: ...

Context:
...

Options:
...

Decision:
...

Consequences:
...

Reopen if:
...
````

Keep active tasks, completed tasks, and decisions separate. Active tasks answer
"what should we do next?", completed tasks answer "what happened and how was it
validated?", and decisions answer "why did we choose this path?".

## First Pass In A Python Project

For a normal Python repository, a good first pass is:

1. Inspect `README.md`, `pyproject.toml`, `requirements*.txt`, `tox.ini`,
   `noxfile.py`, `pytest.ini`, and CI config if present.
2. Identify the cheapest reliable validation command.
3. Record the current state and next useful task in `README.md`.
4. Start implementation only after the active task list is clear.

## Git Hygiene

Before committing:

1. Run `git status --short --untracked-files=all`.
2. Keep unrelated user or IDE changes out of the commit.
3. Commit coherent units of work with a message that describes the saved state.
4. If pushing is blocked by missing user credentials, commit locally and let the
   user push externally.
