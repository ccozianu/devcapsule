---
status: confirmed
severity: minor
target: none
owner: workflow-improvements
opened: 2026-09-26
requirements: [R-PROC-001, R-PRODUCT-004]
---

# `bootstrap` installs single-stream by default and offers no way to choose the mode

The owner bootstrapped a fresh project outside the capsule with plain
`devcapsule bootstrap`. It reported "Bootstrapped single-stream DevCapsule
workflow" and rewrote `.devcapsule/devcapsule.toml` with that mode. Nothing
asked which mode the project wanted; `--help` shows no option for it. The
only way to get `multiple-streams` is to know to edit the declaration by hand
before running, and a project bootstrapped single-stream by default then
needs the adoption procedure to change.

## Evidence

- `bootstrap --help` at `v0.2.14`: options are `--project` and
  `--refresh-workflow-definition` only.
- `project_workflow_declaration` in `devcapsule-src/devcapsule/workflow_bootstrap.py`
  reads the mode from the declaration and defaults to `single-stream`;
  `_reconcile_declaration` then writes the `[workflow]` table with that mode,
  and only when the declaration file already exists. Probe inside this
  capsule on a directory with no `.devcapsule/devcapsule.toml`: bootstrap
  created the workflow files and no declaration at all, leaving the project
  undeclared, which the definition treats as unversioned.
- The specification `engineering-docs/specifications/product/project-workflow-bootstrap.md`,
  *Installation Contract*, says exactly this: read `workflow-type`, a
  missing field means `single-stream`. The code follows the specification;
  the gap is the product contract, not a deviation from it.

## Why it is filed as a bug and not only as a work item

The 2026-09-24 work order on workflow onboarding already asks how mode and
definition choices are expressed for interactive and unattended use. This
record adds the observed consequence for a first session: a defaulted choice
the user never made, reported as if made, and a silent absence of the
declaration when no project file exists yet. The work order's owner decides
the shape; this record is the evidence and the close criterion.

## Expected

A first bootstrap either asks for the mode, with the single-stream default
stated as a default, or takes it from a flag such as `--mode`, and always
leaves a complete `[workflow]` table behind, creating the declaration file
when the directory has none. Unattended runs need the flag or the declared
value; a bare run on an undeclared directory should not silently pick.

## Verification target

Tests in `devcapsule-src/tests/` for: the flag or prompt selecting
`multiple-streams` on a fresh directory produces the reserved workstreams and
the declaration; a bare unattended run on an undeclared directory either
fails with the remedy or declares the default explicitly, as the owner
decides; the declaration file is created when absent.

## Close criteria

Status `closed` when the owner-decided shape is implemented and specified,
the tests pass on `main`, and the owner confirms a fresh multiple-streams
bootstrap from the command line without editing the declaration.
