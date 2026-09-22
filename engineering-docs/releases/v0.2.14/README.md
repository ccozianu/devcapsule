# DevCapsule 0.2.14 — Release Work

Updated: 2026-09-22. Stage: **RC0 published; end-user acceptance in progress**.
Driver: **maintenance**. Product owner: Costin Cozianu.

[Download RC0](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.14-rc0) ·
[Bug triage](bugs.md)

Update these working files as decisions and evidence arrive. Chat highlights
changes and questions; the bug records remain authoritative for individual
status, ownership and technical evidence.

## Scope And Owner Decisions

- Release baseline: preparation merge `21371084f7137624aed6c0581b12495a04b04fbb`
  (PR #131), including integrated configuration/upgrade recovery, workflow,
  component and diagnostic-command changes.
- None of the known bugs is a showstopper. The owner considers publication
  possible on bug grounds; fix a selected few or verify they no longer apply,
  and validate major end-user E2E journeys before final acceptance.
- Branch-name migration is deferred through publication of 0.2.14. Complete
  it before substantive work on the next release. Project-management coordinates;
  each workstream owns its rename. WORKFLOW-LOCAL.md records the exception.
- GitHub UI PR/workflow operations remain with the owner; `gh` and SSO credentials
  are unavailable here. Git fetch/push and public-asset verification are available.

## Next Work

Work through selected undecided rows in [bug triage](bugs.md) and the acceptance
journeys below, recording fixes, obsolete findings and explicit deferrals. Two
old Codium-specific records are retired after checking the removed command and
implementation against RC0; 17 bugs remain open. No runtime fix was needed for
those retirements. Candidate fixes produce RC1 or later; never move RC0.

## Preparation And Publication

- [x] Maintenance selected; release branch `release-0.2.14` cut.
- [x] Source version set to 0.2.14; initial full build passed.
- [x] Preparation integrated through PR #132 at `e50b9f1`.
- [x] Candidate source verified on main; integration method `mainline`, no missing commits.
- [x] Owner authorized RC0 and deferred the legacy branch-name deadline.
- [x] Immutable tag pushed; public PEX, checksum and manifest downloaded and verified.
- [ ] Repeat main-disposition review for subsequent candidate fixes.
- [ ] After publishing final 0.2.14, migrate old branch names before next-release work.

## Candidates

| Candidate | Source | Publication | End-user acceptance |
|---|---|---|---|
| [v0.2.14-rc0](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.14-rc0) | `d078b879469c1790647e32db75005d0fa4369b27` | Public assets verified 2026-09-22. | Clean-machine executable check passed; major journeys pending. |

The annotated tag points to the prepared source, not subsequent record updates.
Public manifest: version `0.2.14rc0`, prerelease true, release branch
`release-0.2.14`, and mainline integration with no missing commits.
Published PEX SHA-256:
`2a425a39d2ed5319d1945dd91e34f693c299fa2c53acdf70a205024eea45d513`.

Downloaded files: `devcapsule-src/dist/rc0-published/`. Checksum file and manifest
both match the PEX; `version --json` matches the exact tag, version and source.
The downloaded executable passed `nox -s pex_clean_machine` on network-disabled
Ubuntu with no Python interpreter. These observations verify public availability
and executable portability; they do not substitute for IDE/agent acceptance.
The Actions run was not independently inspected through a credentialed API.

## End-User Acceptance

Use the downloaded candidate, and record its checksum, platform, IDE/agent,
steps, user-visible outcome and evidence. Do not imply untested combinations.

- [x] Download/install smoke: checksum and identity correct; executable works
  without a preinstalled Python or network access.
- [ ] Fresh-user journey: configure a project, understand permissions, launch
  the IDE and do useful work without an undisclosed remedy.
- [ ] Existing-user upgrade: recover predecessor configuration through offered
  commands while preserving grants, denials and display choices.
- [ ] Everyday work: edit/run/test with a selected IDE and agent; stop normally
  and resume with project and tool state preserved.
- [ ] Relevant graphical/display and login behavior works in actual use.
- [ ] `project run --print-command` is usable, agrees with ordinary launch,
  and does not start the project.
- [ ] Nested-directory workflow mail/publish/claim preserves unrelated state;
  use an isolated remote for the destructive-regression acceptance scenario.
- [ ] Record selected bug fixes, retirements and deferrals with evidence.

## Local Artifacts And Validation

| Artifact | Location / identity |
|---|---|
| Local tagged PEX | `devcapsule-src/dist/rc0-local/devcapsule.pex` — version `0.2.14rc0`, source `d078b87`. |
| Local Docker base | `devcapsule-base:0.2.14-rc0-local` — recipe ubuntu-24.04@9, source `d078b87`. |

Local PEX SHA-256: `2a425a39d2ed5319d1945dd91e34f693c299fa2c53acdf70a205024eea45d513`.
Docker image ID: `sha256:ed0867e6fe51c72ad49eef935bab45d29d1cd742f2333757201d030804289092`.
Both came from exact tagged source. The base used the documented host build
network after the earlier default-network DNS failure; runtime networking was
not changed. This base is local only; RC0 retains its manifest's pinned public base.

All nine packaged checks passed across the initial run (eight passed) and the
corrected identity check: the first invocation used a filename the harness did
not accept, then passed with canonical `devcapsule.pex`, without code changes.
The local RC0 PEX also passed clean-machine validation. Full source validation
remains the earlier 1,044 passes, 18 deselections, one existing xfail and one
quarantined XPASS, plus mypy; runtime/test inputs did not change for RC0.

## Final Promotion

No final tag or acceptance JSON exists. When an exact candidate passes the
selected end-user journeys, prepare `engineering-docs/releases/v0.2.14.json`
through the [release runbook](../../implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md).
Retain this directory as the release's working history.

[Maintenance handoff](../../wip/2026-09-18-maintenance/CURRENT-STATUS.md)
