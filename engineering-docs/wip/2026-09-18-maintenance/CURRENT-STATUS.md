# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: paused; upgrade-recovery implementation ready for owner review

Integration target: `main`

Delivery method: pull request

Requirements: `R-PRODUCT-006`

## Goal

Own the defects that no open workstream covers, on `main` and on maintained
release lines, and drive maintenance releases, for as long as this repository
uses `multiple-streams` mode. See *The Reserved `maintenance` Workstream* in
`WORKFLOW.md`.

## Branch Association

Current branch: `ws-maintenance/triage`, synchronized with remote `main`
at `c6296b7` on 2026-09-20. Branches are `ws-maintenance/<bug-or-release-line>`,
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

At this checkpoint the queue holds 13 open bugs, including the upgrade-recovery
record now marked `fixed` pending host acceptance. Severity and release targets
remain untriaged; the owner explicitly selected this fix ahead of general triage.

## Current State

2026-09-20: the owner selected the upgrade-recovery bug of 2026-09-19 for
autonomous repair, with contract-led abstraction and reviewable unit coverage.
Implementation is complete on `ws-maintenance/triage`. Inspection, resolution
and execution share the authorization assessment; remedies use valid current
choices; developer decisions survive recovery; display and build consequences
are explained before materialization. The entrypoint-to-launch contract and
71-case verification map are in
[`upgrade-recovery-contract.md`](upgrade-recovery-contract.md).

The full local gate passed: mypy, 704 tests (18 host-sensitive tests deselected,
one expected failure), source CLI smoke, PEX build and nine packaged tests.
The new assessment and authorization-review helpers have 100% statement and
branch coverage. The focused configuration/materialization suite passed 178
tests. Actual host GUI upgrade acceptance has not been performed.

No mail was sent, per the owner's instruction. The source-built launcher took
the mailbox before this checkpoint and reported no mail for `maintenance`.
The intake directory contains no pending items.

## Planned Next Step

Owner review and PR integration of the fix, followed by the actual host
upgrade/display walkthrough specified in the bug's acceptance criteria. Keep
the bug `fixed`, not `closed`, until that evidence exists. General queue triage
and release targeting remain after this explicitly selected task.

## External State And Risks

No containers, ports or additional environments were created. The existing
`devcapsule-src/.venv` ran validation; `dist/devcapsule-local.pex` is the
uncommitted-build validation artifact, not a release artifact. No change has
been integrated to `main`. Under `WORKFLOW-LOCAL.md`, the owner opens and merges
the PR. Records and the working branch are prepared for that handoff; the
implementation PR must land before any records-only delivery that links its
new contract document.

## Open Threads

### Awaiting The Product Owner

- Actual host recovery/display acceptance and PR delivery; automated tests
  substitute Docker and GUI launch and cannot establish the owner's experience.
- Remaining queue severity/release triage and ownership of fixed bugs from
  closing workstreams (`contained-display`, `component-catalog`).

### Weighed And Unresolved

- The incident's exact old inputs and build log remain unavailable. Preserve
  explicit display decisions; do not infer X11 consent from an implicit default.
- Matrix-upgrade product design and the next release's ownership remain with
  project-management; this fix does not decide either.

### Deliberately Not Preserved

No transcript was requested. Contracts, case coverage and remaining acceptance
work are preserved in the bug and workstream documents.

## Workstream Document Index

This workstream owns:

- this status file;
- [`upgrade-recovery-contract.md`](upgrade-recovery-contract.md);
- [`intake-dispositions.md`](intake-dispositions.md); and
- its `intake/` directory.

Bug records are owned by whoever their `owner` field names and live under
`engineering-docs/bugs/`, indexed in root `index.md`.
