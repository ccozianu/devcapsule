---
id: R-PYTHON-MVP-002
title: Single-File Python CLI Artifact
type: requirement
kind: concrete-requirement
status: manually validated
priority: current stabilization
source_of_truth: repo
verification:
  - smoke-tests
  - manual
external_refs: []
---

# R-PYTHON-MVP-002: Single-File Python CLI Artifact

## Statement

Python MVP should provide an end-user distribution path that does not require
users to create a virtual environment or understand editable installs. A
release build should produce a single executable Python archive that exposes
the same `devcapsule` CLI entry point.

## Implementation

- `devcapsule-src/scripts/build-pex.sh`
- `devcapsule-src/pyproject.toml`
- `devcapsule-src/dev-requirements.txt`
- `devcapsule-src/devcapsule/assets/docker4pycharm/`
- `devcapsule-src/noxfile.py`
- `devcapsule-src/README.md`

## Verification

- 2026-07-07 repository-side PEX validation passed
- 2026-07-08 `nox -s build` included PEX build and smoke checks
- 2026-07-08 user confirmed host smoke validation for PEX PyCharm run
- 2026-07-10 user confirmed host smoke validation for PEX `pycharm build`

## Related

- `R-PYTHON-MVP-001`
- `R-FRAMEWORK-001`
