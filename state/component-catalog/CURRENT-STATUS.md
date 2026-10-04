# Workstream Current Status: Component Catalog

Mnemonic: `component-catalog`

Start date: 2026-08-30

State: active 2026-10-04; adding Eclipse IDE for Java Developers and recorded noVNC/Playwright acceptance

Definition read: WORKFLOW.md@a8062953ba89, WORKFLOW-LOCAL.md@963fb34f12db

Branch association: `ws-component-catalog/intellij-idea`

Integration target: `main`

Delivery method: pull request, merge commit; owner operates the GitHub UI

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`, `R-DOCS-002`

## Goal And Scope

Maintain the optional IDE/tool component catalog and shared noVNC smoke harness.
The owner requested Eclipse IDE for Java Developers on 2026-10-04, following
the IntelliJ/Rider integrations, with noVNC/Playwright smoke and a retained movie.
Select it via `eclipse-ide`; preserve `java-ide` as IntelliJ. This slice does not cut a release.

## Current State

- Eclipse Java Developers 2026-09 R is pinned with SHA-256 and vendor-verified
  SHA-512. Component, materialization, update discovery, runtime adapter and
  isolated persistent workspace are implemented, with `eclipse-ide` selection.
- The existing noVNC/Playwright/AI harness includes Eclipse and verifies the
  installed Java package/JDT. Real graphical acceptance and movie retention
  are next; the matrix evidence remains explicitly provisional.
- Previous SDK/Rider delivery is on main through PR #165. Its validation and
  licensed-editor limitation remain in the permanent report below.

## Planned Next Step

Implement the pinned Eclipse Java package, its runtime/state contract and shared
smoke surface; validate a real noVNC saved edit and retain the movie. Run the
full build gate, commit/push, and hand the owner a concrete PR for UI integration.

Session entry: fetched main `a3d88e3`; PR #165 contains Rider. Fast-forwarded
before the new slice. No workflow/local changes, no open owned bugs, no mail or
intake. Root workflow version mismatch is the documented source-file exception;
no definition refresh or declaration change was made.

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
