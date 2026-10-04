# Workstream Current Status: Component Catalog

Mnemonic: `component-catalog`

Start date: 2026-08-30

State: paused 2026-10-04 for owner PR integration; today’s IDE blog updated with .NET/Rider and Eclipse evidence and media

Definition read: WORKFLOW.md@a8062953ba89, WORKFLOW-LOCAL.md@dd1c683d82cd

Branch association: `ws-component-catalog/intellij-idea`

Integration target: `main`

Delivery method: pull request, merge commit; owner operates the GitHub UI

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`, `R-DOCS-002`

## Goal And Scope

Maintain the optional IDE/tool component catalog and shared noVNC smoke harness.
The owner requested Eclipse IDE for Java Developers on 2026-10-04, following
IntelliJ/Rider, with a recorded Playwright smoke. The owner then requested an
update to today’s blog with the latest accomplishments and screenshots/movies.
No release or website publishing.

## Current State

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
  The blog follow-up fast-forwarded to `ff6fde1`, the accepted mainline, before
  editing. Definition unchanged; synchronization is complete. No open owned bugs,
  waiting mail or intake. No workflow declaration/version was changed.

## Planned Next Step

The owner opens and merges the blog follow-up PR through the GitHub UI, titled
**Update today’s IDE blog with Rider and Eclipse results and movies**. Editorial
release and website publication remain separate owner decisions. After merge,
fetch and verify remote main contains this blog update.

## Validation And External State

- Blog render check: draft preserved, four images resolved as site assets and
  three distinct movie links. All pinned evidence links exist at the cited
  mainline commit; original movie SHA-256 values match the acceptance records.
  Both added screenshots were visually reviewed. No new GUI run was needed.
- Blog follow-up full `nox -s build` passed: 1,150 unit tests, nine packaging
  checks, type checks, executable smokes and content contract. Log:
  `.git/ide-blog-build.log`. Only prose, indexes and workflow records changed.

- Full `nox -s build` passed: 1,150 tests, one existing xfail and xpass, mypy,
  CLI and executable smokes, nine packaging checks and docs contract.
  Logs: `.git/eclipse-final-build.log` and `.git/eclipse-delivery-build.log`
  (complete final delivery tree). Isolated packaging repeat: nine passed.
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

- Awaiting the human: blog PR merge, editorial release and existing website
  video-publication follow-up. Eclipse PR #166 is verified on remote main.
- No new assets or website implementation changes; screenshots render through
  the existing content contract and movie links open/download original WebMs.
- No unresolved implementation choice. Java build/debug, Maven/Gradle builds,
  Marketplace installation and restart preference acceptance are not claimed.
- Rider licensed-editor acceptance remains unverified as recorded in its report.
- Raw transcripts stay local. No verbatim session record was requested. Existing
  `.git/recovery/` files and the website gitlink remain untouched.

## Workstream Document Index

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
