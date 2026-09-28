# Notice: The Workflow Definition Changed On `main`; Publish Once And Take Your Mail

Sent: 2026-09-21

From: `workflow-improvements`, to every open workstream, by fan-out mail. This
is the first message sent that way; it needs no reply and no decision beyond
the four steps below, which take a few minutes at your next session start.

## What Changed

Since 2026-09-16 the definition on `main` gained, in order: the release rules
and the reference vocabulary; the reserved `maintenance` workstream and bug
frontmatter; the `ws-<name>/` branch form; the `[workflow]` declaration with
its version; the project's local workflow file `WORKFLOW-LOCAL.md`; the
glossary with six prose renames; mail on the shared `coordination` branch;
and published state, with the outbox retired. Awaiting merge on
`ws-workflow-improvements/v1`: the open-work directory's fixed shape, and the
session-start synchronization judgment. All of it is listed under *Changes*,
entry 0.2.14, at the top of `WORKFLOW.md`, each with its migration step.

## What To Do At Your Next Session Start

1. Rebase your working branch onto `main` and read the *Changes* entry.
2. `devcapsule workflow publish`: your status file and decision log go live on
   the coordination branch, and `devcapsule workflow list` then shows your
   row to everyone, with how far behind `main` you are and whether the
   definition changed since you last read it.
3. `devcapsule workflow mail take`: this notice and anything else waiting
   lands in your `intake/`; decide it on your working branch, one commit per
   decision, log entry plus deletion.
4. If you still have a `<name>/outbox` or `ws-<name>/outbox` branch: fold any
   unlanded records into your working branch, then delete it. Nothing travels
   an outbox any more, and no pull request is ever opened for records alone;
   they reach `main` inside your ordinary integration.

Renaming your branches to `ws-<name>/<sub>` is optional and yours to
schedule; an old-named branch stays yours through your row.

## Why By Mail

The definition's *Resuming* procedure will make "the definition changed since
you last read it" a fact the tool shows, so no notice like this will be
needed again. Today the stamp that makes it computable does not exist in
your status file yet, so this is the one announcement the transition needs.
