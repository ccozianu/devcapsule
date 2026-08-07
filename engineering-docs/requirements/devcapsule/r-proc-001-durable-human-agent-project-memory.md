---
id: R-PROC-001
title: Durable Human/Agent Project Memory
type: requirement
kind: concrete-requirement
status: implemented
priority: MVP
source_of_truth: repo
verification:
  - doc-review
  - repo-inspection
external_refs: []
---

# R-PROC-001: Durable Human/Agent Project Memory

## Statement

Project requirements, active tasks, bug evidence, decisions, validation status,
and handoff state must live in repository files rather than only in
conversation history.

## Implementation

- `WORKFLOW.md`
- root `REQUIREMENTS.md`
- `AGENTS.md`
- `docker4pycharm/image-assets/vibe-coding-process.md`
- `docker4pycharm/bootstrap-project.sh`

## Verification

- Future sessions should verify that active tasks and bug records cite
  requirement IDs where applicable

## Related

- Root `R-PRODUCT-003`
