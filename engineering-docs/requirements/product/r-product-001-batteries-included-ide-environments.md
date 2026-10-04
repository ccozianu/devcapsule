---
id: R-PRODUCT-001
title: Batteries-Included IDE Environments
type: requirement
kind: high-level-goal
status: accepted
priority: wanted
source_of_truth: repo
verification:
  - judgment
external_refs: []
---

# R-PRODUCT-001: Batteries-Included IDE Environments

## Statement

The project should produce development environments that include the IDE or
editor surface, common development tools, persistent comfort state, and
agent-ready project context needed for useful work without repeated local
setup.

## Why This Exists

The product is not just a container image. It is meant to be a practical,
resumable development environment that reduces repeated setup and makes both
human and agent work materially easier.

## Evaluation

This is a high-level goal. It is evaluated by judgment against accumulated
evidence across concrete configurations and user workflows rather than by a
single end-to-end pass/fail test.

## Validation Signals

- Concrete implementations document what is included.
- User-facing docs explain what remains external.
- Real project workflows can start without repeated local environment assembly.

## Related

The component-catalog slice implements this goal with optional IntelliJ IDEA
(`java-ide`) and reusable Playwright/Chromium (`browser-automation`). IntelliJ
uses the unified vendor distribution's free core functionality and the bundled
JetBrains Runtime; paid features remain subject to the user's vendor license.
Its configuration, plugins, caches and logs use IntelliJ's own component
namespace. Playwright is additive and does not select or replace an IDE.
The [graphical acceptance scenario](../../development/e2e-tests.md#ai-driven-graphical-acceptance)
exercises a visible saved edit in a fresh capsule and records both deterministic
and model-observed evidence. This is a concrete validation signal, not the
entire high-level goal's pass/fail definition.

- `engineering-docs/decisions/product/d-0001-capability-first-cli-model.md`
- `R-PRODUCT-002`
- `R-PRODUCT-003`
- `R-DOCS-002`
