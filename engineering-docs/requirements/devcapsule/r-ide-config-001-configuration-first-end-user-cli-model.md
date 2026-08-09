---
id: R-IDE-CONFIG-001
title: Capability-First End-User CLI Model
type: requirement
kind: concrete-requirement
status: accepted
priority: current stabilization
source_of_truth: repo
verification:
  - tests
  - smoke-tests
external_refs: []
---

# R-IDE-CONFIG-001: Capability-First End-User CLI Model

## Statement

End users should declare portable capabilities in
`.devcapsule/devcapsule.toml`, commit the matching platform lock, and normally
launch through:

```text
devcapsule run
```

The resolver selects curated concrete components from the abstract capability
set. Project recommendations cannot grant host access; effective host
authorization remains developer-owned. `devcapsule run-image IMAGE` is the
legacy, compatibility, dogfood, and recovery escape hatch.

## Transition

The currently implemented `devcapsule CONFIGURATION ACTION` surface is the
pre-V1 model superseded in direction by adopted D-0001. It remains available
while the capability-first manifest, platform lock, checkout resolution, and
shared runtime planner are implemented.

## Implementation

- `devcapsule-src/README.md`
- `devcapsule-src/devcapsule/commands/`
- `devcapsule-src/devcapsule/configurations/`

## Verification

- `devcapsule-src/tests/test_cli.py`
- `nox -s build` smoke tests source and PEX help surfaces

## Related

- `engineering-docs/decisions/product/d-0001-capability-first-cli-model.md`
- `R-PYTHON-MVP-001`
- `R-PYTHON-MVP-002`
- `R-PYTHON-MVP-003`
- `R-FRAMEWORK-001`
