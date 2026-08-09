---
id: R-DOCS-001
title: Generated Documentation Index
type: requirement
kind: high-level-goal
status: accepted
priority: later
source_of_truth: repo
verification:
  - judgment
external_refs: []
---

# R-DOCS-001: Generated Documentation Index

## Statement

The repository should eventually generate `index.md` from structured markdown
frontmatter so the documentation map stays consistent as files are added,
deleted, renamed, moved, or recategorized.

## Implementation

- Current manual index: root `index.md`
- Current maintenance instruction: `AGENTS.md`

## Verification Or Evaluation

- Future validation should confirm required frontmatter fields and that the
  generated `index.md` matches the committed file

## Related

- `R-PROC-001`
