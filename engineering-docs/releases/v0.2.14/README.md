# DevCapsule 0.2.14 — Release Work

Updated: 2026-09-24. Stage: **RC1 public; local base built; candidate validation in progress**.
Driver: **maintenance**. Product owner: Costin Cozianu.

[Download RC1](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.14-rc1) ·
[Bug triage](bugs.md) · [RC0 smoke scripts](smoke/README.md)

Update these working files as decisions and evidence arrive. Chat highlights
changes and questions; the bug records remain authoritative for individual
status, ownership and technical evidence.

## Scope And Owner Decisions

- Release baseline: preparation merge `21371084f7137624aed6c0581b12495a04b04fbb`
  (PR #131), including integrated configuration/upgrade recovery, workflow,
  component and diagnostic-command changes.
- On 2026-09-24 the owner designated the missing in-capsule `devcapsule`
  command as the first release blocker, superseding the earlier non-blocking
  bug assessment. Smoke progression pauses for blocker triage/fix. URL opening
  is separately filed; workflow onboarding remains non-blocking.
- Branch-name migration is deferred through publication of 0.2.14. Complete
  it before substantive work on the next release. Project-management coordinates;
  each workstream owns its rename. WORKFLOW-LOCAL.md records the exception.
- GitHub UI PR/workflow operations remain with the owner; `gh` and SSO credentials
  are unavailable here. Git fetch/push and public-asset verification are available.

## Next Work

RC1 is tagged at `cec7a0c2f3467b8cc9d84eca820f35ee869087ec`. PR #136 merged
the release fixes into main at `c6bea96cfbbb15a428c86bde6924df8ff3db1c15`;
the candidate integration gate passed with no unintegrated commits. Public
RC1 assets are downloaded and checksum/version/source-verified; the requested
local base is built. Next, validate its
[runtime CLI repair](../../bugs/devcapsule/2026-09-24-runtime-cli-not-on-path.md)
from the IDE terminal before closing the blocker.
The source fix exposes `devcapsule` normally and supports this repository's
recommended `devcapsule0` development exception; Docker command/workflow checks
passed for both names and both IDE image types. Owner accepted the real recursive
PyCharm/devcapsule0 session at `9cc0868` on 2026-09-24. This is local-build
acceptance; the published RC1 now needs exact-candidate validation. The blocker is fixed, not closed. Earlier startup/resume passes remain valid
for their limited assertions; they did not check public CLI availability.

The [bug review](bugs.md#proposed-calls-from-the-2026-09-22-review) now records
the two owner-approved configuration-bug closures and selected retirement of
legacy `pycharm run` (integrated through PR #133; awaiting RC1). Thirteen rows still need decisions:
eight targeted verifications and five deferrals. Review these calls, then use the grouped
acceptance journeys.
The image-composition redesign is already deferred unless its defect recurs
during the E2E campaign.

Work through selected undecided rows in [bug triage](bugs.md) and the acceptance
journeys below, recording fixes, obsolete findings and explicit deferrals. Two
old Codium-specific records are retired after checking the removed command and
implementation against RC0; with the two accepted closures and the legacy
networking retirement, the original list had 14 open bugs. The two new 2026-09-24 records bring
the then-current total to 16 open, including the blocking runtime command defect.
The subsequent installed-IDE reuse report brings the list to 17 open; it has
no release target and requires owner design review before implementation. The legacy command removal changes
runtime source after RC0 and requires RC1 or later; never move RC0.

## Legacy PyCharm Launch Retirement

Owner-authorized 0.2.14 compatibility exception: retire `pycharm run`. We are
currently our only users and everyday dogfood already uses `project run`.
The removed adapter supplied ambient host networking and host-X11 defaults
outside the project configuration path. The command is absent from help;
old invocations return a retirement error before launch or state preparation.
Use `devcapsule project run`, or `devcapsule project --path DIRECTORY run`;
initialize an unconfigured directory with `project --path DIRECTORY init`.
Raw-image/profile options are not translated, and no direct-image replacement
is introduced. The [V1 capability work item](../../work-orders/2026-09-22-legacy-launch-capability-disposition.md)
preserves future product decisions. Shared project launch and the separate
`pycharm build` / `check-runtime` utilities remain.

The legacy networking/parity bug was marked retired first at the owner's
request, then its launch adapter and unused CLI option helpers were removed.
Other PyCharm/component bugs retain their independently applicable scope.
Validation: 115 focused checks and the full `nox -s build` passed (1,046 tests,
18 deselected, one xfail, one quarantined XPASS; mypy, source/PEX smokes and
nine packaged integrations). Direct checks of `dist/devcapsule-local.pex`
reject bare/help/legacy-option launches with the retirement message and create
no checkout state. Log: `/tmp/maintenance-retire-pycharm-run-build.log`.
The dirty-checkout gate deliberately skipped revision-bearing packaging;
RC0 artifacts remain unchanged. No Docker/GUI acceptance was added by this
slice. PR #133 merged the removal commit `1f425f3` at `c8ab2d0`; ancestry
was verified against fetched main on 2026-09-23. The next immutable candidate
is still pending; owner testing starts with the already published RC0.

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
| [v0.2.14-rc1](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.14-rc1) | `cec7a0c2f3467b8cc9d84eca820f35ee869087ec` | Public PEX, checksum and manifest verified 2026-09-24. | Identity checked; local base built and smoke-checked. IDE campaign pending. |

RC1 tag object: `0f460c0cb5a50f9c0fb6f46b4b7ee6060badd572`. Pushed atomically
with the release branch. The public RC1 manifest returned HTTP 404 immediately
after tagging; no successful backend run or published assets are claimed yet.
That initial 404 is superseded by the successful public download below.

RC1 PEX SHA-256: `68c58ec09c1a73e07c3bb1b1f7514341ddddaf645c7fae1ff4ff0763ff6f7689`.
Files: `devcapsule-src/dist/rc1-published/`; executable and manifest identify
`0.2.14rc1`, tag `v0.2.14-rc1`, source `cec7a0c`.
Owner-requested local base: `devcapsule-base:0.2.14-rc1-local`, image
`sha256:0d9a185ec5a2ac04380e9b5540bae2b212356b8b5d4c0f91c7db320d486a414a`.
Built by the downloaded RC1 PEX, recipe `ubuntu-24.04@9`, host-network build.
Metadata and offline tool/display-availability smoke passed; no bundled
runtime or agents. Evidence: `dist/rc1-published/local-base-build.json`;
log `/tmp/maintenance-rc1-base-build.log`. No base registry publication or
lock repin. No fresh GUI or final-release acceptance inferred.

The following artifact evidence describes RC0.

The annotated RC0 tag points to the prepared source, not subsequent record updates.
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

Use the [validation stories](smoke/stories.md) for contracts, pre/postconditions,
actors and separate pass-first/data-reuse dependencies. The old manual walkthrough
has been replaced. Real prompted and unattended initialization and isolated
coordination byte-preservation stories now pass against downloaded RC0; their
[saved evidence](smoke/cli-validation.json) does not imply IDE/service/provider
acceptance. [Runner instructions](smoke/README.md) and the story implementation
table state exactly what is executable and what remains to automate.

Owner observation (2026-09-23): VSCodium “over website devcapsule works as
expected.” This is a positive human observation. Exact executable/candidate,
project path, exercised actions and whether close/reopen was included are not
recorded yet; it does not close the full everyday-work or resume journey.
The new `runner.py launch --project PATH` records subsequent sessions and
explicit observations; `resume` reuses their project and configuration. The
runner has now launched the website's VSCodium session from inside this capsule:
Docker bind translation and desktop readiness succeeded on the second attempt,
after resolving missing local configuration. The owner confirmed "This is
working" for that exact session. The runner subsequently recorded exit 0,
container removal and no monitor errors. The owner also confirmed the file/IDE
resume checklist; attempt 3 passed exit and cleanup checks. Agent-session
continuation and specific edit/debug assertions remain pending. Evidence: local run
`devcapsule-src/dist/rc0-runs/session-7a4dbc068f58/run.json`, attempt 2 and
its human startup observation. Run details and recovery steps are in the
maintenance handoff.

Host-network variant verified by owner on 2026-09-24: runner attempt 4
requested and observed `host` networking, exited 0 and removed its container.
Future local launches use host networking under WORKFLOW-LOCAL.md; deliberate
isolation tests keep their specified mode.

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

Readiness rechecked 2026-09-23: the local base exists with the recorded image
ID, recipe and exact RC0 source labels; the downloaded PEX still matches the
published checksum. Base build inputs have not changed since RC0, so no
rebuild was run. Runtime PEX bytes are supplied when a derived image is
materialized, rather than embedded in this base. The other base recipe,
NVIDIA CUDA, remains `wip` and is outside this RC0 readiness check.

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
