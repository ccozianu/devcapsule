# DevCapsule 0.2.15 — Release Work

Updated: 2026-09-27. Stage: **approved scope expanded; implementation and agent upgrades pending**.
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
[project-management work order at d34fb06](https://github.com/ccozianu/devcapsule/blob/d34fb0672c695acb3a71add510ba6aa414df7f9e/engineering-docs/work-orders/2026-09-27-project-environment-discovery.md).
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

Vendor metadata was fetched directly on 2026-09-27. These are upgrade
candidates, not updated pins or tested installations:

| Agent | Current release pin | Vendor candidate | Metadata source | Disposition |
|---|---|---|---|---|
| Codex | 0.153.4 | 0.157.1 | [OpenAI npm latest](https://registry.npmjs.org/@openai/codex/latest) | Acquire exact meta/platform packages, verify checksums and validate |
| Claude Code | 2.1.261 | 2.1.283 | [Vendor latest channel](https://downloads.claude.ai/claude-code-releases/latest) | Verify exact platform manifest/checksum, then acquire and validate |
| Antigravity CLI | 1.1.24 | 1.2.12 | [Vendor Linux amd64 manifest](https://antigravity-cli-auto-updater-974169037036.us-central1.run.app/manifests/linux_amd64.json) | Verify manifest checksum, acquire and validate |

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
- Candidate gate record: `../v0.2.15-rc0-integration-exception.json`.
  Reconcile it with expanded source and actual main disposition before RC0.
- Historical full gate at `4f28a12`: 1068 passed, 20 deselected, 1 xfailed,
  1 xpassed; mypy clean on 169 files; exact-revision PEX and nine packaged
  checks passed (2026-09-26). This covers only the original init-fix tree.
- [ ] Prepare developer environment in the clean release checkout.
- [ ] Resolve and validate the agent upgrade candidates above.
- [ ] Implement Claude/Antigravity defaults, `/opt/xtras` and `project info`;
  update user-facing help and documentation.
- [ ] Run focused checks and full local gate on the expanded release.
- [ ] Resolve main disposition for all changes before tagging the candidate.
- [ ] Tag `v0.2.15-rc0`, backend publication, downloaded assets verified.
- [ ] Rerun the failing init journey with the downloaded candidate, typo first,
  then corrected through `project run`.
- [ ] Verify xtras persistence and PATH, host/runtime information, and actual
  interactive agent defaults/version behavior using downloaded candidate bytes.
- [ ] Local proofs against downloaded assets per the runbook; final freshness review.
- [ ] Exact-candidate acceptance record, integration to main, final tag and
  verified final assets. Reopen main at 0.2.16.dev0 after publication.

## Candidates

None yet. No implementation or new agent runtime acceptance is claimed by
this scope/metadata checkpoint.

## Release Notes Preparation

Write final adopter notes from the accepted outcomes above, including exact
agent versions and any holdbacks. Do not reuse the former fix-only notes.
Carry forward the unchanged R-COMPAT-001 exception: earlier clients installed
vendor downloads without recording consent; 0.2.14 and later ask once per
checkout. Agent upgrades do not grant new host access or silently replace a
developer's selected version set.
