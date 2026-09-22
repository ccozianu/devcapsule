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
- [x] Run the release-source build gate at `36fa74e`.
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

Release-source evidence: the full build passed on clean commit
`36fa74e4934622b3bdb993b3ccbef86729661046`: 1,044 tests passed, 18 deselected,
one existing xfail and the quarantined claim test XPASS; mypy and nine packaged
checks passed. Both local and revision-bearing PEX artifacts were built and
smoke-tested. `dist/devcapsule.pex version --json` reports version `0.2.14`
and that exact source revision. This is not downloaded-RC acceptance.

The subsequent checkpoint records these results only; runtime/test inputs are
unchanged. Next: owner integrates the initial release preparation PR, then
verify main's disposition and complete pre-RC0 coordination before tagging.

## Local Builds Before RC0

Built from release tip `07fd1143fcaf5a2195128a3b2854495b91ad4613` on 2026-09-22:

| Artifact | Local location / identity | Verification |
|---|---|---|
| PEX | `devcapsule-src/dist/devcapsule.pex` | Version 0.2.14, exact source revision, nine packaged checks passed. |
| Docker base | `devcapsule-base:0.2.14-local-07fd114` | Recipe ubuntu-24.04@9; OCI source revision matches the PEX. |

PEX SHA-256: `61d2d2e8645373d55fcc68edf2988fe421f5cbc73b13d8f6556f52a4af4336c3`.
Image ID: `sha256:85e679728e0c0790ac1631aa8e20cdae58a1de3bc8bd2a69d13b4717974ddab8`.
Machine-readable local evidence: `devcapsule-src/dist/release-0.2.14-local-builds.json`.
The first build's default Docker network could not resolve Ubuntu mirrors;
that owned build was stopped and the documented `--network host` retry succeeded.
This selects build-time networking, not project runtime networking.

The owner requested PR creation, tagging and local builds. Interpreted the
ambiguous local build request as PEX plus Docker base while asking whether a
project environment image was also intended; that clarification is pending.
These are local builds, not tagged candidate artifacts. No project environment
image or runtime acceptance is claimed.

Prepared initial PR title/body locally in `/tmp/release-0.2.14-pr-body.md`.
Agent PR creation needs the requested one-time exception to the owner-UI rule;
no answer has arrived. Under the existing arrangement the owner creates/merges
it. RC0 tagging waits for the main disposition and pre-RC0 coordination already
listed above. No candidate tag has been created or pushed.

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
