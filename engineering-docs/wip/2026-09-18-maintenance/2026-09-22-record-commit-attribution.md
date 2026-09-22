# Commit Attribution Checkpoint

Historical implementation and acceptance record. Subsequently integrated in
PR #128 at `ca3f1d3`, verified from fetched main on 2026-09-22.

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
records evidence and owner-confirmed GitHub display acceptance on 2026-09-22;
the bug is closed. The generic workflow is silent
on co-authorship; used its local-workflow extension point to record the owner's
project convention in `WORKFLOW-LOCAL.md`. No generic definition refresh or
historical commit rewrite is needed. A reusable-policy consideration was
mailed to workflow-improvements as `2026-09-22-maintenance-agent-coauthorship.md`
at coordination `b16003cf563f`; its coordination data-loss fix stays there.

## Validation And External State

The required `nox -s build` passed: 1,041 tests, 18 deselected, one existing
xfail, mypy, CLI/shell checks, local PEX build/smoke and nine packaged checks.
The revision-bearing PEX was skipped under the existing dirty-tree policy.
Commit `1fbe6fa` was pushed with Costin Cozianu as author/committer and the
verified, parsed `GPT-6 Astra Codex` trailer. No runtime source changed in this
slice. The owner confirmed the expected GitHub display on 2026-09-22.
Before recording acceptance, merged main `c93476b` without conflicts because
the generic definition changed. Read the new misplaced-patch handoff rule.
The attribution commits remain absent from main; PR integration is still pending.
The required full build passed again after synchronization, including 1,042
tests and nine packaged checks; no further runtime validation is needed for
this owner-acceptance record. Mailbox and intake remain empty.
The effective Git author and committer now match the owner; this checkout-local
configuration persists in `.git/config` and does not travel with the PR. Other
checkouts must verify their own identity under the new local-workflow rule.
No containers, ports, or historical commits were changed.
