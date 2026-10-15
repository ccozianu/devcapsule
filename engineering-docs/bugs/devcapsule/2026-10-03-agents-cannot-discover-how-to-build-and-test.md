---
status: fixed
severity: minor
target: 0.2.16
owner: workflow-improvements
opened: 2026-10-03
requirements: [R-PRODUCT-004]
---

# The workflow did not make "how do I build and test this project" discoverable to an agent

## Symptom

On 2026-10-03, in the dogfood capsule, the agent reported that the unit
suite could not run because "the capsule has no nox or pytest". Both were
in `devcapsule-src/.venv`, documented in `DEVELOPING.md` under *Developer
Setup* and pointed at from `WORKFLOW-LOCAL.md` under *Validation Commands*,
which `AGENTS.md` lists among the files to read at session start. The owner
ran the tests with one line.

## Why it is a bug and not an agent slip

The owner's reasoning: the workflow is an optional battery, and its value
proposition is that it coordinates agents and humans under a state-of-the-art
engineering process. Such a process sets expectations in general (bugs,
releases, branching) and in particular: for a Python project, a Java
project, any project, an agent must be able to find out how the software is
built and how its tests run. That promise is R-PRODUCT-004's. The agent's
failure to read the brief is real, and the workflow left it possible:

1. The definition listed *Validation commands* among the local file's
   recommended headings, "recommended, not required", and asked only for
   "where the full description lives".
2. The local file's section said `nox -s build` from `devcapsule-src` and
   pointed at the brief for the environment; the one line that mattered,
   `.venv/bin/python -m nox`, was not in it.
3. `workflow brief`, the one thing a session reads first, printed nothing
   about how to build or test.
4. Nothing in the reporting contract said that "the tool is missing" is a
   finding only after the project's own instructions were followed.

## Fix, 2026-10-03, on `ws-workflow-improvements/v1`

- *The Project's Local Workflow*: *Validation commands* is the one required
  heading: environment and commands, runnable as written, for the project's
  ecosystem. *Agent Reporting Contract*: a check reported as not runnable
  names the step that failed; tooling is never reported absent without the
  section having been followed. *Changes*, *Unreleased*: the entry with its
  migration step. Applied to the root file and the packaged definition.
- `WORKFLOW-LOCAL.md` *Validation Commands*: the virtual environment, the
  gate, a single-module run, how to create the environment, and the capsule's
  `/tmp` scratch limit, all inline.
- `AGENTS.md`: one sentence pointing at that section before any check is
  reported as not runnable.
- `devcapsule workflow brief` prints the section verbatim, or says the local
  file lacks it; `tests/test_workflow_coordination.py` covers both.

## Verification target

`test_brief_prints_the_session_context` passes; the owner's next session in
any checkout sees the commands in the brief. Close when a release carries
the fix and a session starting fresh in a capsule runs the gate from the
brief's text alone.

## Reopen if

A later definition refresh drops the required heading, or a project's brief
prints a section that is not runnable as written.
