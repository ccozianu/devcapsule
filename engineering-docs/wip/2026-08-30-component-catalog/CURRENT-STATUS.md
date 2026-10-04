# Workstream Current Status: Component Catalog

Mnemonic: `component-catalog`

Start date: 2026-08-30

State: paused 2026-10-04 for owner PR integration and host launch verification; shared-checkout compatibility restored, local rule and regression guards added

Definition read: WORKFLOW.md@a8062953ba89, WORKFLOW-LOCAL.md@d008030481fe

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
local workflow rule to prevent this. Restore released-launcher compatibility
for the shared checkout; keep unreleased component tests in disposable projects.
No release or website publishing.

## Current State

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
- This follow-up changes records only; main is current, the prior full gate
  remains the source/configuration validation, and the content check was rerun.

- New owned bug: [unreleased Playwright breaks checkout launch](../../bugs/devcapsule/2026-10-04-unreleased-playwright-breaks-checkout-launch.md).
  The original component commit also changed the shared need and lock, making
  the checkout depend on a launcher that has not shipped in a final release.
- Restored `.devcapsule/devcapsule.toml` and the platform lock byte-for-byte
  from `ada153c^`; other pins and the Playwright component/tests are unchanged.
  No generated lock fields were hand-patched, and no host launcher was replaced.
- Added the local shared-checkout compatibility rule and two regression guards
  against final v0.2.15's frozen capability/component vocabulary. The default
  follows the existing released-client manifest policy; the optional owner
  question about deliberately requiring a development build remains unanswered.
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

The owner opens and merges the PR through the GitHub UI: **Keep the shared
checkout launchable with released DevCapsule**. After pulling the repaired pair,
confirm the host launcher path/version and `project run`; close the bug only
after that confirmation. Fetch and verify main after the owner reports merge.

## Validation And External State

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

- Project management must disposition the 0.3 planning handoff. A stronger
  product guarantee is needed beyond the current local compatibility rule;
  consent/recovery design must align with component-upgrades. The proposed
  acceptance criteria are recommendations, not an approved full release scope.

- Awaiting the human: compatibility-repair PR merge, host launcher identity
  and confirmation of `project run`. Blog editorial release and existing website
  video-publication follow-up remain; Eclipse #166 and blog #167 are on main.
- No new assets or website implementation changes; screenshots render through
  the existing content contract and movie links open/download original WebMs.
- No unresolved implementation choice. Java build/debug, Maven/Gradle builds,
  Marketplace installation and restart preference acceptance are not claimed.
- Rider licensed-editor acceptance remains unverified as recorded in its report.
- Raw transcripts stay local. No verbatim session record was requested. Existing
  `.git/recovery/` files and the website gitlink remain untouched.

## Workstream Document Index

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
