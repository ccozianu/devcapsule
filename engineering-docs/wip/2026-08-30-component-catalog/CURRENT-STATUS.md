# Workstream Current Status: Component Catalog

Mnemonic: `component-catalog`

Start date: 2026-08-30

State: paused 2026-10-06 for owner PR integration; configuration contract implemented and validated

Definition read: WORKFLOW.md@a8062953ba89, WORKFLOW-LOCAL.md@9bc049624f48

Branch association: `ws-component-catalog/intellij-idea`

Integration target: `main`

Delivery method: pull request, merge commit; owner operates the GitHub UI

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`, `R-DOCS-002`

## Goal And Scope

Maintain the optional IDE/tool component catalog and shared noVNC smoke harness.
The owner requested Eclipse IDE for Java Developers on 2026-10-04, following
IntelliJ/Rider, with a recorded Playwright smoke. The owner then requested an
update to today’s blog with the latest accomplishments and screenshots/movies.
The owner then reported `project run` rejecting Playwright and requested a
local workflow rule to prevent this. The 2026-10-05 correction establishes
command-only configuration writes, validation by the running `devcapsule0`,
a managed self-hosting exception and mandatory/optional capability handling
for all adopters. Implement the accepted configuration contract at the owner’s explicit request on
2026-10-06: shared required/optional capabilities, SDK-major constraints, local
IDE/agent selection, conservative CLI writers and tolerant readers. No task or
workstream-specific capability profiles. New/changed code coverage must exceed
90%, aiming for complete coverage; document the system ab initio in docs/.
No release or website publishing.

## Current State

- Owner-assigned configuration implementation is complete in this branch:
  project required/optional capabilities, explicit Python/.NET SDK-major checks,
  developer-local IDE/agent/tool pins and optional omissions; no task/workstream
  profiles. New project creation uses `init --required`; changes use
  `config capabilities`, with preview and interrupted-edit recovery. `config check`
  validates candidate/shared documents and artifact metadata without writes.
- Readers preserve shared bytes while omitting unsupported optional capabilities.
  Optional-only contributions reconcile at launch when the mandatory baseline and
  local answers are unchanged. Optional download failures can reduce one run;
  mandatory dependencies and integrity failures cannot be waived. A reduced run
  does not certify the full stored environment as known-good.
- Local version pins for retained tools and all host decisions survive local
  reselection. Following shared versions retains personal capabilities. SDK
  constraints are checked again on local version-set selection and base overrides.
- The ab-initio [capability guide](../../../docs/configuration/capabilities.md)
  explains ownership, commands, validation, recovery and reader rollout. Legacy
  `need` inputs/commands remain available; shared IDE/agent declarations must be
  deliberately migrated. Fresh policy creation has no implicit IDE or agent.
- No reply arrived to the optional IDE-default question: used the proposed
  developer-choice behavior. Missing IDE selection gives an actionable command.
- Merged origin/main at `1eb8e76` via `710fd04` before implementation. The owner
  explicitly assigned this slice here, superseding the earlier maintenance
  handoff; maintenance/project-management were notified by coordination mail.
  No new intake items; the one previously fixed owned bug still awaits host acceptance.
- Existing self-hosting manifest/lock and running `devcapsule0` are unchanged.
  Current baseline identifies 0.2.16.dev0-local-linux-x86_64, source unknown.
  The new source CLI accepts the existing shared contract via read-only check;
  this is offline validation, not a new container launch. Adopting the new
  representation on this host still needs the baseline/candidate transition
  and independent restart path in R-CONFIG-001. No release/version bump.

### Earlier checkpoints

- Owner correction is canonical in accepted [R-CONFIG-001](../../requirements/product/r-config-001-conservative-writers-tolerant-readers.md)
  and the rewritten local rule. Conservative writers, tolerant readers,
  mandatory/optional needs and graceful local degradation are product direction;
  exact schema/commands remain implementation work. The previous blanket
  released-vocabulary rule is superseded; current guards are interim protection
  for today's required-only configuration.
- Sent `2026-10-05-component-catalog-conservative-writers-tolerant-readers.md`
  to project-management and maintenance, correcting the prior planning handoff
  and identifying missing command-based mutations/candidate validation. No
  configuration, launcher or runtime was changed in this follow-up.
- At the 2026-10-05 checkpoint main was `242e13e`, zero commits behind and no definition change on entry;
  no synchronization needed. One owned bug remains fixed pending host acceptance.

- Owner follow-up: recovered the host launch using an already-built executable
  in the shared `dist` folder, then directed the lessons toward a 0.3 release.
  Exact executable identity remains unknown. This recovery does not validate
  the separate released-launcher rollback path or constitute a blanket decision
  to require development builds for every checkout.
- Sent `2026-10-04-component-catalog-0-3-launcher-bootstrap-lessons.md` to
  `project-management` by coordination mail: owner’s 0.3 direction, evidence,
  and agent-proposed compatibility, safe-transition, independent recovery and
  cold-restart acceptance requirements. Detailed scope, owners, timing and the
  relationship to 0.2.16 are pending release planning. No version was bumped.
- The prior 0.3 direction follow-up changed records only; its content check passed.

- New owned bug: [unreleased Playwright breaks checkout launch](../../bugs/devcapsule/2026-10-04-unreleased-playwright-breaks-checkout-launch.md).
  The original component commit also changed the shared need and lock, making
  the checkout depend on a launcher that has not shipped in a final release.
- Restored `.devcapsule/devcapsule.toml` and the platform lock byte-for-byte
  from `ada153c^`; other pins and the Playwright component/tests are unchanged.
  No generated lock fields were hand-patched, and no host launcher was replaced.
- Added the local shared-checkout compatibility rule and two regression guards
  against final v0.2.15's frozen capability/component vocabulary. The owner
  has since clarified that self-hosting with a development build is an allowed,
  managed exception and optional capabilities need tolerant consumption.
- Entry synchronization fast-forwarded to accepted main `242e13e`; the blog
  update is integrated in PR #167. Definition unchanged; no waiting mail or
  intake and no previously open owned bugs. The new bug is owned here because
  it was introduced by this workstream’s catalog/bootstrap change.

- Today’s existing blog is now **An AI takes our IDEs for a test drive**, with
  the .NET CLI build, Rider’s activation limit, Eclipse’s WebKitGTK fix and
  accepted save. Four screenshots and three original movies are linked.
  Existing media is reused without duplication or alteration; movie/report
  links use verified mainline `ff6fde1`. Filename/URL and draft flag are retained.

- `eclipse-ide` selects Eclipse Java Developers 2026-09 R; `java-ide` remains
  IntelliJ. The whole package and native WebKitGTK dependencies are pinned and
  verified; native packages install offline with build networking disabled.
- Runtime uses the ordinary capsule user, a read-only install, persistent home
  configuration and the separate `eclipse/workspace` state slot. The component
  discovery adapter reads stable Java package availability, without auto-upgrades.
- Accepted smoke `20261004T090121Z-ea0a5b` saved a marker through noVNC/Playwright,
  independently checked it on disk and visually recognized the editor. Original
  movie and final screenshot are committed with the permanent record below.
- Implementation: `370abad`, native-library/harness correction `f926036`.
  The accepted executable identifies `f926036` and matches the child checksum.
- Eclipse is integrated through PR #166; remote main contains `d79b967`.
  The blog follow-up was based on `ff6fde1`; this repair starts at `242e13e`.
  No workflow declaration/version was changed.

## Planned Next Step

Owner opens/updates the branch PR in GitHub, titled **Separate project capability
requirements from personal tools**. Merge by the configured merge-commit workflow;
then fetch and verify the integrated tree. This implementation has not reached
remote main yet. Release/adoption sequencing belongs to project-management.
Do not migrate the working self-hosting configuration through direct edits or
replace the host launcher as an incidental follow-up.

## Validation And External State

- Final full `nox -s build` passed: **1,245 unit tests**, ten packaged-executable
  integration tests, mypy, syntax/version checks, source/PEX smokes and documentation
  contract. Log: `.git/config-policy-build.log`. One pre-existing xfail and one
  pre-existing non-strict xpass remain; no skipped gate or new container launch.
- New policy suite: **87 tests**, covering ownership, malformed/unknown inputs,
  SDK mismatches, mandatory dependency closure, optional-only launch reconciliation,
  download versus integrity failures, no-write preview/check, preservation of
  opaque optional pins, local version pins and consent, crash endpoints and
  conflicting edits. The packaged PEX also authors and validates an isolated
  project and rejects an incompatible SDK major without changing shared bytes.
- Changed production-code coverage against merge `710fd04`: **574/574 executable
  lines (100%)**, **199/204 branches (97.55%)**. Measured from the full unit suite,
  Coverage.py JSON and zero-context Git diff; `.git/measure-config-coverage.py`,
  `.git/config-policy-coverage.json`, `.git/config-policy-diff-coverage.json` retain
  the local calculation. Tests establish these finite cases and invariants;
  coverage is not a proof that every possible environment is defect-free.
- Pure configuration dependency checks were extended for the new modules and
  pass. The initial architecture violation and legacy base-override regression
  were fixed; no existing checks were weakened. The documentation frontmatter
  was corrected to conform to the existing content contract.
- Local artifact: `devcapsule-src/dist/devcapsule-local.pex`, built and exercised.
  The dirty-tree gate intentionally leaves public `dist/devcapsule.pex` alone.


- Revised-rule/requirement full gate passed: 1,152 tests, nine packaging checks,
  type checks, source/PEX smokes and content contract. Log:
  `.git/config-contract-build-20261005.log`. Only rules, requirements, indexes
  and records changed; the project manifest and platform lock are unchanged.

- `devcapsule0 project config list` exit 0: recorded launcher inspection only,
  not launch/candidate validation. CLI identity: `/usr/local/bin/devcapsule0`,
  0.2.16.dev0 local-linux-x86_64, source unknown. `need` adds capabilities;
  `resolve` writes and requires launcher context. Help exposes no removal,
  classification or read-only candidate-validation command. Local log:
  `.git/devcapsule0-config-preflight-20261005.log` (not published).

- Repair full `nox -s build` passed: 1,152 unit tests, nine packaging checks,
  mypy, CLI/PEX smokes and content contract. Log: `.git/launcher-compat-build.log`.
  This resumed environment lacked the documented scratch parent; `/var/tmp`
  also proved too small. Recreated `/opt/devcapsule-gate` on the large overlay,
  removed only this attempt’s alternate scratch, and passed without code fixes.

- New capability/lock guards failed before repair, then all 43 focused
  compatibility/resolution tests passed. Isolated v0.2.15 tagged source
  reproduced the exact error and accepted the restored pair through runtime
  planning. Log: `.git/launcher-compat-tagged-source.log`. This did not execute
  the published release binary or launch a container.

- Blog render check: draft preserved, four images resolved as site assets and
  three distinct movie links. All pinned evidence links exist at the cited
  mainline commit; original movie SHA-256 values match the acceptance records.
  Both added screenshots were visually reviewed. No new GUI run was needed.
- Previous blog follow-up full gate passed; `.git/ide-blog-build.log`.

- Previous Eclipse full gate passed: 1,150 tests and nine packaging checks.
  Logs and original acceptance details remain in the permanent validation record.
- The saved-edit smoke used the child's Playwright component with a deliberately
  unavailable parent browser path. Both model driver and recognizer used the
  existing Codex/GPT-6 Astra harness. Log: `.git/eclipse-accepted-smoke.log`.
- Owned test containers, workspaces and checkout records are removed. Acquired
  artifacts and materialized images remain reusable caches. Scratch and the
  exact accepted executable remain under `/opt/xtras/eclipse-work`.
- Raw evidence stays in `devcapsule-src/dist/e2e-evidence/ide-smoke/`; desktop
  access tokens are not published. The movie is retained as original WebM.
- Two packaging checks transiently read local editable metadata instead of the
  release executable's wheel; maintenance received reproduction, proposed fix
  and the successful final-gate follow-up by mail. No unrelated fix was committed.

## Open Threads

- Awaiting owner PR integration and release sequencing. The implemented contract
  requires a reader containing it; binaries already shipped cannot learn it
  from configuration. Host rollout and a real next-session launch are not claimed.
- SDK-major knowledge is explicit catalog data (currently Python and .NET).
  Extra providers are not installed by naming an arbitrary model/vendor.
- No additional product decision is needed to review this implementation. The
  IDE-default question was optional; no implicit default was selected.

- Awaiting the human: compatibility-repair PR merge, host launcher identity
  and confirmation of `project run`. Blog editorial release and existing website
  video-publication follow-up remain; Eclipse #166 and blog #167 are on main.
- No new assets or website implementation changes; screenshots render through
  the existing content contract and movie links open/download original WebMs.
- Earlier IDE validation limits: Java build/debug, Maven/Gradle builds,
  Marketplace installation and restart preference acceptance are not claimed.
- Rider licensed-editor acceptance remains unverified as recorded in its report.
- Raw transcripts stay local. No verbatim session record was requested. Existing
  `.git/recovery/` files and the website gitlink remain untouched.

## Workstream Document Index

- [Capability system guide](../../../docs/configuration/capabilities.md) — ab-initio user documentation

- [Conservative writers and tolerant readers](../../requirements/product/r-config-001-conservative-writers-tolerant-readers.md) — accepted 0.3 direction

- [Shared-checkout Playwright regression and recovery](../../bugs/devcapsule/2026-10-04-unreleased-playwright-breaks-checkout-launch.md) — current slice

- [Eclipse package, native libraries, movie and validation](../../implementation-notes/devcapsule/2026-10-04-eclipse-validation.md) — current slice acceptance

- [SDK/Rider provenance, commands, evidence and limitations](../../implementation-notes/devcapsule/2026-10-04-dotnet-rider-validation.md) — acceptance and resumption
- [Repeatable E2E commands](../../development/e2e-tests.md#rider-and-net-sdk-smoke) — run the smoke
- [IntelliJ completion snapshot](2026-10-04-record-intellij-completion.md) — previous slice history and retained follow-ups
- [IntelliJ/Playwright validation](../../implementation-notes/devcapsule/2026-10-04-intellij-playwright-validation.md) — earlier accepted GUI runs
- [Accepted IntelliJ work order](../../work-orders/2026-10-03-playwright-intellij-agent-smoke.md) — original scope
- [Blog draft and movies](../../blog/2026-10-04-an-ai-takes-intellij-for-a-test-drive.md) — owner editorial review
- [Intake decisions](intake-dispositions.md) and [intake](intake/README.md) — coordination
- [Historical Antigravity status](2026-10-03-record-antigravity-status.md) — earlier delivery history
- [Antigravity license analysis](antigravity-cli-license-and-redistribution-analysis.md) — licensing reference
- [Historical release-candidates proposal](release-candidates-proposal.md) — retrospection
