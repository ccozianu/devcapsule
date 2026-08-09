# DevCapsule

[![Tests](https://github.com/ccozianu/devcapsule/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/ccozianu/devcapsule/actions/workflows/tests.yml)
[![Coverage](docs/badges/coverage.svg)](https://github.com/ccozianu/devcapsule/actions/workflows/tests.yml)

DevCapsule creates reproducible, resumable development environments for humans
and AI coding agents. It combines a real IDE, agent-ready development tooling,
versioned project memory, and explicit boundaries around access to the host.

The active Python distribution project lives in `devcapsule-src/`; its import
package remains `devcapsule`.
Project lifecycle operations and workstation image operations now have
separate noun-oriented command trees:

```text
devcapsule project [--path PATH] SUBCOMMAND [options]
devcapsule images SUBCOMMAND [options]
```

The adopted target model is capability-first: projects declare what their
environment needs, platform locks select concrete components, and
developer-owned configuration authorizes host access.

## Repository Layout

- `devcapsule-src/` — active Python distribution project: packaging, tests,
  runtime assets, and the `devcapsule/` import package.
- `docs/` — stable product guidance for DevCapsule users and adopters.
- `engineering-docs/` — contributor- and agent-facing requirements,
  specifications, decisions, design notes, implementation evidence, and
  workflow records.
- `docker4pycharm/` — historical shell-based PyCharm MVP and reference
  material; it is not the source of the active implementation.
- `.devcapsule/` — this project's capability declaration and platform lock.

The `-src` suffix is deliberate: in a default clone named `devcapsule`, the
three layers are `devcapsule/devcapsule-src/devcapsule` (checkout,
distribution project, import package) rather than three identically named
directories.

## Developer Setup

The Python project uses Nox as its primary validation entry point. From the
repository root:

```text
cd devcapsule-src
python -m nox -s tests
```

Run the full local gate before handing off implementation changes:

```text
cd devcapsule-src
python -m nox -s build
```

The full gate includes compilation, shell syntax checks, pytest, type checks,
CLI smoke tests, PEX construction, and PEX smoke tests. It always creates the
local-only `dist/devcapsule-local.pex`. On a clean repository it also creates
and smoke-tests `dist/devcapsule.pex` with the exact `HEAD` revision, without
requiring that revision to have been pushed already. On a dirty repository it
explicitly reports that the revision-bearing artifact was skipped. To
deliberately discard cached Nox environments, add
`--no-reuse-existing-virtualenvs`.

For CLI installation and usage, see
[`devcapsule-src/README.md`](devcapsule-src/README.md).

## Development Principles

- Keep host filesystem, credentials, Docker, devices, and networking exposure
  explicit and documented.
- Keep current behavior in user documentation; preserve obsolete behavior only
  as clearly labelled historical reference.
- Store requirements, decisions, bugs, validation evidence, and handoff state
  in versioned files rather than only in chat history.
- Add automated Nox-covered checks when practical; use manual validation for
  host Docker, image, and GUI behavior that repository automation cannot cover.

## Project Documentation

- [`index.md`](index.md) — complete documentation map.
- [`AGENTS.md`](AGENTS.md) — mandatory instructions for coding agents.
- [`WORKFLOW.md`](WORKFLOW.md) — human-agent development protocol.
- [`REQUIREMENTS.md`](REQUIREMENTS.md) — project requirement overview and
  index.
- [`docs/README.md`](docs/README.md) — user-facing product documentation map.
- [`engineering-docs/README.md`](engineering-docs/README.md) — engineering
  documentation taxonomy and placement rules.
- [`engineering-docs/decisions/product/`](engineering-docs/decisions/product/) — durable architectural decisions.
- [`engineering-docs/specifications/product/`](engineering-docs/specifications/product/) — product specifications.

## License

DevCapsule is licensed under the [Apache License 2.0](LICENSE). Third-party
components acquired, installed, or used with DevCapsule remain subject to
their respective owners' licenses and terms; see [NOTICE](NOTICE).

## Current Status

The `workflow-type` field in [`.devcapsule/devcapsule.toml`](.devcapsule/devcapsule.toml)
selects the project-memory model. This repository uses `multiple-streams`, so
[`CURRENT-STATUS.md`](CURRENT-STATUS.md) is the open-workstream registry and each
selected track owns its detailed continuation state. Contributors and agents
should follow [`WORKFLOW.md`](WORKFLOW.md) for routing and checkpoint rules;
this README remains the stable developer welcome page.
