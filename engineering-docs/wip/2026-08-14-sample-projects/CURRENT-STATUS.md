# Workstream Current Status: Sample Demo Projects

Mnemonic: `sample-projects`

Start date: 2026-08-14

State: paused 2026-08-21 after adopting the packaged DevCapsule workflow in trading-research; labeled fixtures remain next

Integration target: `main`

Requirements: `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCS-001`

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
- `trading-research` is the second sample. Its public repository is
  `git@github.com:ccozianu/devcapsule-sample-trading-research.git`, and it is
  wired in as a submodule at commit `f058c8c`. Its initial design brief and
  pipeline pseudocode are present in the sample repository, and it now has a
  DevCapsule declaration and Linux lock selecting Python, PyCharm, Codex, and
  Claude Code. Its evaluation-first Python scaffold implements deterministic
  claim classification and calibration reporting. The declaration recommends
  host networking with an explicit workflow justification.
- The sample now carries the reusable packaged `WORKFLOW.md`, the current
  generic `AGENTS.md` entry point, and a project-owned `CURRENT-STATUS.md` and
  documentation index. Its live status no longer resides in README.
- Three DevCapsule gaps were found while building it. None blocked the sample;
  all are recorded below for `project-management` to sequence.

## Last Task And Status

Last task: upgrade `trading-research` with the workflow definition packaged in
the newly fixed local PEX while preserving its project-owned state.

Status: complete and published. Sample `origin/main` is at `f058c8c`. Bare
workflow bootstrap was first fixed and packaged on `recursive-e2e/stage-4`;
the exact local PEX then refreshed only the reusable definitions and created
the missing project-instance handoff and index. Existing requirements, source,
configuration, and project brief were preserved. This checkout has authorized
`network = "host"`; its generated resolution is fresh.

## Evidence

- The trading-research gitlink pins `f058c8c`, the published `origin/main` of
  its repository; generated `.idea/` and Python cache files are ignored.
- The installed `WORKFLOW.md` is byte-identical to the packaged definition in
  the local `devcapsule-local.pex` source tree. Eight unit tests and Python
  compilation pass after the migration, and the nested repository is clean
  and synchronized with its `origin/main`.
- An isolated `devcapsule project config list` accepted the declaration and
  lock, selected PyCharm, Codex, and Claude Code, and reported only the expected
  developer-owned base-image and Claude-download authorizations as unresolved.
- After the host-network change, `devcapsule project config list` reports
  `network` as `authorized` with value `host`, and the generated resolution
  records `network = "host"` and reports `fresh`.
- Trading-research validation: eight unit tests pass and `python -m compileall`
  succeeds across `src` and `tests`.
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
  `PostgreSQL` license label, and an intact Node/Java toolchain.
- Recipe 5 was published on 2026-08-15 as
  `docker.io/mycodespaceai/devcapsule-base:ubuntu-24.04-v026`, registry digest
  `sha256:a9f00250515b757d8e9d8ad832d9cab09a9a6e000f630651704e8538a4702998`.
  Strict pull-by-digest inspection after removing the local tag confirmed
  `psql (PostgreSQL) 16.14`, Node.js `v22.23.1`, `javac 25.0.4`, Apache Maven
  `3.9.16`, `JAVA_HOME=/opt/java/current`, recipe version 5, the `PostgreSQL`
  license label, the exact PEX and source lineage, and that Claude Code is
  absent from the public base.
- The sample now pins that published digest, declares the `postgresql-client`
  component and capability, and still resolves through the public CLI. Gate
  after the change: `239 passed`, `8 deselected`; mypy clean over 90 source
  files; `nox -s build` successful.

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

2. `trading-research` (second, current priority): public repository
   `git@github.com:ccozianu/devcapsule-sample-trading-research.git`, mounted as
   a submodule at
   `devcapsule-src/tests/resources/sample_projects/devcapsule-sample-trading-research`.
   The initial sketch specifies an evaluation-first, rotated multi-LLM debate
   over canonical atomic claims, followed by a deterministic LLM-free merge
   that reports convergence, majority, or divergence without treating
   agreement as correctness. Its initial DevCapsule declares `python`,
   `python-ide`, `codex-agent`, and `claude-code-agent`, and recommends host
   networking. Its initial deterministic Python scaffold is published; the
   workflow definition and project-owned handoff are now published as well;
   the next milestone is a small human-reviewed labeled fixture set.

## Adopter-Path Verification

Run on 2026-08-15. All four criteria passed after the containerized-launch gaps
found during the first attempt were fixed on this branch.

- An isolated adopter checkout authorized the published base digest, host
  Docker, host networking, and the Claude Code download, then resolved. No
  developer-owned configuration was touched.
- Materialization produced the sample's own environment
  `devcapsule-local-pycharm:9952e3bd59d99dbafc9f`, image ID
  `sha256:1a16023eb3d1e2e4b078a8d57fef8dc487dfdea4e81107fb14341e1c9aea5018`,
  formation identity
  `9952e3bd59d99dbafc9f41ae42eb07d1fd097c6dc05d22d3c4cd2d3219f83650`, on base
  identity `sha256:da328dd539d4f65edda2facbabeff3440c9a8ab4211e1fc0dc3cf9e6c94ab4eb`
  obtained from the published recipe-5 digest.
- Probing that image: `psql (PostgreSQL) 16.14` at `/usr/bin/psql`, **Claude
  Code `2.1.227` at `/opt/claude/bin/claude` on `PATH`**, Node.js `v22.23.1`,
  npm `10.9.8`, Python `3.12.3`, Git, and the Docker CLI. Codex is correctly
  absent, because the sample does not declare it. PyCharm is at
  `/opt/jetbrains/pycharm/bin/pycharm.sh` and is launched by the runtime plan
  rather than from `PATH`, so its absence there is by design.
- The developer-readme first-run sequence was executed inside that environment
  against a clean copy of the sample: dependencies installed, backend tests
  `4 passed`, `psql` connected to PostgreSQL `17.11`, the API answered health
  and created and listed a TODO, `psql` then saw the exact row the API had
  written, and the frontend installed and built a 195 kB bundle.
- Two developer-readme defects were found and fixed: the
  individual-authorization fallback omitted the **required** `base-image`
  authorization, and `--all-recommended` refuses to run without an interactive
  terminal while being presented as the primary path.

### GUI Launch From Inside A Capsule

The first attempt exposed three host-only assumptions: bind sources were not
translated through the current container's mounts, the launcher ignored the
Docker socket named by `DOCKER_HOST`, and transient launch files were staged on
a container-local filesystem the host daemon could not read. Commits `2f9f605`
and `ebccbec` fixed those paths and added failure messages for untranslatable
mounts. A live foreground launch against `fastapi-webapp` subsequently started
the sample environment and removed its container when the IDE exited; the
foreground/detached lifecycle evidence is recorded in the
[detached-container bug](../../bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md).

## Next Resumable Task

In the `trading-research` DevCapsule, define and load the first small,
human-reviewed labeled fixture set. Record source/license metadata, gold atomic
claims, and an explicit grading rule; then report the single-best and
flat-majority baselines without live model calls. Capture R-EVAL-002 once the
fixture scope is chosen. Host networking is already authorized for this
checkout; base-image authorization remains required for launch and the Claude
Code download authorization remains recommended.

The earlier `fastapi-webapp` GUI-launch limitation was addressed by this
branch's container-path translation and host-backed staging changes; a live
foreground run against the sample is recorded in the detached-container bug.

## Open Threads

- Fixture scope, source licensing, and the explicit grading rule remain for
  the next interactive trading-research session.
- The sample-projects branch and updated gitlink are not yet integrated into
  DevCapsule `main`.

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
