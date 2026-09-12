# Workstream Current Status: User Documentation

Mnemonic: `user-docs`

Start date: 2026-09-12

State: open; awaiting owner review of first focus

Integration target: `main`

Delivery method: pull request

Requirements: `R-DOCS-002`, `R-PRODUCT-001`, `R-PRODUCT-002`, `R-PRODUCT-003`

## Goal

Deliver V1 user documentation that lets an adopter understand DevCapsule,
start useful work in a supported development environment, and return to that
work without needing the project's engineering history or a maintainer's help.

The owner authorized opening this workstream on 2026-09-12 and asked to review
its specific initial focus. The first slice below is a recommendation, not an
approved choice of audience, scenario, or implementation.

## Branch Association

Branch prefix: `user-docs/`. No working branch exists yet. Fork the first
working branch from current main after the registration lands. Create
`user-docs/outbox` on first use. The opening is sent by
`project-management/outbox`; the originating checkout remains selected on
`project-management/coordination` until the owner directs a switch.

## Current State

Documentation implementation has not begun. The registration survey found:

- `docs/README.md` points to `devcapsule-src/README.md` for installation and
  usage. Its guides list contains a historical Docker4PyCharm setup guide;
  most other listed content is product positioning.
- `devcapsule-src/README.md` contains current commands but mixes adopter and
  contributor needs. Its opening User Setup starts with a source/virtualenv
  installation; the released executable is explained farther down, alongside
  artifact-building instructions. This is a concrete first-entry problem to
  assess, not evidence that all existing instructions are wrong.
- V1's Human-Readable Workflow Documentation commitment is currently unassigned
  in the project-management scope ledger. The separate One Workflow, Many
  Projects review is assigned to `workflow-improvements`. This registration
  does not transfer that assignment or authorize rewriting the workflow.
- The development-blog decision remains in project-management intake. It is
  distinct from helping someone use the product.

## Proposed First Slice: First Useful Session, Then Resume

Recommended reader: a developer new to DevCapsule, using a supported Linux
workstation and comfortable with Git and a terminal.

Recommended scenario: use one existing, maintained sample project to make the
first result reproducible; adapt an existing personal project afterward. The
owner still needs to choose the project and IDE/agent combination.

The first guide would cover this sequence:

1. Understand what DevCapsule provides and whether the host meets prerequisites.
2. Obtain and verify the released executable through the supported user path.
3. Open the chosen project, understand the host permissions being requested,
   and launch its IDE and selected agent.
4. Complete one small, visible development task with an explicit success check.
5. Exit and return, showing what persists and what the user must do to resume.

**Done means:** one coherent guide, reachable from the user entry point, takes
the chosen reader from prerequisites to the demonstrated result and a resumed
session. Commands match the release actually tested. Expected outcomes,
likely failures, host access, and state persistence are explained where needed.

**Verification:** walk the guide from a fresh environment without undocumented
steps; record the release, host prerequisites, commands, outcomes, and any
manual IDE/agent evidence. Check documentation links and command accuracy.
Have the owner assess clarity and perform GUI checks unavailable to the agent.
Do not claim the journey validated from command inspection alone.

**Reopen if:** release behavior or user testing invalidates a documented step.

The documentation site generator, broad command reference, screenshots, and
full manual structure are later choices unless the chosen journey needs them.
Store new user-document drafts under this workstream's `docs/` directory and
follow WORKFLOW.md's Draft User Documentation rules for existing pages.

## Planned Next Step

Return to the owner to select the first reader, project, and visible success
before drafting the guide. Then, after an explicit workstream selection,
inspect the chosen path against the current release and build a short outline
and validation checklist. Carry relevant product gaps back to project management
instead of silently expanding this documentation slice into implementation.

## Open Threads

- Awaiting the owner: sample versus an existing project, IDE/agent pairing,
  and the useful task that proves the first session succeeded.
- Recommended, not decided: prioritize an end-to-end beginner journey over
  a comprehensive documentation rewrite.
- Dependencies: the first journey documents supported current behavior;
  upcoming component or workflow changes require coordination with their owners.
- No session transcript or session record was requested or created. The initial
  intent and unresolved choices are preserved here.

## Documents

- [Intake](intake/README.md)
- [Disposition log](intake-dispositions.md)

## Source Documents

- [Product documentation index](../../../docs/README.md)
- [CLI installation and usage](../../../devcapsule-src/README.md)
- [Current-interface documentation requirement](../../requirements/product/r-docs-002-current-user-docs-show-current-interfaces.md)
- [V1 scope ledger](../2026-08-09-project-management/v1-scope-ledger.md)
- [Workflow review assignment](../2026-08-09-workflow-improvements/intake/2026-09-11-project-management-one-workflow-many-projects.md)
