# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: active; releasing 0.2.14; RC0 public and verified; end-user acceptance and selected bug triage next

Definition read: WORKFLOW.md@bc1937f188ca, WORKFLOW-LOCAL.md@031c167690c0

Integration target: `main`

Delivery method: pull request; agent pushes the branch, owner opens and merges on GitHub

Branch association: `release-0.2.14`

Requirements: `R-PRODUCT-006`, `R-COMPAT-001`, `R-PRODUCT-002`

## Goal

Own defects no open workstream covers and drive maintenance releases. This
reserved workstream remains open for the lifetime of multiple-stream mode.
Its 2026-09-18 start is the recorded adoption exception.

## Current State

Published `v0.2.14-rc0` at `d078b879469c1790647e32db75005d0fa4369b27`, already
integrated through PR #132 at `e50b9f1`. Tag push was verified through remote
refs; public PEX, checksum and manifest were downloaded without credentials.
Checksum, version 0.2.14rc0, tag mnemonic and exact source identity agree.
The downloaded executable passed clean-machine validation with no Python or
network. Full evidence, artifact locations and the acceptance checklist are in
[release work](../../releases/v0.2.14/README.md).

The owner explicitly deferred legacy branch renames through 0.2.14 publication,
before substantive work on the next release. WORKFLOW-LOCAL.md records this;
project-management received `2026-09-22-maintenance-rename-deadline-deferred.md`
on coordination at `4013fca06a54`, superseding the earlier pre-RC0 deadline.
The owner says known bugs do not prevent publication on bug grounds; fix or
verify a selected few and validate major end-user journeys before final acceptance.

Retired the two old codium_with_claude option-parity and ambient-sudo records:
the exact candidate lacks the old command module, launcher and entrypoint, and
both local and downloaded RC0 reject the command. This implements the saved
triage recommendation; it does not claim complete VSCodium acceptance. The
[working bug table](../../releases/v0.2.14/bugs.md) retains all 19 rows, now
17 open and two retired. No runtime code changed during this slice.

## Planned Next Step

Use downloaded RC0 for the release overview's end-user acceptance journeys:
fresh project, predecessor upgrade/recovery, IDE/agent work and resume,
graphical/login behavior, diagnostic command and isolated coordination scenario.
Pick further bugs from the table, fix, verify obsolete, or explicitly defer.
Capture the actual platform/surface/agent and user-visible outcome. Neither
unit coverage nor executable portability alone completes release acceptance.
New source fixes require the next immutable candidate and a main disposition.
Only after owner acceptance of an exact candidate prepare the final JSON/tag.

## Validation And External State

RC0's integration gate passed by mainline ancestry with zero missing commits.
Local RC0 PEX and Docker base were built from a disposable exact-tag worktree,
which was removed after the build; this checkout remains on release-0.2.14.
Nine packaged assertions/checks passed: eight in the first run, then the
identity check after using the harness's canonical artifact filename. No code
was changed to satisfy that filename check. Local and downloaded PEX each
passed the networkless/no-Python clean-machine check. The locally built base
retains tag devcapsule-base:0.2.14-rc0-local and is not published to a registry.

Prior full source gate: 1,044 passed, 18 deselected, one existing xfail and one
quarantined XPASS, mypy and packaged checks. RC0 has identical runtime/test
inputs. Current edits are policy and bug/release records only; links, frontmatter,
row counts and whitespace were verified. The old claim-test xfail remains.

GitHub PR/workflow UI operations stay with the owner; neither gh nor SSO is
available here. No credential probes or API operations were attempted. Public
asset downloads verify publication; no credentialed Actions-run inspection is
claimed. No final release or graphical/end-user acceptance is claimed yet.

## Open Threads

- RC0 is published; end-user acceptance and selected further bug dispositions remain.
- Project-management coordinates renames after 0.2.14 publication, before
  substantive next-release work. This no longer holds 0.2.14 candidates.
- Workflow-improvements owns the claim-test design repair and generic release
  propagation rule revision; the local owner exception already governs here.
- Preserve retired-outbox follow-up, configuration contracts/coverage limits,
  and historical host/blog acceptance gaps; no unrelated cleanup was done.
- The pre-existing Codium delimiter edit remains saved at
  `.git/codex-preserved-codium-sudo-edit.patch`; its intent was never inferred.
  The canonical bug record now records retirement, so review before applying it.
- No transcript/session record was requested; canonical decisions live in the
  release documents and bug records.

## Workstream Document Index

- [Release overview](../../releases/v0.2.14/README.md): cut, candidates and acceptance checklist.
- [Release bug triage](../../releases/v0.2.14/bugs.md): maintained dispositions and evidence.

- [Attribution checkpoint](2026-09-22-record-commit-attribution.md): integrated authorship convention, owner acceptance and build evidence.

- [Run-image replacement checkpoint](2026-09-22-record-run-image-replacement.md): merged implementation, validation and coordination recovery evidence; open only for those details.
- [Prior checkpoint record](2026-09-21-record-maintenance-before-component-upgrades.md): historical implementation, tests and graphical evidence; open only for those details.
- [Proposed bug triage](2026-09-21-note-proposed-bug-triage.md): open on resuming triage; not applied.
- [Pre-V1 assessment](2026-09-21-note-pre-v1-adopter-and-contributor-case.md): positioning input and owner Windows correction.
- [Early-adopter blog](../../blog/2026-09-21-why-try-devcapsule-before-v1.md): merged article and editorial follow-up.
- [Upgrade recovery contract](upgrade-recovery-contract.md): scope of the merged recovery fix.
- [Configuration contract](configuration-contract.md): lifecycle requirements relevant to future changes.
- [Correctness/test map](configuration-correctness.md): implementation evidence and coverage limits.
- [Intake decisions](intake-dispositions.md): outcomes of received mail.
- `intake/`: no pending items; both project-management messages acknowledged in the decision log.
