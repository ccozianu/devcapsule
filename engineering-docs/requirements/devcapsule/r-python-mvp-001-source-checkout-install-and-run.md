---
id: R-PYTHON-MVP-001
title: Source Checkout Install And Run
type: requirement
kind: concrete-requirement
status: repo-validated
priority: current stabilization
source_of_truth: repo
verification:
  - tests
  - smoke-tests
external_refs: []
---

# R-PYTHON-MVP-001: Source Checkout Install And Run

## Statement

A developer on a Linux workstation with Docker, X11, and Python 3.12+ must be
able to check out the repository, install `devcapsule` from source, and use
`python -m devcapsule` to launch PyCharm with the same core behavior currently
available through the historical shell launcher.

## Implementation

- `devcapsule-src/pyproject.toml`
- `devcapsule-src/requirements.txt`
- `devcapsule-src/dev-requirements.txt`
- `devcapsule-src/devcapsule/cli.py`
- `devcapsule-src/devcapsule/pycharm.py`
- `devcapsule-src/noxfile.py`
- `devcapsule-src/README.md`

## Verification

- 2026-07-07 fresh-venv repository-side validation passed
- 2026-07-08 `nox -s build` became the project build gate
- Additional host-workstation validation remains useful outside the current IDE
  container

## Related

- `R-FRAMEWORK-001`
