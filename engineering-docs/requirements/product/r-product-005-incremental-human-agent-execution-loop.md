---
id: R-PRODUCT-005
title: Incremental Human/Agent Execution Loop
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

# R-PRODUCT-005: Incremental Human/Agent Execution Loop

## Statement

The workflow should define a repeatable execution loop for the human and the
agent that favors narrow, testable slices of work; explicit decision points;
concise progress reporting; and durable checkpoints after each meaningful
iteration.

## Why This Exists

Long ambiguous work cycles create avoidable rework. A narrow, explicit loop
improves throughput, validation quality, and resumability.

## Verification

This is a concrete requirement. It is satisfied when workflow docs define the
turn-level choreography and the repository handoff state supports resumption
without relying on chat history.

Verification evidence may include:

- `WORKFLOW.md` defines request framing, slice closure, evidence, reporting,
  escalation, and checkpoint rules;
- the root handoff stays explicit about current next work.

## Related

- `R-PRODUCT-003`
- `R-PRODUCT-004`
