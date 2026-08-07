# Project Requirements Overview

This file is the project-level overview and index for root requirements. It is
the entry point humans and agents should read first to understand overall
direction, current requirement categories, and where to find the canonical
detail for each item.

The canonical detailed record for each root requirement lives under:

```text
engineering-docs/requirements/product/
```

Each requirement file uses frontmatter plus markdown so the repository remains
the source of truth while preserving a path for later machine-readable
integration with external systems if desired.

Implementation-specific requirements still live in:

- `devcapsule-src/REQUIREMENTS.md` for the active Python CLI/framework.
- `engineering-docs/` for canonical requirements, decisions, design notes,
  implementation evidence, and historical Docker4PyCharm context.

## Requirement Types

This project distinguishes two kinds of requirement records:

- high-level goals: important outcomes that require judgment and accumulated
  evidence rather than a strict pass/fail end-to-end test;
- concrete requirements: capabilities, constraints, or behaviors that are
  testable in principle, even when some verification must be manual.

Goals justify concrete requirements. Concrete requirements operationalize goals.
Tasks, bugs, validations, and completed-task records should reference the
relevant IDs.

## Status Values

- `proposed`: captured, but not yet accepted.
- `accepted`: accepted direction, not yet fully implemented.
- `implemented`: supporting docs or implementation exist, but verification is
  incomplete.
- `validated`: accepted by repository review, static checks, tests, manual
  validation, or explicit project-owner judgment, as appropriate for the item
  type.
- `deferred`: accepted direction, intentionally outside the current target.
- `rejected`: considered and intentionally not pursued.

## Current Overview

Current root requirement emphasis:

- product goals define what kind of development environment and workflow this
  repository is trying to produce;
- documentation and process requirements keep the repo resumable and explicit
  for both humans and agents;
- active implementation work remains tracked in `README.md` and
  `devcapsule-src/REQUIREMENTS.md`.

Current release/stabilization reality:

- the root requirement set is now normalized into one-file-per-item records
  under `engineering-docs/requirements/product/`;
- future work should maintain the overview here and update the detailed item
  files when a requirement changes materially;
- future automation may consume frontmatter from these files, but the repo
  remains the canonical source of truth.

## Root Requirement Index

### Product Goals

- `R-PRODUCT-001` — [Batteries-Included IDE Environments](engineering-docs/requirements/product/r-product-001-batteries-included-ide-environments.md)
- `R-PRODUCT-002` — [Explicit Host Boundaries](engineering-docs/requirements/product/r-product-002-explicit-host-boundaries.md)
- `R-PRODUCT-003` — [Durable Human/Agent Project Memory](engineering-docs/requirements/product/r-product-003-durable-human-agent-project-memory.md)
- `R-PRODUCT-004` — [Reusable Human/Agent Workflow](engineering-docs/requirements/product/r-product-004-reusable-human-agent-workflow.md)

### Workflow And Documentation Requirements

- `R-PRODUCT-005` — [Incremental Human/Agent Execution Loop](engineering-docs/requirements/product/r-product-005-incremental-human-agent-execution-loop.md)
- `R-DOCS-001` — [Root Documentation Stays Implementation-Agnostic](engineering-docs/requirements/product/r-docs-001-root-documentation-stays-implementation-agnostic.md)
- `R-DOCS-002` — [Current User Docs Show Current Interfaces](engineering-docs/requirements/product/r-docs-002-current-user-docs-show-current-interfaces.md)

### Product Adoption And Positioning

- `R-GTM-001` — [Compelling V1 Announcement For Adopters](engineering-docs/requirements/product/r-gtm-001-compelling-v1-announcement-for-adopters.md)

## Maintenance Rules

- Read `REQUIREMENTS.md` first for orientation.
- Read only the detailed files relevant to the current task.
- Keep `REQUIREMENTS.md` concise: overview, grouping, status framing, and links.
- Keep canonical detail in the per-item files under `engineering-docs/requirements/product/`.
- When adding, deleting, renaming, or moving any requirement file, update this
  index and `index.md` in the same change.
