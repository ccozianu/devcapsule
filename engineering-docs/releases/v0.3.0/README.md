# DevCapsule 0.3.0 — Release Work

Updated: 2026-10-18. Stage: **candidate 0 published and verified as downloaded; the owner's test on the other checkout next**.
Driver: **maintenance**. Product owner: Costin Cozianu.

[Changelog since 0.2.15](changelog.md) ·
[Bug table](bugs.md) ·
[Work order](../../work-orders/2026-10-18-release-0-3-0.md) ·
[Scope and cut decision](../../wip/2026-08-09-project-management/2026-10-18-decision-release-0-3-0-scope-and-cut.md) ·
[Runbook](../../implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md)

Update this file as decisions and evidence arrive. Chat highlights changes
and questions; the bug records remain authoritative for individual status,
ownership and technical evidence; the maintenance status file links here
for resumption.

## Headline

The capsule web console, persistent session diagnostics, and a launcher
that is honest about what it skips.

## Scope And Owner Decisions

- **Cut now**, decided 2026-10-18 after the inventory of what the plan still
  had unimplemented: a candidate of what exists is worth validating, and
  the candidate cycle is the better place for the remaining launcher work,
  with 0.2.14 as the precedent. `main` stays at `0.2.16.dev0` until the
  final tag, then reopens at `0.3.1.dev0` unless the owner names another.
- **Dogfooding during the cycle.** Six items are implemented during the
  candidate cycle, each a maintenance slice with the implementor-and-reviewer
  loop, landing on the release branch by the owner's direction and reaching
  `main` by the merge before each candidate tag: the universal `network`
  authorization node; C10, the first-session terminal summary and Ctrl+C
  ending with a result; forced configuration, `project config resolve
  --force` and `project run --force-config`, mandatory needs split from
  optional ones; the diagnostics snapshot and export command; cleanup of
  obsolete images and cached files, design reviewed with the owner first;
  C20, release notes and documentation automation, last. Features landing
  on a release branch during a candidate cycle are the owner's direction
  for this release, as the decision asks this overview to record; a
  standing local rule is `workflow-improvements`' to propose if it recurs.
- **Out of 0.3.0:** consent and vendor trust (D-0010 to D-0013,
  `component-upgrades`); installed-IDE reuse with an empty launcher cache;
  browser evidence for the diagnostics; the web console's deliverable 6,
  materialized views; ecosystem-aware project bootstrap, retargeted to 0.9
  on 2026-10-11 and applied with the cut. Their next home is 0.3.1 or the
  next cycle, decided at that planning.
- **Gates before the final tag:** the owner's eleven user-docs proposal
  decisions, the gate of 2026-09-28; the documentation describing the
  accepted candidate, C16; a published base for the candidate, since the
  console needs recipe 11; the fixed bug records verified against a
  downloaded candidate; the release notes as `notes.md` beside this file.
  Project-operation instructions, C17, stay assigned to
  `workflow-improvements` for 0.3.0 and gate the final tag.
- **Stopping points where the owner is consulted:** before each candidate
  tag; before the image-cleanup implementation; when a slice proves larger
  than the cycle tolerates; before the final tag. Scope changes go by the
  decision record's reopen rule.
- Routine release-fix propagation to `main` follows the runbook's *Release
  Fixes And Main* under the owner's standing direction of 2026-09-22.

## What `main` Carried At The Cut

Integrated between `v0.2.15` (final 2026-09-27) and the cut commit, by the
merges on `main`'s first parent:

- The capsule web console, first iteration (#184, #190) and the second
  (#192 to #206, delivered through #201 on `main`), with the notifications
  and decisions groups under `project checkout`.
- Persistent session logs: one file per component, a WARNING baseline, a
  host-backed directory per session (#207); in-process rotation and one
  budget per checkout (#209, #216).
- Maintenance after 0.2.15 (#164, #168, #169, #172): the fresh-workspace
  recursive test, the in-capsule project-command fix, named build contexts,
  the unpacked-cache corrections.
- IntelliJ IDEA and the configuration contract commands from
  `component-catalog` (#163 to #173).
- The user documentation of 43 pages, the website producer migration and
  the versioned documentation live on the site (#151 to #158), the landing
  page identity and the comparison (#219, #221, #222).
- Workflow and coordination records from `project-management` and
  `workflow-improvements` (#159, #162, #176 to #183, #214, #215, #220).

## Agent Freshness Review

Owner direction of 2026-09-27, applied to every release: try to upgrade the
supported agent CLIs to their current generally available versions. The
vendor pointers were read on 2026-10-18 at 12:59 UTC, with the sources the
0.2.15 review used.

| Agent | Current pin | Vendor current | Source consulted | Disposition |
|---|---|---|---|---|
| Codex | 0.157.1 | 0.163.0 | [OpenAI npm latest](https://registry.npmjs.org/@openai/codex/latest) | adopted provisionally, matrix embedded-27 on the slice branch; provider acceptance on the downloaded candidate |
| Claude Code | 2.1.283 | 2.1.302 | [Vendor latest channel](https://downloads.claude.ai/claude-code-releases/latest) | adopted provisionally, matrix embedded-27 on the slice branch; provider acceptance on the downloaded candidate |
| Antigravity CLI | 1.2.12 | 1.4.2 | [Vendor Linux amd64 manifest](https://antigravity-cli-auto-updater-974169037036.us-central1.run.app/manifests/linux_amd64.json) | adopted provisionally, matrix embedded-27 on the slice branch; provider acceptance on the downloaded candidate |

Every vendor was ahead of the pin. The attempt, the same day, on the
slice branch `ws-maintenance/0.3.0-agent-freshness` for a pull request
into the release branch:

- **Artifacts.** The four downloads were checked against the vendors' own
  integrity values before their SHA-256 was recorded in the matrix: npm's
  SHA-512 for `codex-0.163.0.tgz` and `codex-0.163.0-linux-x64.tgz`, the
  Claude manifest's SHA-256 for the 2.1.302 binary, the Antigravity
  manifest's SHA-512 for the 1.4.2 archive, whose member is still
  `antigravity`. Codex still requires Node 16 or newer; the base carries
  22. No layout change was found in any of the three.
- **Startup on the base.** A disposable container on the local recipe-11
  base `devcapsule-base-e2e:v0.2.16.dev0-local-linux-x86_64-36bef9f1e151`
  (Ubuntu 24.04.5, Node 22.23.1, npm 10.9.8), host networking, fetched
  the artifacts again and verified them, laid Codex out with the same
  offline `npm install` the image build emits, and started each CLI as a
  fresh uid-1000 user with DevCapsule's seeds in place: `codex --version`
  reported `codex-cli 0.163.0`, `codex features list` printed its 175
  flags over the seeded `config.toml` and `codex exec --help` answered;
  `claude --version` reported `2.1.302 (Claude Code)`, and a headless
  prompt answered with a JSON result record and stopped at the missing
  account while its debug log recorded `mode=bypassPermissions
  flag=false(fallback)`, the seeded default taken without a command-line
  override; `antigravity --version` reported `1.4.2`, its help and
  `changelog` printed. The three seed files were byte-identical after the
  starts. Not shown without an account: an actual tool action, model
  entitlement, the first-use notices; those are the owner's acceptance
  on the downloaded candidate, as in 0.2.15.
- **Matrix.** `embedded-27`: the three pins, provisional verified edges on
  the Ubuntu 24.04 family, the golden locks regenerated, the init tests
  naming Antigravity 1.4.2. The earlier pins stay, so locks that select
  them keep resolving.
- **The repository's own lock is the owner's step.** The gate test that
  resolves this checkout's need against the matrix fails until
  `.devcapsule/devcapsule.linux-amd64.lock` carries the new pins, and the
  local rule lets only a DevCapsule command write it, outside the capsule.
  One command on the host, with a build of the slice branch's source
  (`devcapsule-src/dist/devcapsule-local.pex` in the shared checkout):

  ```text
  cd /home/costin/work.provisional/costin3/myProjects/devcapsule
  devcapsule-src/dist/devcapsule-local.pex project config capabilities \
    --required antigravity-agent claude-code-agent codex-agent docker-cli python python-ide
  devcapsule0 project config check
  ```

  The first regenerates the lock from the matrix; the second validates the
  written result with the known baseline. Until it runs, the slice is not
  gated and rc0 cannot carry the new pins; the alternative is rc0 on the
  current pins and the upgrade in rc1, the owner's word either way.

The pointers are rechecked before final acceptance, and a version that
appears meanwhile gets an adopt-or-hold decision here, never a silent
replacement.

## Preparation And Publication

- Release branch `release-0.3.0` starts at the preparation baseline
  `3c91183ffd2130f6c7b40d2f9e3fd41588f977eb`, `main` at the merge of PR
  #223, selected by the driver: nothing of maintenance was unmerged, and
  the commit carries the decision and the work order. Version 0.3.0 at
  `6965c5e`, the branch's first commit, by `nox -s bump -- 0.3.0`.
- [x] Cut, version, the work order acknowledged, the bootstrap record
  retargeted, the registry row and the status file on the release branch.
- [x] Full gate on the release branch at the version commit: distribution
  version, syntax, mypy clean over 214 files, 1584 unit tests passed, CLI
  smoke, test PEX built and smoked, packaging integration 17 passed; the
  documentation contract passed after the manifest's release-branch line
  (`source-version: "0.3.0"` on the `devel` entry, a judgment recorded in
  the status file and mailed to project-management as a contract gap); the
  web console session mypy clean over 8 files, 293 tests.
- [x] Agent freshness upgrade attempt; dispositions in the table above.
- [x] PR #224 merged into the release branch at `6b97657`; the release branch merged into `main` by PR #228 at `7c20292`, ancestry holds; `main` carries 0.3.0 during the cycle by the owner's merge. The branch, deleted by `delete_branch_on_merge`, restored at the same tip.
- [ ] The owner regenerates the shared lock on the host; the written lock committed on the release branch, gated, merged to `main`.
- [x] `v0.3.0-rc0` tagged on the release branch at `53ebc17`; backend run
  passed; the three assets downloaded, checksum and version verified.
- [ ] Local proofs against the download: clean machine, component cache,
  runtime session on the pinned base.
- [ ] The dogfooding slices, each merged to `main` before the next
  candidate tag; the bug records closed on candidates.
- [ ] The gates before the final tag; `notes.md`; the acceptance record;
  the final tag; delivery verified; `docs/versions.yaml` promoted on `main`.

## Candidates

### RC0 — tagged 2026-10-18

- Tag `v0.3.0-rc0` on `53ebc17705bf99461bbbbf3c4a128228a14c0d51`, the
  release branch's tip at the pre-candidate merge (PR #231 from the
  throwaway copy); the two record commits after it on the branch carry no
  source. The source is byte-identical to the tree the full gate passed on
  2026-10-18 (PR #230's branch: 1584 unit tests, packaging, documentation
  contract, web console), and the hosted unit run passed on PR #231.
- Candidate gate, run locally from a detached checkout of the tag before
  the push: method `mainline`, no unintegrated commits, version
  `0.3.0rc0`.
- Pushed atomically with the branch; backend run
  [39175482525](https://github.com/ccozianu/devcapsule/actions/runs/39175482525).
  The run passed (`Build, publish, and prove`), and the
  [prerelease](https://github.com/ccozianu/devcapsule/releases/tag/v0.3.0-rc0)
  is public, non-draft, with the three assets.
- Downloaded over HTTPS into a fresh directory,
  `/home/devcapsule/.cache/devcapsule-releases/v0.3.0-rc0`: the checksum
  file verifies the executable, SHA-256
  `5d0f0e6c60e72eb291ce5de18036b10c5496b71cfce4e5c7076fe60cd195a6b1`, and
  the manifest records the same value, the tag, the release branch, the
  source revision `53ebc17…` and the gate's `mainline` disposition. The
  executable reports version `0.3.0rc0`, mnemonic `v0.3.0-rc0` and that
  source revision; its help answers.
- What it carries, beyond 0.2.15: everything `main` had at the cut (see
  above), the agent pins Codex 0.163.0, Claude Code 2.1.302 and
  Antigravity CLI 1.4.2, and the launchable-lock test.
- Owner-reported, 2026-10-18: the downloaded candidate, installed as
  `devcapsule-local` on the host and reporting `v0.3.0-rc0`, package
  `0.3.0rc0`, source `53ebc17…`, ran `project run` on the second
  DevCapsule checkout and the capsule launched the first time. This is
  the owner's evidence, distinct from the agent's machine proofs; the
  interactive agent and console checks continue there. The local Docker
  proofs against the download, clean machine, component cache, runtime
  session on the pinned base, follow once the owner's session on that
  daemon is done.

## Release Notes Preparation

Write `notes.md` beside this file before the final tag: plain Markdown for
adopters, what changed for them, compatibility exceptions with remedies,
the tested agent versions and holdbacks from the freshness review, the
deferred items. C20, the last slice of the cycle, makes the notes block and
the manifest promotion need no operator step.
