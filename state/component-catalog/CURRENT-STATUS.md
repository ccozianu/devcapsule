# Workstream Current Status: Component Catalog

Mnemonic: `component-catalog`

Start date: 2026-08-30

State: paused 2026-10-04 for owner PR integration; Eclipse Java Developers component and recorded noVNC saved-edit smoke passed

Definition read: WORKFLOW.md@a8062953ba89, WORKFLOW-LOCAL.md@dd1c683d82cd

Branch association: `ws-component-catalog/intellij-idea`

Integration target: `main`

Delivery method: pull request, merge commit; owner operates the GitHub UI

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`, `R-DOCS-002`

## Goal And Scope

Maintain the optional IDE/tool component catalog and shared noVNC smoke harness.
The owner requested Eclipse IDE for Java Developers on 2026-10-04, following
IntelliJ/Rider, with a recorded Playwright smoke. No release or website publishing.

## Current State

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
- Entry synchronization fast-forwarded to main `a3d88e3`, which includes Rider
  through PR #165. Latest fetch: zero commits behind main. No open owned bugs,
  waiting mail or intake. No workflow declaration/version was changed.

## Planned Next Step

The owner opens and merges the PR through the GitHub UI, titled **Add Eclipse
IDE for Java Developers with recorded noVNC smoke**. After the owner reports
merge, fetch and verify remote main contains the finished tree.

## Validation And External State

- Full `nox -s build` passed: 1,150 tests, one existing xfail and xpass, mypy,
  CLI and executable smokes, nine packaging checks and docs contract.
  Log: `.git/eclipse-final-build.log`. Isolated packaging repeat: nine passed.
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

- Awaiting the human: owner PR merge. Previous IntelliJ blog editorial release
  and website video publication remain the existing owner/website follow-ups.
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
