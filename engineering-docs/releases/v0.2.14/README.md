# DevCapsule 0.2.14 — Release Work

Updated: 2026-09-22. Stage: stabilization; release branch cut at the owner's direction.
Driver: **maintenance**, selected by the owner. Product owner: Costin Cozianu.

Start with [bug triage](bugs.md). Update these files as decisions and evidence
arrive; use chat for decisions, questions and short progress reports rather
than repeating the inventory. This is a maintained working view, not an
automatically refreshed dashboard.

## Scope And Next Action

Baseline: preparation merge `21371084f7137624aed6c0581b12495a04b04fbb` (PR #131).
The release includes the integrated configuration/upgrade recovery fixes,
workflow, component and diagnostic-command changes. Later main `c8ae736` changes
only the generated coverage badge. Maintenance drives stabilization from this cut.

Owner decision, 2026-09-22: start the release now; none of the currently listed
bugs is a showstopper. Fix or defer them as work proceeds. Individual fixes,
closure and deferral decisions will be recorded in the bug table.

Next: validate and deliver the initial release preparation PR, then work
through the undecided rows in [bug triage](bugs.md) during stabilization. Existing source changes and
owner acceptance may justify closing stale records without another experiment.
An open bug does not automatically block this release.

## Preparation Checklist

- [x] Select maintenance as the driver.
- [x] Integrate the release-fix propagation policy and aligned runbook (PR #124).
- [x] Approve the cut and integrated baseline; decide bug fixes/deferrals as we go.
- [x] Integrate the claim-test quarantine and bug record (PR #131).
- [x] Record the approved baseline and cut `release-0.2.14`.
- [x] Set source version `0.2.14` in the first release commit.
- [ ] Run the release-source build gate.
- [ ] Integrate the initial release preparation PR before RC0.
- [ ] Before RC0: reconcile remaining legacy workstream branch associations.
- [ ] Account for release fixes on main before each candidate.

Baseline SHA: `21371084f7137624aed6c0581b12495a04b04fbb`.
Release branch: `release-0.2.14`. Candidate: none.

## Candidate Acceptance

Use the downloaded candidate executable and record its exact tag, revision,
checksum and evidence. Proposed coverage for the changed behavior:

- [ ] Predecessor configuration recovery and preservation of host decisions.
- [ ] Actual launch and relevant graphical/display behavior.
- [ ] Diagnostic `project run --print-command` behavior.
- [ ] Nested-directory coordination preserves unrelated mail, state and claims.
- [ ] Any further acceptance selected during bug triage.

Local evidence available: the source at `43b0f87` passed the full build with
1,044 tests passed, 18 deselected, one existing xfail and the quarantined claim
test XPASS; mypy and nine packaged checks passed. This is not RC acceptance.

## Candidates And Completion

No candidate has been published for this release. Append each candidate's tag,
source SHA, build/run links, acceptance outcome and remaining issues here as
it is produced. Add an evidence file only when the detail warrants it.

Once an exact candidate is accepted, prepare `engineering-docs/releases/v0.2.14.json`
using the existing promotion procedure. The JSON remains the machine-checked
acceptance record; this directory holds the working checklist and history.
Retain these documents after release, with the final outcome recorded.

Process: [release runbook](../../implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md).
Coordination and resumption: [maintenance status](../../wip/2026-09-18-maintenance/CURRENT-STATUS.md).
