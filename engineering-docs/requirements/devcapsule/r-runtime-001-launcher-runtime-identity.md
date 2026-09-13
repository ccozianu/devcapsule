---
id: R-RUNTIME-001
title: Identical Launcher And Container Runtime By Default
type: requirement
kind: concrete-requirement
status: accepted
priority: current stabilization
source_of_truth: repo
verification:
  - tests
  - e2e
external_refs: []
---

# R-RUNTIME-001: Identical Launcher And Container Runtime By Default

## Statement

Unless the user explicitly chooses otherwise, the DevCapsule CLI must use
the corresponding base selected by project/platform resolution and install
its own executable into the materialized environment. The launcher outside
Docker and runtime support inside Docker must be byte-identical.

A launcher change must not reuse a cached environment carrying a different
runtime executable. Selecting a different base alone does not imply selecting
a different runtime. The base and CLI need not have matching release numbers.

Explicit user overrides are permitted. This requirement does not prescribe a
new command spelling or make such an override implicit.

## Rationale

The owner adopted this default in
[D-0009](../../decisions/product/d-0009-launcher-delivers-identical-runtime.md)
after the successful v0.2.11 implementation. It removes the base/CLI content
dependency cycle and keeps runtime-plan production and execution in one build.

## Implementation And Limits

- `devcapsule/runtime_artifact.py` selects the invoking packaged executable.
- `devcapsule/materialization.py` installs it at
  `/opt/devcapsule/bin/devcapsule.pex` and incorporates its SHA-256 in the
  formation descriptor. The shared base is not modified in place.
- Source-form launchers can explicitly select a built PEX using
  `DEVCAPSULE_RUNTIME_PEX`; running that PEX directly gives the ordinary
  identical-executable path. Source Python files are not themselves a PEX.
- The packaged launcher currently takes precedence over
  `DEVCAPSULE_RUNTIME_PEX`. That variable is a source-development selection,
  not a general packaged-launcher runtime override. No new override interface
  is implemented by recording this decision.

## Verification

Existing coverage for the default, delivered with v0.2.11:

- `tests/test_runtime_artifact.py` checks executable selection, explicit
  source-runtime selection, and formation identity changing with runtime bytes.
- `tests/e2e/test_component_cache.py` checks the installed executable's SHA-256,
  image label, runtime invocation, and inside/outside version metadata for both
  fixture surface families.

Future changes must preserve these properties. Any additional override
interface needs its own explicit-selection and default-regression coverage;
this record does not claim that interface has been validated.
