# DevCapsule 0.2.15 — Release Work

Updated: 2026-09-27. Stage: **final published and verified; main development reopening prepared**.
Driver: **maintenance**. Product owner: Costin Cozianu.

## Scope And Owner Decisions

- Initial 2026-09-26 cut: the init answer-loss fix alone, from `v0.2.14`.
  On 2026-09-27 the owner explicitly expanded the release as listed below.
- Required fix: [`project init` loses interactive answers for an unknown
  configuration name](../../bugs/devcapsule/2026-09-26-init-discards-answers-on-late-authorize-validation.md).
  Fixed on main in PR #143 at `3acc460`; release cherry-pick `9a0567c`
  records main origin `74bc4aa`. The downloaded RC0 and RC1 init-retry journeys passed.
- Persistent `/opt/xtras`: writable without sudo, backed by checkout storage,
  preserving existing `$HOME/xtras`; bin available to IDEs, agents and terminals.
- Read-only `devcapsule project info`: identity, components/versions,
  environment and persistence, on host and inside the capsule, including `/opt`.
- Claude and Antigravity default to ordinary tool execution without approval
  prompts. Preserve explicit user settings and verify fresh interactive starts.
- Attempt current generally available agent versions for this and every release;
  current 0.2.15 candidates and acceptance obligations are below.
- The broader in-capsule project-command guard repair is explicitly non-gating;
  that deferral does not excuse failure of the new `project info` command.
  Previously deferred optimization, cleanup, IDE additions and release-notes
  automation remain outside 0.2.15.

The detailed accepted feature contract is the
[project-management work order](../../work-orders/2026-09-27-project-environment-discovery.md),
imported unchanged from project-management commit `d34fb06`.
Its three mail handoffs are acknowledged in maintenance's published decision
log. The later owner-directed agent freshness review supplements that contract.

Cut source remains `v0.2.14` (`abb785d`), not main. Main's base-contract naming
and images package move remain 0.2.16 material; do not merge main into this
release branch. Apply the release runbook's main-disposition policy separately.

## Agent Freshness Review

Owner direction, 2026-09-27: with every release, try to upgrade at least the
AI agents to their then-current versions so the bundled CLIs keep pace with
vendor models. This starts with 0.2.15 and covers Codex, Claude Code and
Antigravity. Use generally available vendor releases rather than beta/nightly
builds. The release check is required; adoption depends on compatibility and
validation, with a recorded reason and follow-up for a holdback.

Vendor metadata and exact artifacts were fetched directly on 2026-09-27.
The embedded matrix and dogfood/golden locks now select these upgrades;
existing explicit version sets remain unchanged:

| Agent | Previous pin | RC0 pin | Metadata source | Disposition |
|---|---|---|---|---|
| Codex | 0.153.4 | 0.157.1 | [OpenAI npm latest](https://registry.npmjs.org/@openai/codex/latest) | npm SRI verified, offline npm layout and pinned-base startup passed |
| Claude Code | 2.1.261 | 2.1.283 | [Vendor latest channel](https://downloads.claude.ai/claude-code-releases/latest) | Manifest SHA-256 verified; pinned-base startup and bypass mode loading passed |
| Antigravity CLI | 1.1.24 | 1.2.12 | [Vendor Linux amd64 manifest](https://antigravity-cli-auto-updater-974169037036.us-central1.run.app/manifests/linux_amd64.json) | Manifest SHA-512 verified; archive member and pinned-base startup passed |

Before finalizing candidate pins, inspect vendor release notes and supported
artifacts, then verify exact versions and integrity through the trusted
component mechanisms. Update the embedded recommendations and relevant
repository locks/fixtures together; preserve existing checkout version-set
choices and explicit acquisition consent. Do not record an untested
compatibility edge as verified. No independent IDE/base upgrade is implied.

Run the permission-default work and real agent smoke on the selected new
versions: startup, configuration loading, a simple tool action and persistence.
Check intended model discovery/use where the owner's account permits it;
a version bump alone does not establish model entitlement or successful use.
Record the tested platform and what remains unverified.

Recheck vendor pointers before final acceptance. A release that appears during
acceptance gets a recorded adopt-or-hold decision; adopting it changes the
candidate and requires the relevant validation again. Keep an accepted
candidate immutable rather than silently changing pins under its final tag.

The recurring runbook instruction is handed to project-management for its
next resumption; its pause does not block this owner-authorized release review.

## Preparation And Publication

- Release branch starts at `abb785d` (`v0.2.14`), init fix `9a0567c`, version
  `c601fb8`; current pre-expansion tip `1d9a27f`.
- Main disposition: RC0 and RC1 are integrated. PR #145 at `1215795` has
  the tested main-preparation tree (1d1a882) and includes release source a15ff8b;
  main's newer implementation and development version are preserved.
  The former fix-only exception record is removed because its scope is obsolete.
- Historical full gate at `4f28a12`: 1068 passed, 20 deselected, 1 xfailed,
  1 xpassed; mypy clean on 169 files; exact-revision PEX and nine packaged
  checks passed (2026-09-26). This covers only the original init-fix tree.
- [x] Prepare developer environment in the clean release checkout.
- [x] Resolve upgrade pins, verify downloads and test pinned-base startup.
- [x] Owner confirmed RC1 interactive/account-level agent acceptance on 2026-09-27.
- [x] Implement Claude/Antigravity defaults and document managed/adopted behavior.
- [x] Implement `/opt/xtras` and `project info`; update help and documentation.
  Owner agreed to put these in the candidate after RC0.
- [x] RC0 source/local-package gate: 1077 passed, 20 deselected, 1 xfailed,
  1 xpassed; mypy clean on 169 files; nine packaged-runtime checks passed.
- [x] Build and smoke the clean exact-revision release PEX before tagging.
- [x] RC0 integrated by PR #144 at `0770638`; ancestry verified on remote main.
- [x] Tag `v0.2.15-rc0`, backend publication, downloaded assets verified.
- [x] Rerun the failing init journey with the downloaded candidate, typo first,
  then corrected through a real three-agent Codium `project run` and relaunch.
- [x] Downloaded RC1: xtras persistence/PATH, host/runtime information, init retry,
  exact runtime delivery, agent versions and seeded-settings persistence.
- [x] Owner-reported authenticated interactive agent defaults/model behavior.
- [x] Required Docker proofs against downloaded RC1: 7 passed in 201.29 s.
- [x] Vendor freshness rechecked 2026-09-27 20:37 UTC; all pins still current.
- [x] Exact-candidate [acceptance record](../v0.2.15.json), re-downloaded and checksum-verified.
- [x] Acceptance integrated to main; final tag and all three assets verified.
- [ ] Integrate the prepared 0.2.16.dev0 reopening and close-out records.

## Candidates

### RC0 — published 2026-09-27

- Tag `v0.2.15-rc0`; source `d96e0e7ada56dbea3f857777abb28f1bc223ceef`.
- [Published prerelease](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.15-rc0);
  [successful backend run](https://github.com/ccozianu/devcapsule/actions/runs/36340320532).
- Downloaded all three assets. PEX SHA-256:
  `ef7499059a747dff280b3fed31128d9aafa4f6d36ba1c8a46addac6279652014`.
  It agrees with the checksum file and release manifest; the executable reports
  package `0.2.15rc0`, mnemonic `v0.2.15-rc0` and the exact source above.
- Seven Docker proofs passed against that download: no-Python/no-network
  execution, component cache reuse/invalidation, exact runtime delivery on both
  IDE surfaces and both command names, and the pinned-base runtime/display
  session. The suite used the pinned v0.2.12-rc5 base and host build networking;
  intentional network-isolation cases kept their prescribed mode.
- The public CLI, driven through a pseudoterminal in fresh private XDG state,
  rejected `--authorize docker host-socket` with the docker-daemon suggestion
  before prompts or writes. Correcting the name completed interactive init,
  retaining network, Docker and both agent acquisition answers. The first
  harness attempt stopped at an unhandled justification question; a corrected
  harness answered the known questions and passed. No product workaround.
- That initialized project built and launched an actual Codium environment.
  Runtime PEX hash/identity matches the downloaded artifact; on PATH the agents
  report Codex 0.157.1, Claude 2.1.283 and Antigravity 1.2.12. Fresh user settings
  contain the requested defaults. After an explicit stop/removal and a second
  launch, a Claude-slot marker and both settings files survived byte-for-byte.
- Isolated test checkout and evidence:
  `/home/devcapsule/.cache/devcapsule-releases/v0.2.15-rc0/init-smoke-retry`.
  Docker proof log: `/tmp/0215-rc0-docker-proofs.log` (7 passed in 189.60 s).
  Candidate download is in the parent directory. Temporary harnesses are under
  `/tmp/0215-*-smoke.py`; no authentication material was copied.
- The second test session, container `devcapsule-0215-rc0-smoke`, remains running
  for the owner's interactive agent login/tool/model checks. Those checks are
  pending and are not implied by the startup/version or persistence proofs.

RC0 contains the init fix, agent upgrades and agent defaults. `/opt/xtras`
and `project info` follow in the next candidate; all approved scope remains
required for final 0.2.15. This is a candidate checkpoint, not final acceptance.

### RC1 preparation — 2026-09-27

The release tree adds `/opt/xtras` as an alias of persistent home storage,
creates its writable `bin`, and includes that directory on ordinary and login
shell PATH. Image formation identity includes the new layout so old cached
images cannot silently miss it. Existing custom-base content is never replaced.

`project info` supports text/JSON, host discovery and runtime discovery from
outside the project. It captures storage backing at launch, reports running
versions separately from the next selection, and shows only allowlisted
environment values. Explicit paths and nested projects retain their identity.
Managed storage path calculation is shared with the launcher. Updated help,
user guidance and persistence specification accompany the implementation.

- Release local gate: **1081 passed, 20 deselected, 1 xfailed, 1 xpassed**;
  mypy clean on 171 files; nine packaged-runtime checks passed. Log:
  `/tmp/0215-rc1-build.log`.
- A local PEX launched a real Codium/three-agent capsule with host networking,
  no development sudo, a read-only root and UID 1000. An existing
  `$HOME/xtras/gcloud` installation was visible through `/opt/xtras`; an
  executable created in its `bin` worked in ordinary and login shells.
  Both survived removing and replacing the capsule.
- Runtime information from `/opt` and the project agreed. Reported backing
  matched Docker mounts after translating the nested launcher's paths.
  Editing the next-launch Codex selection left the reported running version
  unchanged. Inspection preserved checkout/resolution bytes and omitted an
  injected API-key sentinel. The project lock was restored byte-for-byte.
- The image recipe rejected a pre-existing directory, file and conflicting
  symlink at `/opt/xtras`, preserving each; absent and canonical links succeeded
  idempotently in a disposable container. Separate checkout storage remained
  isolated; focused CLI tests also cover default isolation and an explicit
  shared home binding.
- Fixture evidence is under
  `/home/devcapsule/.cache/devcapsule-0215-xtras-info`; the local test capsule
  was removed after its second run. The RC0 owner acceptance desktop remains
  available. Authenticated agent acceptance is still pending.

The proofs above used local builds. The published RC1 evidence follows;
authenticated owner acceptance still remains.

### RC1 — published 2026-09-27

- Tag `v0.2.15-rc1`; source `a15ff8b58f4af93845c17eaca22f9c9d29c8e000`.
  PR #145 merged at `1215795`; its tree matches tested main preparation 1d1a882.
  The candidate integration gate reports mainline and no unmatched commits.
- [Public prerelease](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.15-rc1);
  [successful backend run](https://github.com/ccozianu/devcapsule/actions/runs/36348273337)
  (3m 5s). Downloaded executable, checksum file and manifest agree on SHA-256
  `52c28999a0a8e83353d060a23ec7b914e781b02269445a4c7a189ea04399e131`.
  The executable reports `0.2.15rc1`, `v0.2.15-rc1` and the exact source above.
- All seven required Docker proofs passed against the downloaded PEX in
  201.29 s: no-Python/no-network execution, component reuse/invalidation,
  launcher/runtime identity on both surfaces/command names, and pinned-base
  runtime/display behavior. Log: `/tmp/0215-rc1-docker-proofs.log`.
- Fresh private-XDG init used the downloaded public CLI through a pseudoterminal.
  The misspelled `docker` authorization failed before prompts or writes;
  corrected `docker-daemon` completed init, retaining network, Docker and
  vendor-acquisition answers. That project launched actual Codium and all
  three agent CLIs with the expected versions and the required settings.
- The runtime PEX hash equals the downloaded launcher hash. With read-only
  root and UID 1000, an existing HOME/xtras installation was visible through
  `/opt/xtras`; its bin was writable and worked on ordinary and login PATH.
  Both installation and executable survived container replacement. Claude and
  Antigravity settings stayed byte-identical, and a Claude-slot marker survived.
- `project info` agreed at host root/descendant and runtime project/`/opt`.
  Storage backing matched actual Docker mounts after nested-launch path
  translation. Changing the next-launch Codex version left running software
  and mounts unchanged. API-key sentinel was omitted; inspection left checkout
  and resolution bytes unchanged. The project lock was restored byte-for-byte.
- Vendor release pointers were rechecked at 20:37 UTC: Codex 0.157.1,
  Claude 2.1.283 and Antigravity 1.2.12 remain current. No holdback is needed.
- Download and fixture evidence:
  `/home/devcapsule/.cache/devcapsule-releases/v0.2.15-rc1`, with the
  `init-smoke-retry` subdirectory containing init transcripts, host/runtime
  reports, settings hashes and run logs. Temporary probe helpers are under
  `/tmp/0215-rc1-*.py`; freshness evidence is `/tmp/0215-rc1-freshness.json`.
- The owner confirmed “It's all good, working as expected” in response to
  the RC1 Claude/Antigravity sign-in, file/shell tool execution without
  approval prompts and desired-model access checks. This is owner-reported
  acceptance, distinct from the agent's machine proofs above. No specific
  model name or performance result is inferred.
- Both temporary test containers are now absent: RC1 had already exited,
  and RC0 was stopped after acceptance.
  Their persistent fixture storage is retained; no account material was
  copied into Git and desktop access tokens remain untracked.

## Final Promotion

Accepted candidate: `v0.2.15-rc1`. The reviewed
[acceptance record](../v0.2.15.json) names Costin Cozianu, candidate SHA-256
`52c28999a0a8e83353d060a23ec7b914e781b02269445a4c7a189ea04399e131`, source
`a15ff8b58f4af93845c17eaca22f9c9d29c8e000` and preparation baseline
`abb785d7ad4069606fd3ab84009ca8efeabc22b9` (`v0.2.14`). The helper re-downloaded
and verified the published candidate when preparing that record.

The acceptance record and post-candidate evidence reached main through PRs
#148 and #146. SSH fetch verified main `82a1b5d9ee4bf815d0d9dc53a4eab4727ace52bd`
has the exact tested preparation tree. The local final gate passed before
pushing annotated `v0.2.15` at accepted source a15ff8b. The release branch
remains at 95c7bad and is retained, together with the immutable candidate tags.

[Final release](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.15)
is public and marked Latest. The
[final backend](https://github.com/ccozianu/devcapsule/actions/runs/36353476393)
completed successfully in 3m 13s. All three assets were freshly downloaded:
executable, checksum and manifest. Final SHA-256:
`0e66b9d9947aa447b53d0466d57de3290bb85ca07309df2d739baf82e4c5e113`.

The executable reports version `0.2.15`, mnemonic `v0.2.15` and exact accepted
source `a15ff8b58f4af93845c17eaca22f9c9d29c8e000`; its help command passes.
Checksum and manifest agree. Frozen file, dependency, Python and base inputs
match RC1, and inspection of the final PEX reproduces the manifest inputs.
The embedded promotion record matches main's acceptance record and captures
main 82a1b5d. Final bytes intentionally differ from RC1 through final-version
metadata. RC1's downloaded Docker and owner-interactive acceptance are reused;
no additional final GUI/provider or Docker round is claimed.

Downloads are under `/home/devcapsule/.cache/devcapsule-releases/v0.2.15`.
Local gate evidence: `/tmp/0215-final-gate.json`; final verification helper:
`/tmp/0215-verify-final.py`. They are regenerable from the published release.
Main reopens at 0.2.16.dev0 through `ws-maintenance/post-0.2.15`, carrying this
close-out evidence. Its full gate passed: 1089 source tests, type checks over
174 files, nine packaged checks and exact/local PEX smokes; log
`/tmp/0215-closeout-build.log`. The final adopter notes below are ready for the owner to
use in the GitHub release body; automated publication currently supplies the
changelog link.

## Release Notes Preparation

Write final adopter notes from the accepted outcomes above, including exact
agent versions and any holdbacks. Do not reuse the former fix-only notes.
Carry forward the unchanged R-COMPAT-001 exception: earlier clients installed
vendor downloads without recording consent; 0.2.14 and later ask once per
checkout. Agent upgrades do not grant new host access or silently replace a
developer's selected version set.


## RC0 Agent Evidence (2026-09-27)

- Exact artifacts passed vendor integrity checks before execution: both Codex
  npm SHA-512 SRI values, Claude manifest SHA-256, and Antigravity manifest
  SHA-512. Computed SHA-256 values are in the committed matrix and locks.
  The existing Codex distribution adapter also accepted 0.157.1 and its
  platform alias/Node contract.
- Release notes reviewed: [Codex 0.157.1](https://github.com/openai/codex/releases/tag/rust-v0.157.1)
  has no detailed highlights; [Claude changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
  includes gateway, model-selection and moved-config fixes; Antigravity's own
  `changelog` command reports its 1.2.12 terminal/rendering fixes. No artifact
  layout or required Node change was found.
- A disposable container on the exact pinned base
  `sha256:8837edd36720763796ab9fe1dbeb66f1aa7ca2db0dabc8d73a58716440f42f7c`
  used host networking and a fresh non-root user. Codex installed both
  checksum-verified tarballs with offline npm and scripts disabled, preserving
  its full package layout. All three executables reported the pinned versions.
- Actual launcher seeds were placed before CLI execution. Codex `features list`
  accepted its existing TOML. Claude's headless initialization reported
  `permissionMode: bypassPermissions` without a command-line permission override.
  The 2.1.283 binary's settings schema and user-settings lookup recognize
  `skipDangerousModePermissionPrompt`; both properties survived startup.
  Antigravity reached its normal authentication flow and retained
  `toolPermission: always-proceed`.
- No account was imported into this disposable smoke. Claude and Antigravity
  consequently stopped at authentication. Interactive first-use notice
  suppression, actual file/shell actions, model entitlement and persistence
  across candidate container replacement remain acceptance tasks. The matrix
  edges explicitly remain provisional for those provider checks.
- Regression coverage exercises fresh settings, missing-key upgrades, nested
  permission preservation, explicit opt-outs, byte/mtime idempotence, malformed
  and non-object JSON, linked settings and adopted external slots. Codex's
  absent-file-only behavior remains covered.
- Initial gate attempts hit temporary-filesystem capacity and Unix socket path
  limits in this container. Test scratch was moved to short disk-backed
  `/opt/d215`; no product workaround or weakened test was introduced.

## Final Adopter Notes

DevCapsule 0.2.15 makes project setup and everyday environment adjustments easier.

- `project init` now catches misspelled configuration names before asking questions or writing files, and suggests the correct name. Correcting a typo no longer means losing the answers you just entered.
- Install additional tools under `/opt/xtras` without sudo. It points to persistent `$HOME/xtras`, preserving existing installations; `/opt/xtras/bin` is available on PATH. Storage belongs to the checkout by default and follows any explicitly selected home binding. You manage these tools and their updates.
- `devcapsule project info` shows component versions, provided environment variables and persistent/temporary storage. It works on the host from the project or a descendant, and anywhere inside its capsule. Runtime output separates running software from the next-launch selection. `--json` supports agent use; secret values are omitted.
- New managed Claude and Antigravity settings use the requested no-tool-approval defaults. Missing properties are added to valid managed settings; explicit choices, malformed files and adopted external state remain intact. Codex retains its existing defaults.
- Updated recommendations: Codex 0.157.1, Claude Code 2.1.283 and Antigravity CLI 1.2.12. Existing project locks and selected version sets remain unchanged until you choose to update them.

Authentication and model access still use your own provider account. Tools stored under `/opt/xtras` are not automatically installed on another machine or recorded in the component lock. The broader in-capsule project-command diagnostic issue remains deferred.

Migration: upgrading the launcher does not grant new host permissions. Checkouts created by older clients may still need the one-time vendor-download consent introduced in 0.2.14.
