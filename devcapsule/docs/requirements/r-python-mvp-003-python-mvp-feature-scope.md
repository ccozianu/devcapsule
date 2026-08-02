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
- Publish official, semantically versioned V1 artifacts under the
  organization-owned namespace. At minimum this includes the supported base
  image and distributable PEX with immutable digests/checksums, real source
  revision metadata, a basic documented security scan, and clean pull/download
  validation.
- Make the public source revision inspectable from both published image
  metadata and the PEX itself. The image must carry the full commit in standard
  OCI source/revision annotations plus DevCapsule metadata; the PEX must embed
  and expose the same full commit and canonical public GitHub commit URL
  without relying on the source checkout. Release validation must compare the
  two values and reject placeholders such as `unknown`. This is transparent
  traceability, not cryptographic build provenance.
- Support both V1 base-trust paths: an explicit managed base built and selected
  by the developer, and developer-owned authorization of one exact published
  registry digest recommended by a project lock. Mutable tags and blanket
  repository or publisher trust are not authorization.
- Keep V1 default bases agent-neutral. Agent CLIs are explicit optional
  materialized components with independent acquisition, version, state,
  licensing, and trust contracts. Antigravity CLI is the first planned V1
  component; it is not downloaded or installed until that task is implemented
  and reviewed.

## Explicit V1 Deferrals

- General YAML/JSON profile loading beyond the V1 proof point
- Broader IDE-family adapters beyond the V1 VSCodium plus Claude proof point
- Extension/plugin installation workflows beyond persistent plugin state
- Translating `pycharm check-runtime` and `bootstrap project` away from shell
  delegation
- Verifiable supply-chain provenance, signed SBOMs, cryptographic artifact
  signatures, build attestations, automated provenance/policy enforcement, and
  fully automated release orchestration beyond the checksums, source metadata,
  and basic security scan required for the manually validated V1 artifacts
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
