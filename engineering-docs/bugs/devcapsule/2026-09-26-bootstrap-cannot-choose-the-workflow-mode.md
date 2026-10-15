---
status: confirmed
severity: minor
target: none
owner: workflow-improvements
opened: 2026-09-26
requirements: [R-PROC-001, R-PRODUCT-004]
---

# Usability: `bootstrap` never asks which workflow mode the user wants, and a mode without an installed workflow means nothing

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

## Owner direction (2026-09-26)

The owner classifies this as a usability bug and ruled the shape:

1. **When the tooling installs a workflow it asks the user which mode the
   workflow should use, and does the needful.** Interactively, bootstrap
   asks single-stream or multiple-streams; the answer drives everything
   that follows: the declaration table, the reserved workstreams, the
   registry. Unattended runs supply the answer on the command line. No
   silent default.
2. **Without an installed workflow, a `[workflow] mode` setting is void.**
   A project that has no `WORKFLOW.md` has no workflow, not a single-stream
   one. The tooling must not write or infer a mode for such a project, and
   readers of the declaration, `AGENTS.md`'s fallback rules included, must
   not turn a missing definition into "single-stream". `definition = "none"`
   already exists in the declaration vocabulary for a project that runs no
   workflow; a missing `WORKFLOW.md` is that case, whatever the table says.

Consequences for the owner of this record: the installation contract in the
bootstrap specification changes (ask, then declare), the generic definition's
*Workflow Declaration* and the `AGENTS.md` fallback change (no mode without a
definition), and `project init`, which writes the project file before any
workflow exists, must not leave a mode behind. The 2026-09-24 onboarding work
order, which asks when the workflow offer happens, is the same decision seen
from `init`'s side.

## Expected

A first bootstrap asks for the mode, or takes it from a flag in unattended
use, and leaves a complete `[workflow]` table behind, creating the
declaration file when the directory has none. A project without an installed
`WORKFLOW.md` carries no mode, and nothing reads one into it.

## Verification target

Tests in `devcapsule-src/tests/` for: the prompt or flag selecting
`multiple-streams` on a fresh directory produces the reserved workstreams and
the declaration; an unattended run without the answer fails with the remedy;
the declaration file is created when absent; a project with no `WORKFLOW.md`
reports no mode from every reader of the declaration.

## Close criteria

Status `closed` when the direction above is implemented and specified,
the tests pass on `main`, and the owner confirms a fresh multiple-streams
bootstrap from the command line without editing the declaration.
