# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: paused; configuration ADT review follow-up validated, ready for owner review

Integration target: `main`

Delivery method: pull request

Requirements: `R-PRODUCT-006`, `R-COMPAT-001`, `R-PRODUCT-002`

## Goal

Own the defects that no open workstream covers, on `main` and maintained release
lines, and drive maintenance releases. See *The Reserved `maintenance`
Workstream* in `WORKFLOW.md`.

## Branch Association

Current branch: `ws-maintenance/triage`, synchronized with remote `main`
at `c6296b7` on 2026-09-20. `ws-maintenance/outbox` carries only this workstream's
records and own workstream-list row. Its previous send has not landed; append
rather than reset until delivery is confirmed.

## Adoption Exception

The repository adopted multiple streams on 2026-08-08. The reserved maintenance
workstream was defined and created on 2026-09-18 under the workflow's adoption
exception; that is its immutable start date.

## Queue

Read the authoritative queue from bug records with `owner: maintenance`, status
neither `closed` nor `retired`. There are 14 open records at this checkpoint.
The two selected upgrade-recovery/configuration-contract records are `fixed`,
not closed or released. Severity and release targets remain untriaged. The owner
selected this correction ahead of general triage.

## Current State

2026-09-20 owner-review follow-up: replaced the launch-mechanics compatibility
claim with an admission/resolution ADT and semantic laws. `Configuration` owns
its input snapshot; `Resolution` owns the derived plan. Both the real resolve
operation and execution adapter use this boundary. The distinction between
plan meaning and freshness is explicit (`same_meaning_as` is not object equality).
Thirty ADT cases cover predecessor admission/meaning, repeated derivation,
observation and ownership, dependency scope, security-question changes, force,
unsupported representations and plan integrity. They invoke no CLI or launcher
mocks. File-byte preservation is separately checked through the CLI adapter.
Set/bind/authorize/unset remain the existing edit API; this follow-up does not
claim to encapsulate those operations in the new ADT.

Validation: final `nox -s build` passed: **907 tests, mypy over 143 source files,
source CLI smoke, PEX build and nine packaged-executable tests**; 18
host-sensitive tests deselected and one pre-existing expected failure. The
final ADT module rerun passed **30 cases**, including the additional absent-base
observation case added after gate collection. Combined coverage is 100%
statements/branches for `configuration.py`, `configuration_documents.py`,
`configuration_review.py` and `configuration_resolution.py` (345 statements,
112 branches). This is not proof of the entire configuration implementation.
Logs: `/tmp/configuration-adt-build.log` and `/tmp/configuration-adt-laws.log`.
The updated proof map separates semantic laws, representation checks and adapter
checks. Historical 0.2.11 data is still interpreted by current source; no test
executes original 0.2.12 or reconstructs the incident's unavailable inputs.

### Earlier refactor checkpoint

2026-09-20: completed the owner's instruction to carry the full configuration
contract through into implementation, rather than stop at the audit. The owner
explicitly supplies serialized access to the underlying configuration files
within and between processes. No cooperative lock is needed under that condition.
This instruction supersedes the consent-conflating portion of the earlier interim
init behavior; project ownership of manifest/lock regeneration is unchanged.

The refactor establishes:

- common artifact admission, supported-format and checkout-identity checks;
- a whole-document checkout writer that preserves unrelated answers, refuses
  unsupported structure, and uses private staging with atomic replacement;
- one registry for node names/effects, shared set/bind operations for init and
  individual edits, and separate identity/configuration elicitation namespaces;
- complete node assessment and a pure generated-plan projection;
- typed effective host decisions, including legacy decisions and run-once
  precedence, with no permission resurrection through unset or stale output;
- one execution admission boundary and a lower launcher that cannot add ambient
  legacy privileges, credential sources or host paths to a project plan;
- scoped manifest freshness and compatible interpretation of released unscoped
  fingerprints, without repinning or rewriting standing user choices.

At that checkpoint all nine audit gap families were fixed. The original audit module has 45 passing
cases, with all ten expected-failure markers removed. The new invariant module
has 128 passing cases, including the related composition consequences identified
while implementing the contract. The recovery journeys remain, with client-only semantics now tested by the ADT laws.

Validation: `nox -s build` passed with **877 tests, mypy, source CLI smoke, PEX
construction and nine packaged-executable tests**. Eighteen host-sensitive tests
were deselected; one unrelated pre-existing expected failure remains. Separately
measured statement/branch coverage is 100% for `configuration_documents.py`
(69 statements/42 branches), `configuration_review.py` (149/34), and
`configuration_resolution.py` (57/26; its impossible missing-selection guard is
excluded). This is not a claim that all CLI code has 100% coverage. The full
[correctness argument](configuration-correctness.md) maps the contract's condition
partitions to tests and states assumptions and external acceptance limits.
Changed document links and all 64 named test references were verified.

Historical checkpoints: `6709756` implemented the bounded upgrade recovery;
`4f5091e` recorded the complete contract/audit. The current continuation repairs
that audit and replaces its intentionally failing obligations with passing tests.
The selected status and document revisions supersede the audit-only handoff.

## Planned Next Step

Owner review of the ADT laws and their production boundary, then PR integration
of `ws-maintenance/triage`, followed by actual
host upgrade/display/privilege acceptance before closing the two records or
claiming a release. Review the contract/proof with the implementation and tests.
Do not repeat the investigation or treat the former audit gaps as still open.
Remaining maintenance queue prioritization belongs to the next selected slice.

## External State And Risks

No containers, ports, additional environments, image pulls or GUI sessions were
created for this work. The existing `devcapsule-src/.venv` ran the required gate.
`dist/devcapsule-local.pex` is the validation artifact, not a release artifact.
No change is integrated into remote `main`; under `WORKFLOW-LOCAL.md`, the owner
opens and merges the PR. The implementation PR should land before any independent
records-only delivery whose links require its contract documents.

No mail was sent, per the owner's instruction. Mailbox retrieval reported no
maintenance mail at both resumption and the final pre-pause check. Remote main
was re-fetched and remains `c6296b7`, with no new commits to synchronize. Intake contains only its README and no pending item.

## Open Threads

### Awaiting The Product Owner

- PR review/integration and actual host recovery/display/privilege acceptance.
- Severity/release triage for the remaining queue, including ownership of fixes
  from workstreams approaching closure.

### Weighed And Unresolved

- General workstation policy/default overlays, lockless-consumer UX, identity
  relocation and a comprehensive historical recipe policy are future product
  boundaries explicitly separated from this V1 correction.
- Concurrent configuration access is excluded by the owner's precondition;
  do not add a locking protocol without a concrete need to change that condition.
- Exact incident-era inputs/build logs remain unavailable; real predecessor
  fixtures and complete recovery journeys provide the recorded unit evidence.

### Deliberately Not Preserved

No transcript was requested. The contract, correctness case map, tests, bug
records and this checkpoint retain the consequential decisions and evidence.

## Workstream Document Index

- this status file;
- [upgrade recovery contract](upgrade-recovery-contract.md);
- [configuration lifecycle contract](configuration-contract.md);
- [configuration correctness and test map](configuration-correctness.md);
- [intake dispositions](intake-dispositions.md); and
- the adjacent `intake/` directory.

Bug records remain under `engineering-docs/bugs/`, indexed in root `index.md`.
