# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: active; permanent maintenance

Integration target: `main`

Delivery method: pull request

Requirements: `R-PRODUCT-006`

## Goal

Own the defects that no open workstream covers, on `main` and on maintained
release lines, and drive maintenance releases, for as long as this repository
uses `multiple-streams` mode. See *The Reserved `maintenance` Workstream* in
`WORKFLOW.md`.

## Branch Association

`maintenance/`; no branch yet. Branches are `maintenance/<bug-or-release-line>`,
one per fix or per maintained release line, forked from `main`. Several pairs
may work this workstream at once on separate branches.

## Adoption Exception

This repository adopted `multiple-streams` on 2026-08-08. The reserved
`maintenance` workstream was defined by `workflow-improvements` on 2026-09-18
and created the same day, so its start date is later than the mode's
initialization. This is the adoption exception `WORKFLOW.md` defines for the
case; nothing else about the workstream is exceptional.

## Queue

Read from `main`, not from this file: the bug records under
`engineering-docs/bugs/` whose `owner` is `maintenance` and whose `status` is
neither `closed` nor `retired`.

At registration the queue held 12 open bugs, all with `severity: untriaged`,
because the controlled vocabulary was introduced the same day and the product
owner has not yet rated them. Three further open bugs are owned elsewhere: one
by `contained-display` and two by `component-catalog`, each fixed on a branch
and awaiting the owner's validation.

## Current State

Registered 2026-09-18 by `workflow-improvements`, in the same round that
defined the workstream and the bug vocabulary. No fix has been started. The
`Status note` line in each bug record preserves the free-text status that
predates the vocabulary; it is evidence, not a second status.

## Planned Next Step

Triage: the product owner rates each of the 12 untriaged bugs `blocking`,
`major`, or `minor`, and names a `target` release where one applies. Then take
the highest-severity open bug on the current release line, on a
`maintenance/<bug>` branch. The owner has said a handful of bugs should be
fixed for the next release; which handful is the triage's output.

## Open Threads

### Awaiting The Product Owner

- The triage above. Nothing can be selected on evidence until severities
  exist.
- Whether the three bugs marked `fixed` and owned by closing workstreams
  (`contained-display`, `component-catalog`) should move here for validation
  and closure once those workstreams conclude.

### Weighed And Unresolved

- Whether the next release is a maintenance release driven here or a feature
  release driven by another workstream. Depends on the triage and on what else
  is ready; `project-management` decides if the headline is unclear.

### Deliberately Not Preserved

The 2026-09-18 conversation that created this workstream; its reasoning is in
`workflow-improvements`' handoff under *Sixteenth Task*.

## Workstream Document Index

This workstream owns:

- this status file;
- [`intake-dispositions.md`](intake-dispositions.md); and
- its `intake/` directory.

Bug records are owned by whoever their `owner` field names and live under
`engineering-docs/bugs/`, indexed in root `index.md`.
