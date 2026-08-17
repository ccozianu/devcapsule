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
conversation history. Initializing or adopting the mode must create exactly one
reserved `project-management` workstream that owns project-wide priorities,
sequencing, cross-workstream dependencies, and lifecycle decisions, remains
open for the lifetime of the mode, and ends only on migration away from it. Successful integration must be executable as a routine
agent operation while respecting repository policy: prepare and validate a
frozen integration branch, finalize the workstream records, and deliver through
a pull request by default or through explicitly permitted direct-main
integration, without force-pushing `main`. Session startup must select at most
one editing workstream from explicit user intent and registered Git
branch/worktree association, without hidden checkout-local routing state.

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
  `engineering-docs/wip/YYYY-MM-DD-MNEMONIC/CURRENT-STATUS.md`, using its
  immutable ISO start date;
- work handed between workstreams has a defined queue, a delivery route that
  does not wait on the sender's own integration, exactly two disposition
  outcomes, and a completion gate that prevents a workstream from concluding
  while items remain undispositioned;
- exactly one open workstream uses the reserved `project-management` mnemonic,
  is registered like any other, and carries a handoff whose scope, permanent
  lifecycle, branch association, and retirement-on-migration match
  `WORKFLOW.md`; and the agent instructions and the reusable bootstrap template
  require initialization and adoption to create it;
- ended workstreams preserve that directory name under
  `engineering-docs/archive/YYYY-MM-DD-MNEMONIC/`; and
- selection reads the registry from an unambiguous locally accepted mainline
  ref, uses the current branch or a documented exception as the persistent
  local default, leaves `main` and detached or unregistered checkouts
  unselected, and rejects mismatched routing before editing; and
- successful completion requires the finalized tree to be present on remote
  `main`, with pull-request and permitted direct-main delivery rules plus
  conflict, divergence, approval, and unavailable-authority escalation rules
  documented; and
- WIP user documentation cannot be mistaken for current root `docs/` content.

## Related

- `R-PRODUCT-003`
- `R-PRODUCT-004`
- `R-PRODUCT-005`
- [Multiple-stream workflow design](../../design-notes/multiple-stream-workflow.md)
- [Authoritative workflow](../../../WORKFLOW.md)
