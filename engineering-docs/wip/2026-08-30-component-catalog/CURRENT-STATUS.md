# Workstream Current Status: Component Catalog

Mnemonic: `component-catalog`

Start date: 2026-08-30

State: paused 2026-10-04 for owner PR integration; .NET SDK and Rider components implemented; SDK build/run and noVNC startup passed; licensed editor interaction remains unverified

Definition read: WORKFLOW.md@a8062953ba89, WORKFLOW-LOCAL.md@963fb34f12db

Branch association: `ws-component-catalog/intellij-idea`

Integration target: `main`

Delivery method: pull request, merge commit; owner operates the GitHub UI

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`, `R-DOCS-002`

## Goal And Scope

Maintain the optional IDE/tool component catalog and shared noVNC smoke harness.
The owner requested autonomous Linux .NET SDK-first, Rider-second delivery on
2026-10-04, continuing the IntelliJ work. This slice does not cut a release.

## Current State

- `dotnet` adds SDK 10.0.401; `dotnet-ide` selects Rider 2026.2.3.1 plus the SDK.
  Vendor archives were verified in full and are pinned by SHA-256. The SDK's
  SHA-512 also matched Microsoft metadata. Stable releases exclude .NET 11 RC.
- The complete SDK installs under `/opt/dotnet`, available on PATH with
  DOTNET_ROOT set and telemetry off. Rider uses independent `rider/*` state
  slots and the shared JetBrains adapter/recovery. No host credentials enter.
- The SDK built and ran a package-free C# fixture as the normal capsule user.
  The Rider noVNC startup smoke passed with the child Playwright component.
- The stronger AI saved-edit test correctly failed at mandatory JetBrains
  activation. No sign-in, trial or purchase was performed. Licensed editing,
  Rider's SDK detection and editor-state persistence are not claimed validated.
- Implementation is committed as `4df3e4f`; validation details and a sanitized
  screenshot are in the linked permanent record. The final delivery gate passed.
- The earlier IntelliJ/Playwright slice has landed: synchronization fast-forwarded
  628c038 to main 5e9cd94. A fresh SSH fetch before delivery found zero commits
  behind main. Mailbox/intake are empty; no open component-catalog bugs.

## Planned Next Step

The owner opens and merges the PR through the GitHub UI, titled **Add .NET SDK and
JetBrains Rider components with noVNC startup smoke**. After the owner reports
merge, fetch and verify remote main contains the finished tree. An activated
Rider session is needed only for additional saved-edit/persistence acceptance.

## Validation And External State

- Full `nox -s build` passed for implementation: 1,138 tests, existing one xfailed
  and one xpassed result, mypy, executable smokes, nine packaging tests and docs
  contract. Final gate also passed with the same counts; logs: `.git/rider-build.log`
  and `.git/rider-final-build.log`.
- `20261004T081323Z-95cbac`: SDK and startup passed; Codex/Astra saved-edit failed
  explicitly at licensing, with `marker_saved: false`.
- `20261004T081836Z-932fc8`: startup/SDK smoke passed, child component browser,
  parent browser deliberately unavailable. Log: `.git/rider-startup-smoke.log`.
- Both owned containers, workspaces and checkout records were verified removed.
  Vendor artifacts and image cache remain reusable. Raw evidence stays under
  `devcapsule-src/dist/e2e-evidence/ide-smoke/`; no desktop tokens are published.
- Scratch under `/opt/xtras/rider-work`; final gate uses `/opt/devcapsule-gate`.
  The website gitlink is unchanged. No release or website publication performed.

## Open Threads

- Awaiting the human: owner PR merge; JetBrains activation if deeper Rider
  editor acceptance is desired. Startup smoke is complete without activation.
- Previous blog editorial release and native video publication remain owner/
  website follow-ups; the website already received the recorded intake item.
- No unresolved implementation choice. Optional .NET workloads and additional
  SDK versions were deliberately excluded; the whole pinned SDK is installed.
- Raw videos/transcripts remain local rather than committed. No verbatim session
  record was requested. Existing `.git/recovery/` files remain untouched.
- Legacy migration/outbox housekeeping and the earlier network-authorization
  mismatch remain with their recorded owners; see the historical handoff.

## Workstream Document Index

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
