# Workstream Current Status: Sample Demo Projects

Mnemonic: `sample-projects`

Start date: 2026-08-14

State: active

Integration target: `main`

Requirements: `R-PRODUCT-002`, `R-SCOPE-001`

## Goal

Provide a small set of realistic sample projects, each carried as a Git
submodule under `devcapsule-src/tests/resources/sample_projects/`, that a
developer can open and run inside DevCapsule. The samples exist to exercise and
demonstrate ordinary adopter workflows rather than DevCapsule's own recursive
self-test, and to surface missing product features from real use.

## Branch Association

The active branch is `sample-projects/fastapi-webapp`, forked from the `main`
registration commit for this workstream.

## Delivery Method

Each sample project is an independent public repository added as a submodule.
The parent repository records only the submodule pointer and `.gitmodules`
entry; sample source history belongs to the sample repository.

The first sample uses remote
`git@github.com:ccozianu/devcapsule-sample-fastapi-webbapp`, provisioned by the
product owner. Note the doubled `b` in `webbapp`; it is the actual repository
name, not a typo in this record.

## Current State

- The workstream is registered and its first branch is associated.
- The `fastapi-webapp` sample is complete, published, and wired in as a
  submodule.
- Three DevCapsule gaps were found while building it. None blocked the sample;
  all are recorded below for `project-management` to sequence.

## Last Task And Status

Last task: build the first sample project, `fastapi-webapp`.

Status: complete. The sample repository is
`git@github.com:ccozianu/devcapsule-sample-fastapi-webbapp` at commit
`7bf15e5`, and the parent records that pointer at
`devcapsule-src/tests/resources/sample_projects/fastapi-webapp`.

## Evidence

- Sample backend tests: `4 passed` against temporary SQLite.
- Full CRUD verified against real PostgreSQL 17 over `psycopg`: create, list,
  patch, and delete all behaved correctly, and the verification database was
  removed afterwards.
- Frontend production build succeeded: 30 modules transformed, 195 kB bundle.
- The sample's declaration and lock resolve through the ordinary public CLI.
  `config list` reports the PyCharm and Claude Code bindings, the
  `database.url` value, and the base-image, `claude-code-download`,
  `docker-daemon`, and `network` authorizations. No Codex component is
  selected.
- DevCapsule gate on this branch after adding the submodule: `230 passed`,
  `8 deselected`; mypy clean over 88 source files; five packaging
  integrations; `nox -s build` successful.

## Discovered DevCapsule Gaps

These did not block the sample, so the workstream continued rather than
pausing. They are candidates for `project-management` to sequence.

1. **No service dependency model.** A project cannot declare that it needs a
   database. The sample starts PostgreSQL itself with the Docker CLI, which is
   the only reason it recommends host-socket Docker and host networking at all.
   A first-class service declaration would let a sample like this need neither
   grant, which is a meaningful reduction in requested host privilege.
2. **No port declaration or allocation.** The sample publishes a fixed host
   port and collided immediately with an unrelated PostgreSQL already running
   on the development host. It now takes `TODO_DB_PORT`, but every sample
   solving this privately is a sign the product should model it.
3. **No `psql` client in the base image.** Reasonable for a general base, but
   database work then requires going through the database container. Worth a
   decision on whether database clients belong in a base, a component, or
   neither.

## Pending For The Product Owner

- The submodule pointer commit on this branch is not yet on `main`.
- Whether the three gaps above justify pausing this workstream in favour of
  `project-management` is a product-owner call; the escalation rule below was
  deliberately not triggered unilaterally because the sample works today.

## Planned Samples

1. `fastapi-webapp` (first): FastAPI backend, React single-page frontend,
   PostgreSQL persistence, PyCharm as the interactive surface, and Claude Code
   enabled. Ships a small TODO application, `.devcapsule/` project declaration
   and lock, and a `developer-readme.md` explaining how to start development
   inside DevCapsule.

Further samples are deliberately unspecified until the first one proves the
shape.

## Next Resumable Task

Prove the `fastapi-webapp` sample from a real adopter's starting point: launch
it as its own DevCapsule environment rather than developing it from inside the
DevCapsule checkout.

Done means:

- an isolated checkout authorizes the sample's base image and recommended host
  access, resolves, and launches PyCharm on the sample project;
- the developer-readme first-run sequence is executed verbatim in that
  environment and corrected wherever it does not match reality;
- Claude Code is confirmed available on `PATH` inside that environment; and
- the result is recorded here as evidence.

The sample's own verification is already complete; what remains untested is the
adopter path through `devcapsule project run` against the sample itself.

## Feature-Gap Escalation Rule

If completing a sample requires a DevCapsule capability that does not exist,
pause this workstream and switch to `project-management` to sequence the gap
rather than working around it inside a sample. Record the exact missing
capability, the sample that exposed it, and the workaround considered and
rejected.

## External State And Risks

- Sample repositories are public. No credential, host path, or personal
  configuration may enter their history.
- A sample must not depend on DevCapsule's recursive E2E workspaces, retained
  runs, or engineering-mode commands.
- Adding a submodule makes the parent tree depend on a reachable remote. Until
  a sample remote is published, parent-repository clones cannot initialize that
  submodule.

## Workstream Document Index

This workstream currently owns only this WIP status file.
