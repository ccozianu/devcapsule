# Workflow Change Proposal: Multiple Workstreams

Status: proposed for discussion; not yet adopted

Date: 2026-08-07

Scope: repository workflow and reusable DevCapsule project-memory model

Related requirements: `R-PRODUCT-003`, `R-PRODUCT-004`, `R-PRODUCT-005`

Related discovery input:
[FastAPI web application configuration research](fastapi-webapp-configuration-research.md)

## Summary

The current human/agent workflow assumes that development proceeds through one
active milestone, one current slice, and one next step. That model has worked
for the mostly linear DevCapsule dogfood effort, but it does not adequately
represent either of these ordinary situations:

- two or more contributors work on different concerns in the same repository;
- one contributor pauses one coherent effort and starts or resumes another.

The immediate example is the recursive dogfood E2E milestone and the proposed
FastAPI, React, and PostgreSQL demo effort. The E2E milestone has a precise
resumption point at Stage 4, while the demo may proceed independently and may
drive new DevCapsule functionality. Treating either effort as the repository's
single next step would hide important state about the other.

This proposal introduces a repository-level portfolio handoff plus one durable
handoff per workstream. It pairs those committed records with separate Git
branches and worktrees for execution isolation. The proposal deliberately does
not prescribe CLI automation yet; the repository convention should be
dogfooded before DevCapsule turns it into a product interface.

## Problem

`CURRENT-STATUS.md` currently serves several different roles at once:

1. repository-wide validated state;
2. active release and milestone selection;
3. detailed milestone evidence;
4. the current session's continuation point; and
5. the next task an agent should execute.

Those roles are compatible when work is linear. With parallel workstreams,
they create several problems.

### A central edit hotspot

Every meaningful checkpoint updates the same file. Contributors working on
unrelated tracks are therefore likely to create textual conflicts even when
their implementation changes do not overlap.

### Lossy pause and resume

Replacing the root next step when priorities change can make a paused effort
look completed, abandoned, or obsolete. Keeping every detail in the root file
instead makes the handoff grow into an undifferentiated backlog.

### Ambiguous agent routing

An agent instructed to read one global next step cannot distinguish among:

- the repository's highest-level priority;
- the workstream associated with its current branch or worktree;
- a track explicitly selected by the user; and
- another contributor's concurrently active track.

### Hidden integration risk

Independent workstreams may modify common contracts even when their immediate
goals differ. Without a small coordination surface, contributors discover the
overlap only during merge or validation.

### Branch-relative truth

Git commits provide durable checkpoints, not live contributor presence. A
status record committed on one branch is not automatically current in another
checkout. The workflow must not pretend that committed Markdown is a locking
or real-time coordination service.

## Goals

The changed workflow should:

- make all open workstreams discoverable from a stable repository entry point;
- preserve an exact, independently resumable handoff for each workstream;
- distinguish active, paused, blocked, integrating, and completed work;
- let the user or repository context select the workstream for a session;
- make cross-workstream dependencies and integration risks visible;
- reduce routine contention on `CURRENT-STATUS.md`;
- preserve the existing narrow, evidence-driven slice loop within each track;
- work for one contributor using several worktrees and for several
  contributors using branches or pull requests; and
- remain useful as a reusable workflow that DevCapsule can later bootstrap
  into other repositories.

## Non-Goals

This initial workflow change should not:

- implement a real-time presence, locking, or task-assignment system;
- replace Git branches, worktrees, pull requests, or contributor communication;
- impose exclusive ownership of source files;
- require a DevCapsule CLI command before the convention has been dogfooded;
- copy detailed plans, requirements, decisions, or bug evidence into status
  files; or
- make session records a source of canonical current state.

## Proposed Repository Structure

```text
CURRENT-STATUS.md
engineering-docs/
  workstreams/
    README.md
    recursive-dogfood-e2e.md
    fastapi-demo.md
```

`CURRENT-STATUS.md` remains the mandatory repository-level entry point. It
becomes a portfolio handoff rather than the detailed handoff for one selected
track.

`engineering-docs/workstreams/README.md` defines the schema, lifecycle, and
agent-routing rules. Each other file under `engineering-docs/workstreams/` is
the canonical handoff for one workstream. Existing execution plans,
requirements, decisions, bug notes, and validation records remain in their
current locations and are linked rather than copied.

The directory and exact placement are part of this proposal, not an adopted
decision. A subproject-local workstream directory is a viable alternative if
dogfooding shows that repository-wide placement mixes unrelated subprojects.

## Repository-Level Portfolio Handoff

The root `CURRENT-STATUS.md` should contain only information that a contributor
needs before selecting a workstream:

- project and release-wide baseline;
- a compact table of open workstreams;
- each workstream's lifecycle state, branch or integration reference, and
  linked handoff;
- repository-wide external state or safety constraints;
- cross-workstream dependencies and integration ordering that cannot belong to
  one track alone; and
- shared validated evidence that every track may rely upon.

It should not contain one repository-wide `Next Step` when several workstreams
are independently actionable. Each workstream row may show a short next
checkpoint, while the linked handoff owns the exact next slice.

An illustrative table is:

| Workstream | State | Branch | Next checkpoint | Handoff |
|---|---|---|---|---|
| Recursive dogfood E2E | paused | `milestone/recursive-dogfood-e2e` | Begin Stage 4 | linked track file |
| FastAPI demo | active | workstream branch to be selected | Define executable demo contract | linked track file |

This table is illustrative only. This proposal does not change either
workstream's current canonical status.

## Workstream Handoff Contract

Each workstream handoff should be concise enough to read at the start of every
session and complete enough to resume without chat history.

Recommended metadata and sections are:

```markdown
---
id: stable-workstream-id
title: Human-readable title
state: proposed | active | paused | blocked | integrating | complete
kind: milestone | discovery | feature | maintenance
branch: optional-portable-branch-reference
base-revision: optional-full-commit
last-updated: YYYY-MM-DD
requirements:
  - R-...
depends-on:
  - other-workstream-id
---

# Workstream: ...

## Outcome
## Scope And Non-Goals
## Current State
## Evidence
## Current Or Last Slice
## Next Resumable Slice
## Cross-Workstream Dependencies
## Integration Risks And Conditions
## External State
## References
```

The record may omit empty sections, but it must always identify the intended
outcome, lifecycle state, current evidence, and next resumable slice.

Absolute local worktree paths, credentials, personal tokens, and other
machine-specific secrets must not be committed. A portable branch reference
and exact base revision are appropriate when they improve resumption or
integration safety.

## Lifecycle Semantics

- `proposed`: captured for consideration, but execution has not been selected.
- `active`: independently actionable work is being pursued; more than one
  workstream may be active when contributors operate concurrently.
- `paused`: intentionally preserved with a known continuation point; it is not
  blocked, abandoned, or complete.
- `blocked`: cannot make meaningful progress until a recorded condition
  changes.
- `integrating`: track-local work is sufficiently complete and its current
  concern is safe integration and cross-track validation.
- `complete`: the outcome and integration conditions are satisfied, with
  evidence recorded or linked.

Completion removes a workstream from the open-workstream table but does not
require moving or renaming its handoff immediately. Preserving the stable path
avoids unnecessary documentation churn and retains historical links.

## Workstream Selection And Agent Routing

At the start of work, an agent should:

1. read the repository brief and portfolio handoff;
2. select a workstream explicitly named by the user when one is named;
3. otherwise match the current branch or worktree to an open workstream;
4. read that workstream's handoff and directly referenced execution material;
5. inspect other open workstreams for declared dependencies and integration
   risks;
6. state the selected workstream and next narrow slice before proceeding; and
7. ask the user to select a track only if several remain plausible and the
   choice materially changes the work.

A contributor's momentary focus should not be stored as one global repository
fact. User intent and checkout context select the session; the committed files
preserve durable workstream state.

Routine progress updates should modify the selected workstream handoff, not
the root portfolio. The portfolio should change when a workstream is opened,
paused, resumed, blocked, moved to integration, completed, or introduces a
repository-wide coordination fact.

## Branch And Worktree Model

The recommended execution model is one branch and Git worktree per active or
paused workstream when the tracks need independent source state.

```text
workstream
    -> Git branch and worktree
    -> DevCapsule checkout registration
    -> checkout-scoped IDE, cache, and agent state
```

This provides several useful boundaries:

- pausing one workstream does not require stashing another;
- dirty or generated files do not contaminate evidence for another milestone;
- each DevCapsule checkout can retain independent project and agent state;
- source overlap is reviewed during integration rather than accidentally
  combined during implementation; and
- a contributor can close or suspend one IDE environment without losing the
  other track's durable handoff.

A branch name recorded in a workstream file is a routing aid, not proof that a
contributor is actively working. Local worktree locations should be discovered
with Git or DevCapsule rather than committed.

When multiple contributors work on the same track, they may still use multiple
branches or pull requests. The workstream handoff describes their shared
outcome and latest durable checkpoint; it does not replace ordinary source
integration practices.

## Cross-Workstream Coordination

Each active workstream should identify, at an appropriate level:

- other workstreams it consumes or depends upon;
- contracts, components, documentation, or tests it is likely to affect;
- outputs another workstream expects from it;
- known merge or validation order; and
- evidence that must be rerun after integration.

These declarations are awareness aids, not source-file locks. Contributors
should use actual branch diffs to verify overlap. Lists of anticipated surfaces
should remain coarse and should not become a manually maintained inventory of
every changed file.

For the motivating example, the FastAPI demo may drive component runtime-path,
Claude component, ecosystem-bootstrap, service, port, and networking changes.
The recursive E2E milestone owns clean-source, PEX, base-image, and successor
formation evidence. Both tracks may affect image formation or runtime-plan
contracts, so their integration conditions should make that overlap visible
before merge.

## Requirement Impact

The existing requirements cover durable memory, reusable workflow, and a
narrow incremental execution loop, but none explicitly requires coordination
among several loops.

If this workflow direction is adopted, add a proposed concrete root
requirement such as:

`R-PRODUCT-006: Parallel Human/Agent Workstream Coordination`

Candidate statement:

> A repository workflow should represent multiple active or paused
> workstreams, preserve an independently resumable handoff for each, route
> humans and agents to the selected workstream, and expose cross-workstream
> dependencies and integration risks without relying on conversation history.

`R-PRODUCT-005` would continue to define execution within one workstream. The
new requirement would define coordination among several workstreams. The
existing DevCapsule `R-CONC-001` concerns concurrent runtime sessions and
should not be overloaded with source-workflow coordination.

Because the resulting convention is intended to be bootstrapped into other
repositories, adoption would also influence the evaluation of
`R-PRODUCT-004` and the reusable workflow assets distributed by DevCapsule.

## Documentation And Index Consequences

One-file-per-workstream reduces contention on `CURRENT-STATUS.md`, but adding
Markdown files still touches the central `index.md` under the repository's
current documentation policy. This is a smaller and less frequent conflict,
but it is not eliminated.

If concurrent dogfooding makes the documentation index a recurring merge
hotspot, the repository should reconsider the priority of its deferred
generated-index work. A generated or mechanically validated index could make
those conflicts procedural rather than semantic. That question is outside the
initial workflow convention.

## Product Automation Direction

After the repository convention has been exercised, DevCapsule could provide
optional assistance such as:

- discover and list workstreams from their metadata;
- show the workstream associated with the current checkout;
- create a branch, worktree, and initial handoff together;
- register the new worktree as a DevCapsule checkout;
- report dependencies or overlapping changed surfaces;
- render a repository portfolio summary; and
- validate that every open workstream has a resumable next slice.

The CLI shape and command names should be selected only after the manual model
has produced evidence. Repository Markdown and Git remain the source of truth;
automation should help maintain and inspect them rather than introduce an
unrelated task database.

## Alternatives Considered

### Keep one expanded `CURRENT-STATUS.md`

This preserves one obvious entry point but retains the central conflict
surface, encourages an ever-growing active backlog, and makes independent
pause/resume state harder to review.

### Keep status only on workstream branches

This gives each track an independent checkpoint but provides no repository
portfolio view. A new contributor cannot discover all open tracks without
enumerating branches and knowing where to look.

### Use only issues or an external project tracker

External tools provide stronger live coordination and assignment features,
but they weaken the repository-local, offline, agent-readable memory contract.
They may supplement the committed workflow, especially for live presence, but
should not be required to reconstruct durable status.

### Treat every workstream as a separate repository

This is appropriate when the effort has an independent product and release
lifecycle. It is excessive when several tracks intentionally modify the same
codebase or must integrate before one release.

### Store one status file per contributor

Contributor files describe people rather than outcomes, become stale when work
is handed off, and make it difficult to determine the canonical state of a
shared effort. Workstreams should be organized around outcomes; contributors
and branches remain execution details.

## Risks And Open Questions

- How much repository-wide evidence should remain in `CURRENT-STATUS.md`
  rather than live in the workstream that produced it?
- Should workstream files remain repository-wide under
  `engineering-docs/workstreams/`, or should that directory contain
  subproject-specific namespaces?
- Should branch association be one exact branch, a list of branches, or an
  optional convention inferred from naming?
- When several contributors share one workstream, who updates its canonical
  checkpoint and how frequently should branches integrate that update?
- Should completed workstreams retain their original location indefinitely or
  later move to an archive through a deliberate cleanup?
- At what point does mechanical rendering or validation of the portfolio and
  documentation index become worthwhile?
- Which parts of the convention belong in the generic workflow template and
  which are DevCapsule-repository-specific?

## Proposed Dogfood Sequence

If the direction is accepted, use the current situation to test it in small
steps:

1. Adopt the workstream lifecycle and minimal handoff schema.
2. Add the workstream directory and its workflow README.
3. Convert `CURRENT-STATUS.md` into a portfolio handoff.
4. Extract the recursive dogfood E2E state into one workstream record without
   changing its technical status or planned Stage 4 continuation.
5. Add a FastAPI demo workstream linked to the existing configuration plan.
6. Update `AGENTS.md` and `WORKFLOW.md` with deterministic workstream routing.
7. Save a clean shared checkpoint before creating another worktree.
8. Create a separate FastAPI branch and worktree while leaving the recursive
   E2E source and external evidence intact.
9. Dogfood pause, resume, concurrent awareness, and later integration.
10. Decide whether repository validation or DevCapsule CLI assistance is
    justified by the observed friction.

## Acceptance Criteria For The Workflow Change

The proposal should be considered successfully validated when:

- a new session can discover both the paused E2E track and active FastAPI
  track from the repository entry point;
- either track can be resumed without reading the other track's full history;
- routine progress on one track does not edit the other track's handoff;
- an agent correctly selects a track from explicit user intent or checkout
  context;
- cross-track dependencies and shared validation obligations are visible
  before integration;
- separate worktrees preserve clean and independent source state;
- completed or paused work is not mistaken for the repository's current next
  action; and
- the convention remains understandable without a DevCapsule-specific status
  database or external conversation history.

## Decision Needed

This document records a proposal only. Adoption requires the project owner to
choose at least:

1. whether to adopt portfolio-plus-workstream handoffs;
2. where canonical workstream files should live;
3. whether to add the proposed parallel-workstream requirement; and
4. whether to dogfood the convention before adding any CLI automation.

Until that decision is made and propagated, `CURRENT-STATUS.md`, `WORKFLOW.md`,
`AGENTS.md`, and the current requirement records remain authoritative and
unchanged.
