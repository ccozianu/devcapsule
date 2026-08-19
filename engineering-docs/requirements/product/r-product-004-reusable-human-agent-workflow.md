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

The workflow is not required to be complete. It must state that it is
incomplete, tell adopters what to do where it is silent, and give them a route
for returning what they discover, so that underspecification degrades into
recorded findings rather than into blocked work or silent divergence between
projects that believe they share a protocol.

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
- target repositories can choose the linear or multiple-workstream protocol in
  committed project metadata;
- template/bootstrap material teaches the same structure future adopters are
  expected to use;
- the workflow states its own incompleteness, distinguishes silence from
  express denial, and requires exercised latitude to be recorded; and
- adopters have a defined route for returning gaps they discover;
- adopting the workflow does not require an adopter to stop using an issue
  tracker they already have, and nothing in it assumes the tracker's absence;
  and
- minimum viable adoption is small enough to state in a sentence — the agent
  entry point plus the one record it keeps current — with the rest of the
  protocol reachable as depth rather than required reading. Added 2026-08-19,
  because a workflow whose entry cost is nineteen terms and 1,838 lines is not
  adoptable however good its content is.

## Related

- `R-PRODUCT-003`
- `R-PRODUCT-005`
- `R-PRODUCT-006`
