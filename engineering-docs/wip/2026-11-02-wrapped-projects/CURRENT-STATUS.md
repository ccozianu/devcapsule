# Workstream Current Status: Wrapped Projects

Mnemonic: `wrapped-projects`

Start date: 2026-11-02

State: active; opened 2026-11-02 at the owner's direction; design and the JDK experiment in progress

Definition read: WORKFLOW.md@635ed43f2fde, WORKFLOW-LOCAL.md@fb8d8f100502

Branch association: `ws-wrapped-projects/wrap`, forked from `origin/main` at 31d44fa473a8

Integration target: `main`

Delivery method: pull request, merge commit, under the Pair Review Loop with Codex as the review partner

Requirements: R-CONFIG-001, R-SCOPE-001; a new requirement for the wrapped-project shape is a deliverable

Work order: [wrapped projects](../../work-orders/2026-11-02-wrapped-projects.md), issued 2026-11-02 by the owner and accepted as this workstream's goal

## Goal And Scope

Let a developer wrap a foreign repository, one that is not theirs and carries no DevCapsule
configuration, in a small wrapper repository of their own, as a submodule, and work on it in a
capsule with three commands. The showcase is an FRC learning project around Mechanical-Advantage's
public robot code. The work order holds the owner's rulings; this file holds the state.

## Current State

**2026-11-02, opened.** The owner described the feature and ruled on its shape in conversation.
The work order records the rulings. Preparation evidence from inside the 0.3.0 capsule:

- A shallow clone of RobotCode2025Public, Gradle 8.11 through its wrapper, under the capsule's
  Temurin 25.0.4+7: `BUILD FAILED`, `Unsupported class file major version 69` during the
  build script's semantic analysis, before any Java compiled. Exit 1 after 2m 5s, most of it
  the Gradle download.
- The same build under a Temurin 17 downloaded into the session scratch: in progress when
  this file was written; the result is recorded below when it lands.

## Next Resumable Task

1. Record the Temurin 17 build result here.
2. Write `2026-11-02-design-wrapped-source.md`: the manifest shape, the JDK selection
   mechanism, the IDE opening rule, the detection rules for the showcase. Stop there for the
   owner's reading in the IDE; this is the first stopping point of the work order.
3. After the ruling: slice 1, the declaration and `project wrap`, as PR1 with its Codex review.

## Open Threads

- The release target is the owner's to fix at the first stopping point.
- `project-management` has four items waiting in its mailbox from 2026-10-31; this session
  left them untaken because the owner directed it to open this workstream instead.
- The owner's checkout carries an uncommitted 0.3.0 migration of the dogfood manifest and lock
  (schema 2) and an IDE module file change; they are not this workstream's and travel
  uncommitted.

## Document Index

- [the work order](../../work-orders/2026-11-02-wrapped-projects.md): read first.
- `intake/` and `intake-dispositions.md`: the queue and its log; empty at opening.
