---
id: R-PYTHON-MVP-003
title: Python MVP Feature Scope
type: requirement
kind: high-level-goal
status: accepted
priority: current stabilization
source_of_truth: repo
verification:
  - judgment
  - task-review
external_refs: []
---

# R-PYTHON-MVP-003: Python MVP Feature Scope

## Statement

The project should refine and settle the feature list for V1 (`python_mvp`).
The scope should distinguish must-have Python MVP behavior from deferred
post-MVP framework work.

## Accepted V1 Scope

- Keep `docker4pycharm/` as the stable compatibility/reference surface for the
  original PyCharm MVP
- Keep `devcapsule pycharm run` as the Python-native day-to-day launcher with
  parity for the documented launch surface
- Remove Python `pycharm run` dependence on historical bootstrap scripts as an
  implementation path
- Replace the delegated PyCharm image builder with a Python-native,
  configuration-neutral build pipeline
- Support editable source install, pinned contributor setup, Nox build gate,
  and local PEX artifact
- Build and validate at least one additional IDE-plus-agent proof point:
  VSCodium plus Claude Code
- Provide acceptable user documentation for supported V1 behavior
- Close obvious quality-gate gaps in the Python project itself
- Keep tests focused on non-GUI-regression-prone behavior

## Explicit V1 Deferrals

- General YAML/JSON profile loading beyond the V1 proof point
- Broader IDE-family adapters beyond the V1 VSCodium plus Claude proof point
- Extension/plugin installation workflows beyond persistent plugin state
- Translating `pycharm check-runtime` and `bootstrap project` away from shell
  delegation
- Formal release automation, signing, checksums, or publishing
- Alternative GUI transports
- GPU/device profiles
- Deferred GitHub SSH/HTTPS remote push validation from the PyCharm v0 pass

## Verification Or Evaluation

- The accepted V1 feature list, deferrals, and likely implementation order are
  recorded here
- On 2026-07-15, the lightweight quality-gate gap around static Python
  typechecking was closed with a `mypy` gate wired into contributor
  dependencies, `nox -s typecheck`, and `nox -s build`
- The root `CURRENT-STATUS.md` handoff should identify the next implementation
  task from
  this scope

## Related

- `R-PYTHON-MVP-001`
- `R-PYTHON-MVP-002`
- `R-IMAGE-BUILD-001`
- `R-FRAMEWORK-001`
- `devcapsule/implementation-notes/bugs/2026-07-13-codium-run-option-parity.md`
