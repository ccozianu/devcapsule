---
id: R-PRODUCT-006
title: Multiple Human/Agent Workstream Coordination
type: requirement
kind: concrete-requirement
status: implemented
priority: current
source_of_truth: repo
verification:
  - doc-review
  - repo-inspection
external_refs: []
---

# R-PRODUCT-006: Multiple Human/Agent Workstream Coordination

## Statement

A repository workflow selected for multiple streams must represent every open
workstream explicitly, preserve one independently resumable handoff for each,
associate every non-main branch with exactly one workstream, isolate unfinished
documentation, and define deterministic beginning, development, successful or
unsuccessful completion, integration, and recovery rules without relying on
conversation history.

## Why This Exists

One contributor may alternate between substantial efforts, and several
contributors may develop changes concurrently. A single detailed root handoff
creates conflicts, hides paused work, and makes it unclear which changes and
next task belong together.

The workflow must retain the simplicity of the existing linear model for
projects that do not need concurrency while giving multiple-stream projects
enough structure to remain understandable.

## Verification

This requirement is satisfied when repository inspection shows that:

- `.devcapsule/devcapsule.toml` selects a supported workflow type;
- `WORKFLOW.md` preserves the existing single-stream process and defines the
  multiple-stream restrictions and lifecycle;
- root `CURRENT-STATUS.md` is a compact open-workstream registry in
  multiple-stream mode;
- every open workstream has
  `engineering-docs/wip/MNEMONIC/CURRENT-STATUS.md`;
- ended workstreams use `engineering-docs/archive/MNEMONIC/`; and
- WIP user documentation cannot be mistaken for current root `docs/` content.

## Related

- `R-PRODUCT-003`
- `R-PRODUCT-004`
- `R-PRODUCT-005`
- [Multiple-stream workflow design](../../design-notes/multiple-stream-workflow.md)
- [Authoritative workflow](../../../WORKFLOW.md)
