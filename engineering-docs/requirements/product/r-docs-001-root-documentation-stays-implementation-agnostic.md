---
id: R-DOCS-001
title: Root Documentation Stays Implementation-Agnostic
type: requirement
kind: concrete-requirement
status: implemented
priority: current
source_of_truth: repo
verification:
  - doc-review
external_refs: []
---

# R-DOCS-001: Root Documentation Stays Implementation-Agnostic

## Statement

Root markdown files and top-level `docs/` should describe project purpose,
product positioning, workflow, and current handoff without embedding
implementation-specific shell, Python, or Docker details that belong to a
subproject.

## Why This Exists

The repository root should orient readers without forcing them to separate
historical details from the active implementation.

## Verification

This is a concrete requirement. It is satisfied when root docs stay at the
project level and route implementation-specific readers into the relevant
subproject.

Verification evidence may include:

- `index.md` routes readers to subproject docs;
- root docs avoid presenting subproject details as the main project interface;
- markdown moves or additions keep the documentation index current.

## Related

- `R-DOCS-002`
