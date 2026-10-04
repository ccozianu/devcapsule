# Workstream Current Status: Component Catalog

Mnemonic: `component-catalog`

Start date: 2026-08-30

State: paused 2026-10-04 for owner PR integration; IntelliJ and Playwright components implemented and validated; Codex/Astra IntelliJ initial and relaunch smoke passed; Claude/Fable PyCharm and VSCodium smoke passed

Definition read: WORKFLOW.md@a8062953ba89, WORKFLOW-LOCAL.md@6ff07c49a7ea

Branch association: `ws-component-catalog/intellij-idea`

Integration target: `main`

Delivery method: pull request, merge commit; owner operates the GitHub UI

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`, `R-DOCS-002`

## Goal And Scope

Deliver IntelliJ IDEA as an optional IDE surface and Playwright as an additive
browser-automation component, with a shared, parameterized graphical AI smoke
harness. Codex with `gpt-6-astra` is the default; Claude CLI with
`claude-fable-5-1` is the tested alternative. Action driver and visual
recognizer can be selected independently.

The owner accepted autonomous execution of the
[work order](../../work-orders/2026-10-03-playwright-intellij-agent-smoke.md).
IntelliJ's release target is 0.2.16. This slice does not cut a release.
Antigravity is done per the owner; its historical branch remains intact and
its obsolete delivery tasks are not prerequisites to this slice.

## Current State

- IntelliJ IDEA 2026.2.3 (`java-ide`) uses the shared JetBrains template with
  independent state slots. Its unified distribution's free editor passed the
  smoke without license purchase, trial activation or sign-in.
- Playwright 1.63.0/Chromium 153.0.8010.12 (`browser-automation`) installs
  verified wheels and browser archives offline under `/opt/playwright`.
  The repository's development manifest and generated lock select it.
- One scenario drives screenshots, clicks and keyboard input, checks the
  saved marker independently and requests final visual recognition. Codex
  and Claude implement the same image/decision contract, with finite limits
  and retained evidence. Credentials stay in the parent.
- The component-browser repeat uses Chromium in the fresh child. The parent
  binding was installed from the component's wheels, with its own browser
  path deliberately nonexistent. Both initial and relaunch interactions passed.
- The repeat exposed a real stale-directory-lock failure after `docker stop`.
  IntelliJ now opts into exclusive profile guards and verified dead-socket
  recovery. The test rejects startup-error windows and requires another
  saved editor interaction after relaunch. The
  [bug](../../bugs/devcapsule/2026-10-04-intellij-relaunch-stale-directory-lock.md)
  is closed by the corrected real run, not by its earlier false-positive check.
- The continuation began at `69ced64` and merged main `17532fd` before
  implementation. A fresh SSH fetch on 2026-10-04 found zero commits behind
  main and no unread definition changes. Future synchronization of the
  published branch merges main according to the current policy.
- The website gitlink is unchanged from main. Mailbox and intake are empty
  apart from the intake README. No unresolved implementation task remains
  in the accepted slice; remote-main integration remains with the owner.

## Planned Next Step

The owner opens and merges the PR from `ws-component-catalog/intellij-idea`
into `main` through the GitHub UI. Suggested title:
**Add IntelliJ and Playwright components with reusable AI graphical smoke tests**.
After the owner reports the merge, fetch over SSH and verify that remote main
contains the finished tree before treating integration as complete.
Coordinate the assigned 0.2.16 release through project-management.

## Validation

See the [validation record](../../implementation-notes/devcapsule/2026-10-04-intellij-playwright-validation.md)
for source checksums, commands, limitations and a committed final screenshot.

- Required `nox -s build` passed at runtime source `d6d3566`: syntax, mypy,
  1,117 passing tests, the existing one xfailed and one xpassed result,
  executable smokes, nine packaging tests and the website content contract.
  The final harness path correction at `c5e0535` passed focused checks and
  is exercised in the accepted repeat.
- `20261004T002250Z-01def7`: Claude/Fable VSCodium passed.
- `20261004T002435Z-d44b57`: Codex/Astra IntelliJ passed; the child component
  browser independently launched and rendered HTML.
- `20261004T003322Z-b53949`: Claude/Fable PyCharm passed.
- `20261004T005804Z-c554e8`: corrected Codex/Astra IntelliJ component-browser
  repeat passed, then passed again after container stop/relaunch. Font size
  remained 17, the old marker remained, a new marker was saved and visually
  recognized, and the log confirms stale-socket recovery. Both containers
  and every listed project-record path were confirmed removed.

Evidence: `devcapsule-src/dist/e2e-evidence/ide-smoke/`. Gate scratch:
`/opt/devcapsule-gate`, outside the checkout and fixture-mocked mounts.
Logs: `.git/intellij-recovery-build.log`, `.git/intellij-recovery-smoke.log`.

## Open Threads

- Owner PR integration is pending; no GitHub API or direct-main push is
  authorized. The release driver and cut remain project-management's work.
- Codex JSONL omits a server-reported model id. Evidence records explicit
  `--model gpt-6-astra` selection and the actual CLI version without inventing
  a returned identity. Claude reported the requested Fable model in usage.
- The local host-network instruction is rejected by this CLI's run-once
  authorization grammar. Our test uses supported initialization of its own
  disposable project. The mismatch was delivered to maintenance as
  `2026-10-04-component-catalog-network-run-once-mismatch.md`, coordination
  commit `34cbad056e31`; this slice does not change generic launcher policy.
- The legacy workflow migration/outbox reconciliation remains historical
  housekeeping: no legacy ref was removed. Preserve unlanded records before
  any future removal, as directed by the accepted migration notice.
- Local bootstrap tools remain under `/opt/xtras`; cached vendor artifacts
  and materialized images are retained for reuse. Raw videos, model transcripts
  and failed intermediate runs remain local, with ephemeral desktop tokens in
  raw logs. Permanent records preserve the sanitized conclusions and final
  screenshot. No verbatim session record was requested or created.
- Earlier website recovery files remain under `.git/recovery/`. Their preserved
  contents were not changed or discarded by this slice.

## Workstream Document Index

- [Accepted work order](../../work-orders/2026-10-03-playwright-intellij-agent-smoke.md)
- [Validation and final screenshot](../../implementation-notes/devcapsule/2026-10-04-intellij-playwright-validation.md)
- [Repeatable E2E commands](../../development/e2e-tests.md#ai-driven-graphical-acceptance)
- [Closed IntelliJ relaunch bug](../../bugs/devcapsule/2026-10-04-intellij-relaunch-stale-directory-lock.md)
- [Project-management status](../2026-08-09-project-management/CURRENT-STATUS.md)
- [0.2.16 planning](../2026-08-09-project-management/2026-09-27-0216-release-planning.md)
- [Intake decisions](intake-dispositions.md)
- [Intake](intake/README.md)
- [Historical Antigravity status](2026-10-03-record-antigravity-status.md)
- [Antigravity license analysis](antigravity-cli-license-and-redistribution-analysis.md)
- [Historical release-candidates proposal](release-candidates-proposal.md)
