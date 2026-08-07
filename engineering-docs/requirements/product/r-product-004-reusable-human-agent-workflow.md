---
id: R-PRODUCT-004
title: Reusable Human/Agent Workflow
type: requirement
kind: high-level-goal
status: accepted
priority: current
source_of_truth: repo
verification:
  - judgment
  - doc-review
external_refs: []
---

# R-PRODUCT-004: Reusable Human/Agent Workflow

## Statement

The human/agent development workflow used to build this repository should
itself be available to users of Dockerized environments created by this project
when they choose that mode.

## Why This Exists

The workflow is part of the product idea, not just an internal convenience.
Users should be able to adopt the same resumable, evidence-based collaboration
shape in their own repositories.

## Evaluation

This is a high-level goal. It is evaluated by whether the workflow is
documented clearly enough to be bootstrapped into other projects and remains
useful in practice.

## Validation Signals

- environment implementations provide or document a bootstrap path;
- root workflow docs are generic enough to transfer;
- template/bootstrap material teaches the same structure future adopters are
  expected to use.

## Related

- `R-PRODUCT-003`
- `R-PRODUCT-005`
