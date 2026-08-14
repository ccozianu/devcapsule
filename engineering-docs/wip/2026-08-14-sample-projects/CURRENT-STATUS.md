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
- After the `postgresql-client` component: `239 passed`, `8 deselected`; mypy
  clean over 90 source files; `nox -s build` successful. Nine focused tests
  cover catalog registration, the empty artifact contribution, and rejection of
  local-materialization delivery, a wrong license, a missing version, and
  declared artifacts.
- Base recipe 5 built locally as
  `docker.io/mycodespaceai/devcapsule-base:ubuntu-24.04-v026`, image ID
  `sha256:da328dd539d4f65edda2facbabeff3440c9a8ab4211e1fc0dc3cf9e6c94ab4eb`,
  from public PEX
  `dbdff25a6e09283c61318fd1f16803186f05cb454abef807f7338f19081827e1` at
  revision `49ad45362830746eecf180c7439859c50dcf0d4b`, with source
  verification reporting the public GitHub commit reachable. Direct inspection
  confirmed `psql (PostgreSQL) 16.14` at `/usr/bin/psql`, recipe version 5, the
  `PostgreSQL` license label, and an intact Node/Java toolchain. The image is
  **not published**.

## Discovered DevCapsule Gaps And Their Resolution

Three gaps surfaced while building the first sample. On 2026-08-14 the product
owner ruled on all three, so this workstream did not pause.

1. **No service dependency model.** *Deliberately out of scope for V1*: it
   would expand implementation, verification, and testing considerably. A
   sample may instead assume a developer-provided database or document how to
   start one in a container. Recorded in the V1 backlog as
   [modest sample-project experience improvements](../../implementation-notes/devcapsule/2026-08-07-v1-test-backlog.md).
2. **No port declaration or allocation.** Same ruling. Host networking is an
   accepted V1 simplifying assumption, and the sample's declaration now says so
   explicitly rather than presenting it as a workaround. The sample documents
   how to run with tighter host access instead.
3. **No `psql` client in the base image.** *Resolved.* A `postgresql-client`
   component now exists and the base provides it, because the PostgreSQL
   License permits redistribution.

## The postgresql-client Component

Product work performed under this workstream on the product owner's direction,
because the sample exposed the need.

`postgresql-client` is declared like any other component but is delivered by
the pinned base rather than materialized: its `delivery-policy` is
`base-image`, it contributes no artifact, and declaring artifacts on it is an
error. Base recipe 5 installs the client and labels its license. This is the
deliberate contrast with Claude Code, which cannot be redistributed and is
therefore acquired per developer after explicit terms authorization.

## Pending For The Product Owner

- **Publishing a base with recipe 5.** The rebuilt local base carries `psql`,
  but no base with recipe 5 is published yet. Until one is, a sample cannot
  honestly declare `postgresql-client`, because samples pin the published base
  by digest. The first sample therefore still pins the recipe-4 v025 digest and
  does not declare the component.
- **Advancing the sample's base pin** to the published recipe-5 digest and
  adding the `postgresql-client` component to its lock, once that base exists.
- **Routing.** The component is DevCapsule product work committed on a
  sample-projects branch. It was directed here because a sample exposed the
  need, but this workstream's registered goal is samples. Either widen the
  registered goal to include the modest capabilities samples require, or move
  such work to its own workstream in future.
- The submodule pointer and these commits are on this branch, not on `main`.

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
