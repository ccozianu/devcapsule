# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: paused; configuration contract and correctness audit ready for review

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

At this checkpoint the queue holds 14 open bugs. The upgrade-recovery record
remains `fixed` pending host acceptance; the new configuration-contract record
is `confirmed` with nine gap families and ten executable counterexamples.
Severity and release targets remain untriaged; the owner explicitly selected
this work ahead of general triage.

## Current State

2026-09-20 follow-up complete: the owner requested the complete configuration
contract, from empty state through edits and CLI/base/schema upgrades, followed
by a readable correctness argument mapped to unit tests. Delivered:

- [`configuration-contract.md`](configuration-contract.md): ownership, the typed
  tree, precedence, node states, initialization/edit/resolve/run transitions,
  schema-evolution obligations and explicit unresolved product boundaries.
- [`configuration-correctness.md`](configuration-correctness.md): entrypoint-to-
  launcher trace, compositional arguments, 15 obligations, 61 named test
  references, nine gap families and limits of the earlier coverage claim.
- `tests/test_configuration_contract.py`: 35 passing domain/lifecycle cases
  and ten strict expected failures that assert the desired behavior at known
  counterexamples. G1 has two distinct schema boundaries; G2–G9 one each.
- [Configuration-contract defect](../../bugs/devcapsule/2026-09-20-configuration-contract-not-enforced-across-boundaries.md):
  durable tracking of the unmet obligations. No production behavior was
  changed by this follow-up; it audits production revision `6709756`.

The full argument does not hold yet. In particular, init can turn an existing
recommendation into a grant (overlapping a previously accepted interim behavior),
and the lower launcher can override a sudo denial through legacy environment
configuration. Unknown-schema mutation/execution and loss of unknown local
content also prevent a general upgrade-preservation claim.

Validation: `nox -s build` passed with mypy, 739 tests, source CLI smoke, PEX
construction and nine packaged tests; 18 host-sensitive tests were deselected.
There are 11 expected failures: ten audit obligations plus one pre-existing
case. They are known failures, not successful correctness evidence. Relative
links and the 61 referenced test names were checked. No new mainline commits
or maintenance mail were found at resumption.

2026-09-20: the owner selected the upgrade-recovery bug of 2026-09-19 for
autonomous repair, with contract-led abstraction and reviewable unit coverage.
The bounded repair is on `ws-maintenance/triage`. Inspection, resolution
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

Review the contract and address the recorded obligations with one admitted
typed configuration and an effective launch plan that downstream layers cannot
override. Prioritize consent provenance and denial preservation (G2/G9), then
schema admission/preservation and the remaining gaps. Turn each strict expected
failure into an ordinary passing test. The interim init/regeneration ruling
must be explicitly reconciled, not silently revoked. Owner PR integration and
actual host validation of the earlier repair remain outstanding.

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

- Review of the full contract, including the existing interim init/regeneration
  exception; PR delivery and actual host recovery/display acceptance.
- Remaining queue severity/release triage and ownership of fixed bugs from
  closing workstreams (`contained-display`, `component-catalog`).

### Weighed And Unresolved

- The general workstation overlay, lockless consumer flow, regeneration
  ownership, identity relocation and supported-schema/recipe policy remain open.
- The incident's exact old inputs/build log remain unavailable. This audit
  supplies counterexamples and a conditional argument, not a whole-system proof.

### Deliberately Not Preserved

No transcript was requested. Contracts, case coverage and remaining acceptance
work are preserved in the bug and workstream documents.

## Workstream Document Index

This workstream owns:

- this status file;
- [`upgrade-recovery-contract.md`](upgrade-recovery-contract.md);
- [`configuration-contract.md`](configuration-contract.md);
- [`configuration-correctness.md`](configuration-correctness.md);
- [`intake-dispositions.md`](intake-dispositions.md); and
- its `intake/` directory.

Bug records are owned by whoever their `owner` field names and live under
`engineering-docs/bugs/`, indexed in root `index.md`.
