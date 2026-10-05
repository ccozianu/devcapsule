# Intake Dispositions: `maintenance`

What became of every item delivered to this workstream. Append-only, newest
last. Never pruned; travels with the workstream into the archive.

On `main`, every item ever delivered here is either still in `intake/`, meaning
undispositioned, or listed below, meaning resolved. Never both, never neither.

| Item | Dispositioned | Outcome | Note |
|---|---|---|---|
| `2026-09-21-workflow-improvements-definition-changed-please-publish.md` | 2026-09-21 | acknowledged | Fast-forwarded to main, read changed definition, took mail; publish at this checkpoint. Retired-outbox verification/deletion accepted after the owner-requested positioning handoff. |
| `2026-09-22-project-management-retire-run-image-print-command.md` | 2026-09-22 | acknowledged | Owner-selected bounded replacement accepted; later tested-patch mail supersedes the implementation request. Applied and validated on maintenance; see current status. |
| `2026-09-22-project-management-run-image-tested-patch.md` | 2026-09-22 | acknowledged | Exact checksum-verified patch applied after main synchronization; full gate passed. Maintenance owns source commit and PR delivery. Receipt commit `6c6f08f` and coordination `93d794a41882` preserve the diff; network defect remains open for legacy PyCharm. |
| `2026-09-22-project-management-drive-0-2-14-release.md` | 2026-09-22 | acknowledged | Accepted release driver; owner subsequently approved cut and progressive bug fixes/deferrals. See release overview. |
| `2026-09-22-project-management-release-working-documents.md` | 2026-09-22 | acknowledged | Accepted maintained release overview and bug table; integrated in PR #131 and now maintained on release-0.2.14. |
| `2026-09-26-project-management-init-discards-answers-bug.md` | 2026-09-26 | acknowledged | Blocking init bug taken as the 0.2.15 headline; fixed on this branch with tests, record carried here with status fixed. |
| `2026-09-26-project-management-release-0215.md` | 2026-09-26 | acknowledged | Maintenance drives 0.2.15 from `main` as `release-0.2.15`; superseded on scope by the fix-only item below. |
| `2026-09-26-project-management-release-0215-fix-only.md` | 2026-09-26 | acknowledged | 0.2.15 carries the init fix alone; cleanup candidates, surfaces and release notes move to 0.2.16. |
| `2026-09-27-project-management-0215-xtras-info-scope.md` | 2026-09-27 | acknowledged | Accepted xtras and host/runtime project info into 0.2.15; general guard repair remains non-gating. Supersedes fix-only scope. |
| `2026-09-27-project-management-0215-antigravity-default.md` | 2026-09-27 | acknowledged | Accepted always-proceed default with preservation of explicit choices and selected-version acceptance. |
| `2026-09-27-project-management-0215-claude-default.md` | 2026-09-27 | acknowledged | Accepted minimal pre-first-launch bypassPermissions settings and interactive first-use acceptance, extending the agent-defaults slice. |
| `2026-10-04-component-catalog-network-run-once-mismatch.md` | 2026-10-05 | acknowledged | Owner ruling: the documented command is supported on every project; its refusal on a project without a network recommendation is a bug, filed as `bugs/devcapsule/2026-10-05-run-once-network-authorization-needs-a-recommendation.md`, target 0.3.0. The local workflow text stands; the sender's `project init --authorize network host` workaround keeps working. |
| `2026-10-04-component-catalog-packaging-metadata-shadow.md` | 2026-10-05 | acknowledged | Owner accepted the bounded test patch: the packaging version check runs from the temp directory, so the editable egg-info in the source tree cannot shadow the embedded wheel. Applied on `ws-maintenance/post-0.2.15`; the three cases pass with the egg-info present. |
| `2026-10-04-component-catalog-packaging-shadow-followup.md` | 2026-10-05 | acknowledged | Confirms the shadow is a test-isolation problem, not a product bug; closed with the patch above. |
| `2026-10-05-component-catalog-conservative-writers-tolerant-readers.md` | 2026-10-05 | acknowledged | The maintenance part is a 0.3.0 requirement, folded into the in-capsule project-command work: read-only validation of the working-tree configuration, commands for every configuration change, and the owner's addition of the same day, `project config resolve --force` and `project run --force-config` with bash as the IDE of last resort. Principle and sequencing stay with project-management, mailed. |
