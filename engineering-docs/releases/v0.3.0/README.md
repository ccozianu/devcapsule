# DevCapsule 0.3.0 — Release Work

Updated: 2026-10-25. Stage: **candidate 5 published and verified as downloaded; it carries the capabilities and components model; the owner's test on the download next, then the diagnostics snapshot, image cleanup and C20**.
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
  `workflow-improvements` for 0.3.0 and gate the final tag. Added by the
  owner's direction of 2026-10-24, on reading the candidate-4 stack: a
  language review of the user documentation, which reads as machine prose
  and whose sections lack a conceptual entry page, the configuration
  section first; booked with `project-management` by mail at
  `9fcfdb8db440`, which assigns the reviewer and the method.
- **Rulings of 2026-10-21.** The base publication happens later, in the
  promotion of the accepted candidate, not before the next one. The
  candidates are grouped: rc2 carries the network node and C10; rc3 forced
  configuration and the diagnostics snapshot; rc4 image cleanup and C20.
  C17 stays a gate in both halves, the generic rule in `WORKFLOW.md` with
  `workflow-improvements` and this project's own operating instructions in
  `WORKFLOW-LOCAL.md`, the concrete case against which the abstract rule is
  debugged.
- **Direction of 2026-10-24.** Candidate 3 is tagged now with what the
  release branch carries, software approvals at launch (PR #250) and the
  saved Docker arguments (PR #253), because the owner needs the extra
  Docker arguments to test development scenarios, environment variables
  and GPUs among them. Forced configuration and the diagnostics snapshot,
  grouped into rc3 on 2026-10-21, move to rc4 with image cleanup and C20;
  the manifest's schema-version slice goes with them. The regenerated
  shared lock rides rc3, so provider acceptance of the new agent pins on
  a downloaded candidate becomes possible there.
- **Direction of 2026-10-24, evening.** Candidate 4 is tagged with the
  CLI UX redesign, the stack of PRs #260 to #269 the owner merged the same
  day: the manifest's schema 2 with the owner's `require`, `offer`, `drop`
  and `recommend` commands; the checkout commands; `run` deriving the plan
  with no resolve step; workstation trust (D-0011); the console writing
  through the launcher; the documentation and the candidate-4 changelog.
  Forced configuration is superseded by the redesign: there is no resolve
  step to force and `run --force-config` is retired. The diagnostics
  snapshot, image cleanup and C20 move to the next candidate. The
  documentation language review is a gate before the final tag (above).
- **Direction of 2026-10-25.** Candidate 5 is tagged with the capabilities
  and components work order, the three slices the owner merged the same
  day (#276, #277, #279): one model of capabilities provided by
  components, the IDE the only special role; agents as ordinary
  capabilities; the SDK major removed, old files still read; a minimum
  on a requirement; the resolution recommendation; the developer's
  `add`, `omit`, `restore`, `use`; every retired spelling deleted; the
  configuration documentation rewritten on the model, with its entry
  page. The diagnostics snapshot, image cleanup and C20 move to the next
  candidate.
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
- [x] The shared lock regenerated on 2026-10-22 by `project config capabilities` on a fresh clone inside the capsule, where the command runs for any project but the capsule's own; committed on the release branch at `0c1a555`, gated (1672 unit tests), proven by the recursive attached launch from a fresh clone; merges to `main` with the next pre-candidate merge.
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
- Owner-reported, 2026-10-19: with the candidate's own builder, the owner
  built a recipe-11 base on the host (`images build --type base
  --recipe ubuntu-24.04 --network host --source-revision 53ebc17…`),
  selected it for the second checkout with `config authorize base-image`,
  resolved and launched: the web console answered on the printed link.
  The first finding of the day, the console link on the recipe-9 base,
  is the bug record below; the console itself works on the base the
  release will publish.

### RC1 — tagged 2026-10-19

- Tag `v0.3.0-rc1` on `7016cdd7cbd373204c4ae0b9fcb01cede3433d94`, the
  release branch's tip after the merge of PR #232 and the pre-candidate
  merge into `main` by PR #233 from the throwaway copy `4PR-2-release-0.3.0`.
- Candidate gate from a detached checkout of the tag before the push:
  method `mainline`, no unintegrated commits, version `0.3.0rc1`.
- What it adds to rc0: the console-link fix, the launcher announcing the
  web console only on a base that has one, and the local-base guide. The
  candidate verifies the fix against the published recipe-9 base and a
  recipe-11 base and closes the bug record.
- Backend run [39265210147](https://github.com/ccozianu/devcapsule/actions/runs/39265210147)
  passed; the [prerelease](https://github.com/ccozianu/devcapsule/releases/tag/v0.3.0-rc1)
  is public, non-draft, with the three assets, and the changelog is its
  body.
- Downloaded over HTTPS into `/home/devcapsule/.cache/devcapsule-releases/v0.3.0-rc1`:
  the checksum file verifies the executable, SHA-256
  `4022a1828575eb24ac029d8915e5fb3a29f191aed4e9aab2ca9b2d1f6452cfc0`, the
  manifest records the same value, the tag, the branch, the source
  revision and the `mainline` disposition; the executable reports
  `0.3.0rc1`, `v0.3.0-rc1` and `7016cdd…`, and its help answers.
- Verified by the owner, 2026-10-21: on the published recipe-9 base the
  launcher prints the substitute line and no link; on the local recipe-11
  base the link works and the console answers. The bug record is closed.
  The owner's judgment of the console: it works nicely, to the extent
  required for 0.3.0.

### RC2 — tagged 2026-10-22

- Tag `v0.3.0-rc2` on `e5b5a8b73309959f9407e115dcb3acd8707d6050`, the release
  branch's tip at the pre-candidate merge (PR #249 from the throwaway copy
  `4PR-3-release-0.3.0`, which carried one commit keeping `main`'s version
  files); the record commits after it on the branch carry no source.
- Candidate gate from a detached checkout of the tag before the push:
  method `mainline`, no unintegrated commits, version `0.3.0rc2`.
- Backend run [39803285881](https://github.com/ccozianu/devcapsule/actions/runs/39803285881)
  passed; the [prerelease](https://github.com/ccozianu/devcapsule/releases/tag/v0.3.0-rc2)
  is public, non-draft, with the three assets.
- Downloaded over HTTPS into `/home/devcapsule/.cache/devcapsule-releases/v0.3.0-rc2`:
  the checksum file verifies the executable, SHA-256
  `abb9a8e18f6688326b7a94aae5b504ccdfa1e1782f1215465857eb9a03d9ba7e`; the
  manifest records the tag, the branch, the source revision and the
  `mainline` disposition; the executable reports `0.3.0rc2` at `e5b5a8b…`.
- The shared lock is not in rc2: it was regenerated after the tag and
  rides the next candidate. Provider acceptance of the new agent pins on a
  downloaded candidate stays the owner's.

- Carries, beyond rc1: the universal `network` authorization node (PR #240,
  review #242 by the Codex pair); the first-session summary and Ctrl+C
  ending with a result (PR #244, review #246 by the Antigravity pair), the
  session's log paths printed at its end; the listing's source label for
  workstation defaults. Each slice gated in full on its merged branch; the
  interrupted-launch end-to-end test passed on a real fresh VSCodium
  launch.
- The release branch synchronized with `main` twice on 2026-10-22, on the
  owner's word, so the cycle's workflow rules and both checkouts' records
  bind it; the version files kept the release side.
- Next: the owner's dogfooding of the terminal and of Ctrl+C, and the three
  records' verification: the IDE smoke on a fresh project, the interrupted
  launch, the quiet terminal.

### RC3 — tagged 2026-10-24

- Tag `v0.3.0-rc3` on `a22a21585f353c269c566686fe348e99959a91cd`, the release
  branch's tip at the pre-candidate merge (PR #257 from the throwaway copy
  `4PR-4-release-0.3.0`, merged by the owner at `cf760b8`); the record
  commits after it on the branch carry no source.
- Candidate gate from a detached checkout of the tag before the push:
  method `mainline`, no unintegrated commits, version `0.3.0rc3`.
- Backend run [40052369307](https://github.com/ccozianu/devcapsule/actions/runs/40052369307)
  passed; the [prerelease](https://github.com/ccozianu/devcapsule/releases/tag/v0.3.0-rc3)
  is public, non-draft, with the three assets.
- Downloaded over HTTPS into `/home/devcapsule/.cache/devcapsule-releases/v0.3.0-rc3`:
  the checksum file verifies the executable, SHA-256
  `be739875ac75da0188f1330ebc6ca25805f2fb0257650ed986f2e9f7212c39bb`; the
  manifest records the tag, the branch, the source revision and the
  `mainline` disposition; `devcapsule version` reports `0.3.0rc3` at `a22a215…`.

- Carries, beyond rc2: software approvals at launch, the one y/n for new
  versions of software approved before and `project config approve`
  (PR #250, review #251 by the Codex and gpt-6-astra pair); the saved
  Docker arguments for each checkout, `set-extra-docker-args`,
  `list-extra-docker-args`, `remove-extra-docker-args` and the `set-env`,
  `list-env`, `unset-env` conveniences on the same list, with inline
  environment values masked in every report (PR #253, review #255 by
  Claude Code); the shared lock regenerated on matrix embedded-27, Codex
  0.163.0, Claude Code 2.1.302, Antigravity CLI 1.4.2 (`0c1a555`). Each
  slice was gated in full on its merged branch.
- Full gate on the release tip before the pre-candidate merge: mypy clean
  over 224 files, 1769 unit tests passed, 36 deselected, 2 xfailed,
  packaging integration 17 passed, the documentation contract 188 pages,
  the web console clean with its tests passed; posted on PR #257.
- Next: the owner's test of the saved Docker arguments and of the
  approvals prompt on the download; provider acceptance of the new agent
  pins, which this candidate's lock makes possible; the network node's
  check on a fresh project, still open from rc2.
- Not in rc3: forced configuration, the diagnostics snapshot, the
  schema-version slice; see the direction of 2026-10-24 above.

### RC4 — tagged 2026-10-24

- Tag `v0.3.0-rc4` on `78a9c6617226599f457504929d747faa9387830b`, the release
  branch's tip at the pre-candidate merge (PR #274 from the throwaway copy
  `4PR-5-release-0.3.0`, merged by the owner at `c04cb4e`).
- Candidate gate from a detached checkout of the tag before the push:
  method `mainline`, no unintegrated commits, version `0.3.0rc4`; record at
  `/opt/devcapsule-gate/rc4-release-protocol.json`.
- Backend run [40123896286](https://github.com/ccozianu/devcapsule/actions/runs/40123896286)
  passed; the [prerelease](https://github.com/ccozianu/devcapsule/releases/tag/v0.3.0-rc4)
  is public, non-draft, with the three assets.
- Downloaded over HTTPS into `/home/devcapsule/.cache/devcapsule-releases/v0.3.0-rc4`:
  the checksum file verifies the executable, SHA-256
  `474fea1e04a5c87f99cac61ec50d980a88244f1ed9a74a267eb0e7ef51494995`; the
  manifest records the tag, the branch, the source revision and the
  `mainline` disposition; `devcapsule version` from an empty directory
  reports `0.3.0rc4`, build `v0.3.0-rc4`, at `78a9c66…`.
- Next: the owner's test of the redesigned commands on the download,
  `init`, `config require|offer|recommend`, `config show|check`, `run`
  asking at the terminal, `config trust`, the console's configuration
  requests; then the diagnostics snapshot, image cleanup and C20 for the
  next candidate; provider acceptance of the agent pins and the network
  node's check on a fresh project, still open.

How the candidate was prepared:

- The release branch's tip after the owner's merge of the stack is
  `3cc8a50`, PR #269. The full gate on it: mypy clean over 242 files,
  2091 unit tests passed, 36 deselected, 1 xfailed, 1 xpassed; the
  packaging integration failed one test of seventeen,
  `test_built_pex_authors_shared_policy_and_keeps_personal_selection_local`,
  which authored a project with the old spellings and expected `config
  check` to pass with the base channel neither trusted nor consented to,
  and expected the retired `--sdk-major` flag to resolve. Both
  expectations predate the redesign: `check` reports the pending channel
  with status 3, and the old flag refuses with a migration note. The test
  now asserts the pending check, accepts the channel under its isolated
  configuration home, and refuses the SDK major through `config require
  tool`; `fe886ad` on the release branch, a test-only change. The unit
  gate never ran this test, so the slices' gates could not see it; the
  packaging integration runs only in `nox -s build` against the built
  executable.
- Full gate on `fe886ad`: mypy clean over 242 files, 2091 unit tests
  passed, packaging integration 17 passed, the web console session clean
  with its tests passed; the documentation contract passed on the same
  `docs/` content, 188 pages, at the slice-6 tip.
- The throwaway copy `4PR-5-release-0.3.0`, the release tip plus the
  cherry-pick of `62fa063` keeping `main`'s version files, test-merged
  into `main` cleanly and was PR #274, merged by the owner; the tag
  followed on the release tip, `78a9c66`, the record commit.
- Carries, beyond rc3: the CLI UX redesign of the direction above, every
  slice reviewed by the Codex and gpt-6-astra pair (#262, #264, #267,
  #270, #271, #272) with the reviews merged. The resolution matrix is
  still embedded-27 with the recipe-9 base, so an existing lock
  regenerated by this candidate is byte-identical.
- Not in rc4: the diagnostics snapshot, image cleanup, C20; the gaps the
  docs reviewer found and the candidate-4 changelog lists under *Not in
  candidate 4*.

### RC5 — tagged 2026-10-25

- Tag `v0.3.0-rc5` on `03ed3483608de97ebf7770149fd25544e8387b49`, the release
  branch's tip at the pre-candidate merge (PR #280 from the throwaway copy
  `4PR-6-release-0.3.0`, merged by the owner at `35d74d9`).
- Candidate gate from a detached checkout of the tag before the push:
  method `mainline`, no unintegrated commits, version `0.3.0rc5`; record at
  `/opt/devcapsule-gate/rc5-release-protocol.json`.
- Backend run [40147675417](https://github.com/ccozianu/devcapsule/actions/runs/40147675417)
  passed; the [prerelease](https://github.com/ccozianu/devcapsule/releases/tag/v0.3.0-rc5)
  is public, non-draft, with the three assets.
- Downloaded over HTTPS into `/home/devcapsule/.cache/devcapsule-releases/v0.3.0-rc5`:
  the checksum file verifies the executable, SHA-256
  `429aefee8af6434615b92f97c6c3b1f2f6ef55f177a3d58f9127e8b1cad8bfbb`; the
  manifest records the tag, the branch, the source revision and the
  `mainline` disposition; `devcapsule version` from an empty directory
  reports `0.3.0rc5`, build `v0.3.0-rc5`, at `03ed348…`.
- Next: the owner's test of the model's commands on the download, `init
  --require 'java>=21' --with`, `config require|offer|drop|recommend`,
  `config add|omit|restore|use`, `run --with|--use`, the refusals of the
  old spellings, the console's configuration page; then the diagnostics
  snapshot, image cleanup and C20 for the next candidate; the
  documentation language review before the final tag.

How the candidate was prepared:

- The release branch's tip after the owner's merges is `d01fb8c`, PR
  #279. Full gate on it from a separate worktree: mypy clean over 246
  files, 2281 unit tests passed, 36 deselected, 2 xfailed, packaging
  integration 17 passed, the web console session mypy clean over 9 files
  with 326 tests passed; the documentation contract 189 pages, passed.
- Carries, beyond rc4: the capabilities and components work order of the
  direction above, implemented by the Codex and gpt-6-astra pair and
  reviewed by Claude Fable 5.1, one round per slice (PRs #276, #277,
  #279). The resolution matrix is still embedded-27 with the recipe-9
  base; an rc4 lock regenerated by this candidate is byte-identical, and
  an rc4 manifest with the SDK-major table reads with one note.
- The throwaway copy `4PR-6-release-0.3.0`, the release tip plus the
  cherry-pick of `62fa063` keeping `main`'s version files, test-merged
  into `main` cleanly and was PR #280, merged by the owner; the tag
  followed on the release tip, `03ed348`, the record commit.
- Not in rc5: the diagnostics snapshot, image cleanup, C20; the gaps the
  candidate-5 changelog lists under *Not in candidate 5*.

## Release Notes Preparation

Write `notes.md` beside this file before the final tag: plain Markdown for
adopters, what changed for them, compatibility exceptions with remedies,
the tested agent versions and holdbacks from the freshness review, the
deferred items. C20, the last slice of the cycle, makes the notes block and
the manifest promotion need no operator step.
