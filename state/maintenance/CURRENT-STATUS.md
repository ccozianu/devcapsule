# Workstream Current Status: Maintenance

Mnemonic: `maintenance`

Start date: 2026-09-18

State: paused 2026-09-22; attribution fix validated, awaiting owner GitHub display acceptance and PR integration

Definition read: WORKFLOW.md@a1002b6f5e67, WORKFLOW-LOCAL.md@0f44773f837c

Integration target: `main`

Delivery method: pull request; agent pushes the branch, owner opens and merges on GitHub

Branch association: `ws-maintenance/triage`

Requirements: `R-PRODUCT-006`, `R-COMPAT-001`, `R-PRODUCT-002`

## Goal

Own defects no open workstream covers and drive maintenance releases. This
reserved workstream remains open for the lifetime of multiple-stream mode.
Its 2026-09-18 start is the recorded adoption exception.

## Current State

Run-image replacement and incident recovery evidence are preserved in the
[completed-slice checkpoint](2026-09-22-record-run-image-replacement.md).

## Current Slice: Commit Attribution

Verified owner-reported PR #125 integration at `f0d6901`: main contains the
run-image replacement `1c6d2c9`; the fetched tree differs only in the generated
coverage badge. Fast-forwarded this clean branch to main `223b8c4` before the
new slice. Definition/local rules had not changed; synchronization was appropriate
at this delivery boundary. Maintenance mailbox and intake were empty.

Owner treats missing Codex co-authorship as a bug and requires the actual model
name first, then Codex. Corrected this checkout's placeholder Git identity to
Costin Cozianu's name/email already used on owner merge commits. This session's
recorded model is `gpt-6-astra`. The [attribution bug](../../bugs/devcapsule/2026-09-22-codex-commit-attribution.md)
records evidence and UI acceptance still needed. The generic workflow is silent
on co-authorship; used its local-workflow extension point to record the owner's
project convention in `WORKFLOW-LOCAL.md`. No generic definition refresh or
historical commit rewrite is needed. A reusable-policy consideration was
mailed to workflow-improvements as `2026-09-22-maintenance-agent-coauthorship.md`
at coordination `b16003cf563f`; its coordination data-loss fix stays there.

## Planned Next Step

Owner checks the pushed attribution fix for the human author and
`GPT-6 Astra Codex <noreply@openai.com>` co-author display, then integrates this
local-policy fix through a PR. Fetch and verify main after the owner reports merge. After this
bounded delivery, resume saved triage with the owner; retired-outbox verification
remains accepted follow-up. Run-image implementation is already integrated;
the legacy PyCharm networking issue remains open.

## Validation And External State

The required `nox -s build` passed: 1,041 tests, 18 deselected, one existing
xfail, mypy, CLI/shell checks, local PEX build/smoke and nine packaged checks.
The revision-bearing PEX was skipped under the existing dirty-tree policy.
Commit `1fbe6fa` was pushed with Costin Cozianu as author/committer and the
verified, parsed `GPT-6 Astra Codex` trailer. No runtime source changed in this
slice; GitHub UI acceptance remains pending.
The effective Git author and committer now match the owner; this checkout-local
configuration persists in `.git/config` and does not travel with the PR. Other
checkouts must verify their own identity under the new local-workflow rule.
No containers, ports, or historical commits were changed.

## Open Threads

- Awaiting GitHub display acceptance and PR integration of the commit-attribution rule;
  run-image replacement is integrated in PR #125.
- Awaiting workflow-improvements: fix the nested-directory coordination bug and
  decide the separately proposed diff-handoff rule. Use the root-cwd workaround.
- Preserved: 14-item triage, remaining legacy host-network issue, broader
  configuration evidence/docs, release sequencing and retired-outbox verification.
- Production blog deployment and incident-era exact host bytes remain unverified;
  no new live acceptance or cleanup is claimed.
- Deliberately not preserved: no transcript/session record; the received diff
  remains in intake history and coordination history after disposition.

## Workstream Document Index

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
