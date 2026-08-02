# DevCapsule

[![Tests](https://github.com/ccozianu/ChatGpt_Codex/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/ccozianu/ChatGpt_Codex/actions/workflows/tests.yml)
[![Coverage](docs/badges/coverage.svg)](https://github.com/ccozianu/ChatGpt_Codex/actions/workflows/tests.yml)

DevCapsule creates reproducible, resumable development environments for humans
and AI coding agents. It combines a real IDE, agent-ready development tooling,
versioned project memory, and explicit boundaries around access to the host.

The active implementation is the Python package and CLI in `devcapsule/`.
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

- `devcapsule/` — active Python CLI/framework, tests, packaging, and runtime
  assets.
- `docs/` — product requirements, specifications, decisions, and positioning.
- `docker4pycharm/` — historical shell-based PyCharm MVP and reference
  material; it is not the source of the active implementation.
- `.devcapsule/` — this project's capability declaration and platform lock.

## Developer Setup

The Python project uses Nox as its primary validation entry point. From the
repository root:

```text
cd devcapsule
python -m nox -s tests
```

Run the full local gate before handing off implementation changes:

```text
cd devcapsule
python -m nox -s build
```

The full gate includes compilation, shell syntax checks, pytest, type checks,
CLI smoke tests, PEX construction, and PEX smoke tests. It always creates the
local-only `dist/devcapsule-local.pex`. On a clean repository it also creates
and smoke-tests the public-source `dist/devcapsule.pex`; on a dirty repository
it explicitly reports that the public artifact was skipped. To deliberately
discard cached Nox environments, add `--no-reuse-existing-virtualenvs`.

For CLI installation and usage, see [`devcapsule/README.md`](devcapsule/README.md).

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
- [`docs/decisions/`](docs/decisions/) — durable architectural decisions.
- [`docs/specifications/`](docs/specifications/) — product specifications.

## License

DevCapsule is licensed under the [Apache License 2.0](LICENSE). Third-party
components acquired, installed, or used with DevCapsule remain subject to
their respective owners' licenses and terms; see [NOTICE](NOTICE).

## Current Status

Detailed progress, validation evidence, open work, and the planned next step
are maintained in [`CURRENT-STATUS.md`](CURRENT-STATUS.md). Contributors and
agents should update that handoff file as project state changes; this README is
the stable developer welcome page and should change only when developer-facing
project information changes.
