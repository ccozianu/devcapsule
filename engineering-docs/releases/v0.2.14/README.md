# DevCapsule 0.2.14 — Release Work

Updated: 2026-09-22. Stage: preparation; the release branch has not been cut.
Driver: **maintenance**, selected by the owner. Product owner: Costin Cozianu.

Start with [bug triage](bugs.md). Update these files as decisions and evidence
arrive; use chat for decisions, questions and short progress reports rather
than repeating the inventory. This is a maintained working view, not an
automatically refreshed dashboard.

## Scope And Next Action

Proposed baseline: current main at the approved cut. Proposed headline:
configuration/upgrade recovery fixes, with the already-integrated workflow,
component and diagnostic-command changes. Final scope and cut await the owner.

Next: work through the undecided rows in [bug triage](bugs.md), settle what
0.2.14 must fix or validate, then record the cut. Existing source changes and
owner acceptance may justify closing stale records without another experiment.
An open bug does not automatically block this release.

## Preparation Checklist

- [x] Select maintenance as the driver.
- [x] Integrate the release-fix propagation policy and aligned runbook (PR #124).
- [ ] Decide the release scope and applicable bug dispositions.
- [ ] Integrate the claim-test quarantine and bug record (prepared at `43b0f87`).
- [ ] Record the approved baseline and cut `release-0.2.14`.
- [ ] Set/confirm source version `0.2.14` and run the build gate.
- [ ] Before RC0: reconcile remaining legacy workstream branch associations.
- [ ] Account for release fixes on main before each candidate.

Baseline SHA: not selected. Release branch: not created. Candidate: none.

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
