# Workstream Current Status: Component Catalog

Mnemonic: `component-catalog`

Start date: 2026-08-30

State: active 2026-10-03; implementing the accepted Playwright/IntelliJ work order; shared Codex/Claude driver implemented; full gate and real graphical acceptance in progress

Definition read: WORKFLOW.md@a8062953ba89, WORKFLOW-LOCAL.md@6ff07c49a7ea

Branch association: `ws-component-catalog/intellij-idea`

Integration target: `main`

Delivery method: pull request, merge commit; owner operates the GitHub UI

Requirements: `R-PRODUCT-001`, `R-PRODUCT-002`, `R-SCOPE-001`, `R-DOCKER-001`

## Goal And Scope

Accept and test IDE surfaces and agent CLIs as regular catalog components.
The requested scope is IntelliJ IDEA as an optional IDE surface, Playwright
as a reusable component for future development capsules, and a shared
agent-driven graphical smoke harness using Codex with `gpt-6-astra`.
The [work order](../../work-orders/2026-10-03-playwright-intellij-agent-smoke.md)
records the accepted execution plan and acceptance evidence.

The owner's 2026-10-01 decision, delivered by project-management and confirmed
in this checkout on 2026-10-03, assigns IntelliJ to this workstream for
0.2.16 and lifts the historical Antigravity scope freeze. New IDE components
belong here; component orchestration, upgrades and channels belong to
`component-upgrades`. Eclipse is not scheduled.

## Current State

- Antigravity is completed work per the owner. Its old branch
  `ws-component-catalog/antigravity-cli` remains intact as history; do not
  resume its obsolete delivery tasks or merge its intermediate changes as
  a prerequisite to IntelliJ.
- The continuation branch started at `69ced64` and merged current main
  `17532fd` on 2026-10-03 before implementation, with the
  current workflow definition and local rules. No synchronization was
  needed at this checkpoint. Future synchronization of the published
  branch merges `main` in, following the current integration policy.
- Read the graphical and recursive tests from main at `69ced64`. The current
  IDE smoke has deterministic HTTP/window checks and optional Playwright
  capture; no LLM driver is implemented in the inspected path.
- The owner accepted and extended the work order on 2026-10-03.
  `/opt/xtras` is authorized for the exercise's Playwright bootstrap; the
  deliverable must also supply it as a component in fresh capsules.
- Implemented IntelliJ 2026.2.3 unified distribution (`java-ide`) using the
  shared JetBrains template, plus Playwright 1.63.0/Chromium 153.0.8010.12
  (`browser-automation`) through verified offline wheels/browser archives.
  Dogfood manifest and generated locks select Playwright.
- Added one shared visual action/recognition scenario with Codex/GPT-6 Astra
  default and Claude/`claude-fable-5-1` alternative. Both exact model CLI
  text and image probes succeeded. Real IDE acceptance remains pending.
- Full unit suite passes after adding discovery adapters and status-service
  probe registrations; required gate has reached executable packaging.
  Scratch is `/opt/devcapsule-gate`, outside the repo and mocked home mounts.
  Local log: `.git/intellij-build-gate.log`.
- No open bug records owned by `component-catalog` were found on this
  mainline baseline. Re-read the queue at the next session.
- The website gitlink remains exactly the one on `main`; the owner reserves
  pointer updates to the docs workstream.

## Planned Next Step

Execute the accepted [work order](../../work-orders/2026-10-03-playwright-intellij-agent-smoke.md):
Playwright and IntelliJ components, one shared graphical scenario with
parameterized AI action driver and visual success recognizer. Codex with
`gpt-6-astra` is the default and required IntelliJ acceptance; provide the
Claude CLI/Fable 5.1 alternative on a best-effort basis. Finish the gate, commit an identified source checkpoint, then perform the
real successor browser/IntelliJ acceptance and regression/lifecycle checks.

## Open Threads

- The owner granted autonomous execution and requested the Claude/Fable 5.1
  alternative on 2026-10-03. Reload the current workflow and project-management
  records when resuming. Both model identifiers and screenshot input worked in local probes.
  IntelliJ acquisition is in progress; its vendor checksum is pinned.
  Do not silently change `gpt-6-astra`.
- 0.2.16 is the assigned target; release driver, cut and formal work order
  remain project-management responsibilities. Re-verify their latest state.
- The workflow migration notice is accepted. Publish status and use
  coordination mail. Before removing any legacy outbox refs, establish
  whether they hold unlanded records and preserve those records; no legacy
  ref is removed by this checkpoint.
- Bootstrap Playwright and browsers are under `/opt/xtras`; they are not
  the managed component. Model probe evidence is under
  `/opt/devcapsule-gate/visual-probes`. No IntelliJ launch yet at this checkpoint.
  The earlier website recovery files remain in `.git/recovery/`.
- Historical status is preserved verbatim in the record below. Its old next
  steps and external-state claims are historical, not current instructions.

## Validation

Work-order checkpoint (2026-10-03): work order/status links and
`git diff --check` pass. No runtime or test source changed. The required gate
was attempted again with a short scratch path outside the checkout and the
fixture's mocked home mount. `/var/tmp` is a 1 GB tmpfs here; pytest filled it,
so the run was terminated and its owned `/var/tmp/cc-order-tests` directory
removed. Version, syntax and mypy checks had passed; no full gate pass is
claimed. Log: `.git/component-catalog-work-order-build.log`. Before the next
gate, choose scratch outside the source tree and the fixture's mocked mounts,
with sufficient disk space and a short path for Unix sockets. Do not repeat
these unsuitable locations.

Previous status checkpoint:

Status and routing update only. `git diff --check` and the new status links
pass; the historical record is byte-identical to the previous status.
The required `nox -s build` was attempted on unchanged runtime source:
version, syntax and mypy checks passed; pytest reported 1,088 passed,
one failed, 22 deselected, one xfailed and one xpassed. The failure is
`test_host_daemon.py::test_unmountable_staging_fails_loudly`: the expected
`PycharmRunError` was not raised with scratch under
`/home/devcapsule/cc-status-tests`. Later gate stages did not run.
Revisit the test scratch setup before implementation validation; no runtime
fix or full gate pass is claimed. Local log:
`.git/component-catalog-status-build-short-path.log`. An earlier attempt
used an overly long scratch path inside the project; that setup produced
socket-path and project-discovery failures and is not the retained result.

## Workstream Document Index

- [Playwright, IntelliJ and agent-smoke work order](../../work-orders/2026-10-03-playwright-intellij-agent-smoke.md):
  primary execution scope, acceptance ladder and autonomy boundaries.
- [Project-management status](../2026-08-09-project-management/CURRENT-STATUS.md):
  read *Owner Decisions Of 2026-10-01* for surface ownership and IntelliJ scope.
- [0.2.16 planning](../2026-08-09-project-management/2026-09-27-0216-release-planning.md):
  read C12 and its owner-decision addendum for the release target.
- [Intake decisions](intake-dispositions.md): accepted handoffs and their disposition.
- [Intake](intake/README.md): any received, undecided work.
- [Historical Antigravity status](2026-10-03-record-antigravity-status.md):
  prior implementation and acceptance history; consult only for historical evidence.
- [Antigravity license analysis](antigravity-cli-license-and-redistribution-analysis.md):
  historical agent-component licensing evidence, not IntelliJ licensing evidence.
- [Release-candidates proposal](release-candidates-proposal.md): historical proposal;
  current release policy is in WORKFLOW-LOCAL.md and the release runbook.
