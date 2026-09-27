# DevCapsule 0.2.15 — Release Work

Updated: 2026-09-27. Stage: **RC0 published; machine checks passed; interactive agent acceptance pending**.
Driver: **maintenance**. Product owner: Costin Cozianu.

## Scope And Owner Decisions

- Initial 2026-09-26 cut: the init answer-loss fix alone, from `v0.2.14`.
  On 2026-09-27 the owner explicitly expanded the release as listed below.
- Required fix: [`project init` loses interactive answers for an unknown
  configuration name](../../bugs/devcapsule/2026-09-26-init-discards-answers-on-late-authorize-validation.md).
  Fixed on main in PR #143 at `3acc460`; release cherry-pick `9a0567c`
  records main origin `74bc4aa`. Candidate acceptance remains pending.
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
- Main disposition: prepare an ordinary merge of the RC0 release slice into
  main, preserving main's newer implementation and development version. Verify
  remote ancestry after the owner merges the PR, then tag the release commit.
  The former fix-only exception record is removed because its scope is obsolete.
- Historical full gate at `4f28a12`: 1068 passed, 20 deselected, 1 xfailed,
  1 xpassed; mypy clean on 169 files; exact-revision PEX and nine packaged
  checks passed (2026-09-26). This covers only the original init-fix tree.
- [x] Prepare developer environment in the clean release checkout.
- [x] Resolve upgrade pins, verify downloads and test pinned-base startup.
- [ ] Interactive/account-level agent acceptance with downloaded candidate.
- [x] Implement Claude/Antigravity defaults and document managed/adopted behavior.
- [ ] Implement `/opt/xtras` and `project info`; update help and documentation.
  Owner agreed to put these in the candidate after RC0.
- [x] RC0 source/local-package gate: 1077 passed, 20 deselected, 1 xfailed,
  1 xpassed; mypy clean on 169 files; nine packaged-runtime checks passed.
- [x] Build and smoke the clean exact-revision release PEX before tagging.
- [x] RC0 integrated by PR #144 at `0770638`; ancestry verified on remote main.
- [x] Tag `v0.2.15-rc0`, backend publication, downloaded assets verified.
- [x] Rerun the failing init journey with the downloaded candidate, typo first,
  then corrected through a real three-agent Codium `project run` and relaunch.
- [ ] Verify xtras persistence and PATH, host/runtime information, and actual
  interactive agent defaults/version behavior using downloaded candidate bytes.
- [ ] Local proofs against downloaded assets per the runbook; final freshness review.
- [ ] Exact-candidate acceptance record, integration to main, final tag and
  verified final assets. Reopen main at 0.2.16.dev0 after publication.

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
