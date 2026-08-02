---
id: R-PRODUCT-003
title: Durable Human/Agent Project Memory
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

# R-PRODUCT-003: Durable Human/Agent Project Memory

## Statement

Important requirements, decisions, bugs, validation notes, handoff state, and
next steps should live in repository files rather than only in chat history or
local memory.

## Why This Exists

The workflow must survive model changes, IDE restarts, and session breaks. Repo
state needs to be resumable without reconstructing context from conversation.

## Verification

This is a concrete requirement. It is satisfied when the repository maintains
durable files for project memory and those files are actually used during work.

Verification evidence may include:

- workflow docs that define the project-memory protocol;
- explicitly requested consequential-session records that link back to the
  canonical decisions, requirements, validation, and handoff they influenced;
- handoff state in `README.md`;
- bug, decision, and completed-task records under durable paths.

## Related

- `R-PRODUCT-004`
- `R-PRODUCT-005`
