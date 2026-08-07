---
id: R-FRAMEWORK-001
title: Shared Python DevCapsule Orchestration
type: requirement
kind: high-level-goal
status: implemented
priority: current stabilization
source_of_truth: repo
verification:
  - repo-inspection
  - tests
external_refs: []
---

# R-FRAMEWORK-001: Shared Python DevCapsule Orchestration

## Statement

The post-MVP implementation should refactor one-off IDE launcher logic into a
shared Python `devcapsule` framework with reusable runtime orchestration,
profile loading, IDE-family adapters, and thin compatibility wrappers.
Under adopted D-0001, the shared framework also owns capability resolution,
configuration overlays, platform locks, checkout-local resolution, state
contracts, and host-access authorization; IDE adapters remain thin.

## Implementation

- `devcapsule-src/pyproject.toml`
- `devcapsule-src/devcapsule/cli.py`
- `devcapsule-src/devcapsule/__main__.py`
- `devcapsule-src/devcapsule/configurations/pycharm/`
- `devcapsule-src/noxfile.py`
- `devcapsule-src/devcapsule/commands/`
- `devcapsule-src/tests/test_cli.py`
- `devcapsule-src/devcapsule/project.py`
- `devcapsule-src/tests/test_project.py`

## Verification Or Evaluation

- 2026-07-03 initial editable-install and pytest validation passed
- 2026-07-05 translated Python `pycharm run` path replaced Bash forwarding
- 2026-07-05 Click/Typer command-tree migration validated
- 2026-07-07 ergonomics and packaging-contract slices validated
- 2026-07-08 Nox build orchestration and class-backed Click discovery
  validated

## Related

- `engineering-docs/decisions/product/d-0001-capability-first-cli-model.md`
- `engineering-docs/design-notes/docker4pycharm/future-agent-refactoring-brief.md`
- root `README.md`
