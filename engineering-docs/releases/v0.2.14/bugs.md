# 0.2.14 — Bug Triage

[Release overview](README.md)

Initial review: 2026-09-22 at `8e7cc21`, against RC0 source `d078b87` and
main `e50b9f1`. Follow-up: legacy PyCharm launch removed after RC0; validation
and integration state are recorded in the release overview.
27 tracked records: 21 open, three closed and three retired. Two records from
the owner's rc3 test on 2026-09-24 await disposition: the newly required
acquisition decision (R-COMPAT-001) and the misleading `config list` trailer. The 2026-09-24
released-launcher manifest rejection is **blocking**, fixed on the release
branch, and needs RC2. The installed-IDE
reuse report has no release target and awaits owner design review. The two new
2026-09-24 findings are a **blocking** missing runtime command owned by
maintenance and a URL-opening defect owned by contained-display, both targeted
at 0.2.14. The original 19 rows retain their recorded fields and dispositions.

**Owner decision, 2026-09-24: release blocked; pause the smoke campaign to
address the missing `devcapsule` command inside the website capsule.** This
supersedes the earlier assessment that no known bug blocked publication.
Automatic workflow installation is a separate non-blocking onboarding work item.

## How We Use This List

The linked bug records own general status, severity, target, ownership and
technical evidence. This table mirrors those fields for review and records
this release's disposition and next action. Update the relevant bug record
and this row together when a triage decision is implemented; follow ownership
routing for another workstream's work. Reconcile rows when another owner lands
a change, and before each candidate. Record the reconciliation revision above.

Replace **Undecided** with the agreed release disposition and rationale, such
as fix for 0.2.14, validate for 0.2.14, defer, already resolved, or retire.
A proposal in the last column is not an accepted decision. Keep resolved rows
here so release history survives; record revisions and evidence links rather
than copying the technical narrative. `fixed` does not mean closed or released.

## Working List

| Bug | Owner | Recorded status | Recorded severity | 0.2.14 disposition | Next action / evidence |
|---|---|---|---|---|---|
| [Client upgrade requires an acquisition decision](../../bugs/devcapsule/2026-09-24-client-upgrade-requires-acquisition-decision.md) | maintenance | confirmed | untriaged | **Undecided: name the R-COMPAT-001 exception in the notes (recommended), or grandfather pre-0.2.14 records** | Corrected root cause: 0.2.12 enforced acquisition consent only for Claude Code and materialized antigravity without any recorded approval (verified in the running capsule and the host records); 0.2.14 requires every acquisition since 6709756/85bec27. Existing 0.2.12 checkouts now owe the decision once. |
| [`config list` advises resolve on a fresh resolution](../../bugs/devcapsule/2026-09-24-config-list-advises-resolve-on-fresh-resolution.md) | maintenance | confirmed | minor | Fix for 0.2.14 proposed | Root cause: `ConfigurationReview.render()` appends the resolve instruction unconditionally; `run` checks freshness separately and is correct. |
| [Release workflow gated on Docker on a hosted runner](../../bugs/devcapsule/2026-09-24-release-workflow-gated-on-docker-on-hosted-runner.md) | maintenance | fixed | blocking | **Fixed on branch; RC2 has no assets, RC3 needed** | rc2 backend run failed at a Docker build the rc1 run had passed with identical code; local reproduction passes. Owner ruling: no Docker on hosted runners. Workflow stripped of Docker steps; proofs move to local acceptance; e2e helpers now report command output. |
| [Released launchers reject the repository manifest](../../bugs/devcapsule/2026-09-24-released-launchers-reject-repository-manifest.md) | maintenance | fixed | blocking | **Release blocker — fix on branch, needs RC2** | Root cause: 658749f declared runtime-effect devcapsule.command-name in the repository manifest; v0.2.12 and rc0 reject unknown effects, so every released client failed on main and release-0.2.14. Fixed by the reserved value name, a version-naming diagnostic, and a guard test; published 0.2.12 now lists and resolves the manifest. Full gate passed. Owner PR to main, then tag RC2. |
| [Runtime CLI missing from PATH](../../bugs/devcapsule/2026-09-24-runtime-cli-not-on-path.md) | maintenance | closed | blocking | **Closed: owner verified devcapsule0 on the PATH in a real rc3 capsule, 2026-09-24** | Public command installed; this repository recommends devcapsule0 for development. Four Docker command-mode/surface variants passed. Owner accepted the real PyCharm/devcapsule0 session at 9cc0868. Integrated through PR #136; RC1 public at cec7a0c; downloaded identity verified, exact-candidate IDE validation pending. |
| [In-capsule configuration inspection](../../bugs/devcapsule/2026-09-24-runtime-configuration-inspection-fails.md) | component-upgrades | confirmed | untriaged | **Narrowed on rc3: only the /opt discovery fallback affects ordinary launches; fix proposed for 0.2.14 under maintenance** | Recursive launch omits read-only configuration mounts; /opt discovery lacks capsule-project fallback. Both config list failures reproduced with exact RC1 image. |
| [Installed IDE Docker reuse](../../bugs/devcapsule/2026-09-24-installed-ide-docker-reuse.md) | maintenance | confirmed | minor | No release target — design review first | No implementation authorized; review cache identity, reuse, retention and scope with the owner. |
| [URL opening has no browser handler](../../bugs/devcapsule/2026-09-24-url-opening-without-browser-handler.md) | contained-display | confirmed | untriaged | Triage for 0.2.14 | Host networking active; no local browser or authorized host-browser bridge. Decide supported no-bridge UX; preserve host-access choices. |
| [Codium runtime-option parity](../../bugs/devcapsule/2026-07-13-codium-run-option-parity.md) | maintenance | retired | untriaged | Retired — removed implementation | Local RC0 rejects the old command; candidate tree lacks its launcher/assets. See linked retirement evidence. |
| [Codium ambient passwordless sudo](../../bugs/devcapsule/2026-07-16-codium-ambient-sudo-default.md) | maintenance | retired | untriaged | Retired — removed implementation | Local RC0 rejects the old command; candidate tree lacks its launcher/assets. See linked retirement evidence. |
| [Multiline Dockerfile quoting](../../bugs/devcapsule/2026-07-16-pycharm-build-multiline-exec-rendering.md) | maintenance | confirmed | untriaged | Deferred — unless it recurs during the release E2E campaign | Owner decision 2026-09-22. Current recipes build; generic rendering defect remains. After this release, redesign component image composition around documented, unit-testable contracts; see bug for evidence and scope. |
| [Legacy PyCharm host networking](../../bugs/devcapsule/2026-07-23-pycharm-ambient-host-network.md) | maintenance | retired | untriaged | Retired — launch command removed | Legacy adapter/helpers removed; rejected invocations cannot launch or prepare state. Shared project launch remains. [V1 capability decisions](../../work-orders/2026-09-22-legacy-launch-capability-disposition.md) stay open. Integration and next candidate pending; RC0 still contains the command. |
| [Codex ACP missing CODEX_HOME](../../bugs/devcapsule/2026-08-03-codex-acp-missing-home.md) | maintenance | fixed | untriaged | Undecided | **Propose verify:** fresh component state, one actual PyCharm ACP exchange, then relaunch. CLI use alone does not exercise ACP. |
| [Component tooling missing from PATH](../../bugs/devcapsule/2026-08-03-component-tooling-runtime-path.md) | maintenance | confirmed | untriaged | Undecided | **Propose verify, likely resolved:** base PATH export and generic environment inheritance exist. Check node/npm/npx by name in the IDE terminal and a child build process. |
| [Manual ecosystem setup for fresh clones](../../bugs/devcapsule/2026-08-03-ecosystem-aware-project-bootstrap.md) | maintenance | confirmed | untriaged | Undecided | **Propose defer:** multi-ecosystem bootstrap needs product/consent/lifecycle design. Keep setup instructions usable; reopen release scope if the documented onboarding cannot reach useful work. |
| [JetBrains X11 alpha-compositing warning](../../bugs/devcapsule/2026-08-03-jbr-slow-x11-alpha-compositing.md) | maintenance | reported | minor | Undecided | **Propose defer:** warning has no recorded functional impact. Observe the normal GUI journey; investigate visible corruption or material latency, not the warning alone. |
| [JetBrains embedded-browser preview](../../bugs/devcapsule/2026-08-03-jcef-sandbox-container-preview.md) | maintenance | fixed | untriaged | Undecided | **Propose verify:** Markdown/SVG preview with fresh IDE settings, no AppArmor remedy prompt, existing disclosure and outer isolation retained. |
| [PyCharm native-launcher warning](../../bugs/devcapsule/2026-08-03-jetbrains-native-launcher.md) | maintenance | reported | minor | Undecided | **Propose defer:** changing launcher affects signals, restart and lifecycle; no functional failure reported. Investigate if normal close/restart fails. |
| [Exited containers not cleaned up](../../bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md) | maintenance | reported | untriaged | Undecided | **Propose defer:** retained recursive successors need an owned cleanup policy; ordinary foreground runs already use --rm. Preserve diagnostic evidence; record retained objects during acceptance. |
| [X11 host-session credential exposure](../../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md) | contained-display | fixed | untriaged | Undecided | **Propose verify scope:** confirm contained project launch shares no host X socket/cookie and explicit passthrough is disclosed. Legacy bypass removed; old-base fallback in project launch remains. Avoid blanket closure. |
| [Base-image consent versus selection](../../bugs/devcapsule/2026-09-02-authorize-base-image-conflates-consent-with-selection.md) | maintenance | fixed | untriaged | Undecided | **Propose verify, likely resolved:** exercise current local-reference selection and consent UX; reconcile superseded yes/no instructions before closure. |
| [Formation entrypoint and image lifecycle](../../bugs/devcapsule/2026-09-02-formation-identity-claims-an-entrypoint-the-recipe-never-sets.md) | component-catalog | confirmed | untriaged | Undecided | **Propose verify/split:** inspect actual image boot configuration against descriptor, then repeat launch for reuse. Defer remaining superseded-image cleanup separately; do not close the combined record wholesale. |
| [Incomplete Codex installation](../../bugs/devcapsule/2026-09-05-codex-installed-as-a-single-plucked-binary.md) | component-catalog | fixed | untriaged | Undecided | **Propose verify:** fresh npm-based installation and state; actual agent edit/shell/test turn. Owner accepted the capsule as sandbox; --version or an obsolete sandbox command is insufficient. |
| [Upgrade recovery rejects its own remedy](../../bugs/devcapsule/2026-09-19-upgrade-config-recovery-rejects-its-own-remedy.md) | maintenance | closed | untriaged | Closed — owner accepted 2026-09-22 | PR #117 is in main and RC0; recorded owner and graphical acceptance supersede the pending integration note. Retain RC acceptance for later regressions. |
| [Configuration contract across boundaries](../../bugs/devcapsule/2026-09-20-configuration-contract-not-enforced-across-boundaries.md) | maintenance | closed | untriaged | Closed — owner accepted 2026-09-22 | G1–G9 have implementation, regression, integration and recorded owner/GUI evidence. Broader future contracts are not established by this closure. |
| [Nested-directory coordination data loss](../../bugs/devcapsule/2026-09-22-workflow-nested-directory-loses-coordination.md) | workflow-improvements | fixed | untriaged | Undecided | **Propose verify first:** downloaded RC0, disposable bare remote, nested/relative paths; compare unrelated blob IDs after every mutation. Existing test checks names, not all unchanged bytes. |
| [Flaky claim lifecycle test](../../bugs/devcapsule/2026-09-22-workflow-claim-test-flakiness.md) | workflow-improvements | confirmed | minor | Undecided | **Propose defer repair:** preserve owner-requested xfail and contract/design review. Verify intended claim operations in the isolated candidate journey; XPASS cannot establish lifecycle coverage. |

## Proposed Calls From The 2026-09-22 Review

The initial review proposed one bounded fix, two closures, eight targeted
verifications and five deferrals. **The owner accepted both closures on
2026-09-22; they are now applied.** Retirement of legacy `pycharm run` is also
selected and implemented on the release branch. Thirteen rows remain undecided:
eight targeted verifications and five deferrals. The accepted
image-composition deferral and two retirements remain unchanged. Other
workstreams' records have not been edited.

### Selected Resolution: Retire Legacy PyCharm Run

Pre-removal bug comb, 2026-09-22: only the legacy networking/parity record is
wholly retired by this change. The Codium records were already retired.
Multiline rendering still affects the shared builder; native-launcher and
preview behavior still affect the modern PyCharm component; formation and
container cleanup are independent. Keep the broader X11 record pending its
project-launch scope/acceptance review: explicit passthrough and fallback on
pre-contained-display bases remain in `select_display_transport`. Removing
the legacy CLI does not establish that every supported project launch avoids
host-session exposure. No other bug is retired merely for naming PyCharm.

Owner follow-up: preserve all potentially retiring capabilities for future
releases in the [V1-blocking work item](../../work-orders/2026-09-22-legacy-launch-capability-disposition.md).
It records the full inventory and requires explicit migrate/already-covered/drop
decisions, including the open question of an image-oriented launch for directories
without DevCapsule configuration. The owner confirms that current users are only
ourselves and everyday dogfood already uses `project run`; do not assume an
external installed-user migration burden. This future gate is not a new 0.2.14
implementation requirement.

**Owner-selected resolution:** retire the public `pycharm run` command
instead of adding more legacy options. The adapter and CLI-only helpers are
now removed; a non-launching retirement diagnostic handles old invocations.
Normal `project run` calls the shared `run_pycharm` implementation directly;
it does not depend on `PycharmRunCommand`. Keep that shared backend, and leave
`pycharm build` / `check-runtime` outside this proposed removal's scope.
Removing the public bypass also removes its ambient host-X11 entry path.

Retirement has a compatibility cost: this is still a documented command with
raw-image, profile/state and Docker-in-Docker options, not a proven exact alias
of configured `project run`. A release-specific exception and migration guidance
under R-COMPAT-001 must explain the new path and unsupported legacy-only uses.
Correct README examples, CLI/PEX smoke checks and shared-launcher diagnostics
that still prescribe the retired command. Give old invocations an actionable
migration error with no launch, and verify normal project launch is preserved.
Removal is implemented; integration and the next candidate are pending. The
narrower networking patch below is historical analysis, superseded by retirement.

The retained [CLI adapter](../../../devcapsule-src/devcapsule/commands/_pycharm.py)
constructs `PycharmRunOptions` without a network choice. The
[launcher](../../../devcapsule-src/devcapsule/launch/pycharm/_launcher.py) defaults
that field to `host` and emits it as Docker's network mode. A current CLI probe,
substituting only `run_pycharm`, returned 0 and observed `network_mode='host'`
for `pycharm run --project <temporary-directory> --image triage:unused`.
It launched no container. The source path is identical to RC0.

The initial, now-superseded proposal was a bounded correction: bridge
by default and an explicit host-network selection for users who need it,
with CLI-to-plan checks and one actual default/explicit-host Docker inspection.
Preserve normal configured `project run` choices and the retired run-image
decision. Proposed severity: major, because host access is enabled without
the developer's choice; this is not a unilateral release-blocker designation.
Do not silently remove the legacy command or redesign its entire option model.
If compatibility work expands substantially, return the scoped tradeoff to the
owner before turning it into a release refactor. A source fix needs RC1.

The removed legacy adapter also selected host-X11 transport. The broader X11
record still needs scoped acceptance for project launch, including its fallback
on older bases and explicit user selection. No display-policy redesign is
included in this command retirement.

### Evidence Supporting Closure Or Verification

- **Two configuration bugs:** merge `d2386bb` (PR #117) is an ancestor of
  both RC0 and freshly fetched main. Their 2026-09-21 acceptance updates and
  the [maintenance checkpoint](../../wip/2026-09-18-maintenance/2026-09-21-record-maintenance-before-component-upgrades.md)
  record successful owner use and normal graphical-successor exit from a
  0.2.12-authored configuration. The pending-integration wording is stale.
  Close those demonstrated failures; retain predecessor/permission/display
  checks in the release campaign for subsequent changes. Exact original host
  configuration bytes and exhaustive compatibility are not claimed.
- **PATH:** `base_image.py` exports the Node/JDK/Maven prefixes;
  `materialization.py` chains component PATH prefixes; the generic runtime
  preserves inherited PATH rather than installing a Node-specific override.
  Historical graphical evidence includes Node by name. Verify npm/npx and a
  child build in the actual derived candidate environment before closure.
  The bug's proposed metadata design is not itself proof that this implemented
  alternative violates the user-facing contract.
- **ACP and Codex layout:** the current Codex component declares its home
  slot/environment, full npm packages and a fresh-state configuration seed.
  Tests cover those declarations and launcher delivery. An ACP exchange and
  an agent command are different acceptance paths; test both without copying
  an old home that could mask missing initialization. Preserve the owner's
  capsule-as-sandbox policy rather than demanding the historical bubblewrap
  probe succeed as a closure prerequisite.
- **Preview and display:** PyCharm's template supplies the JCEF property and
  JVM option before startup. The contained display is recorded as shipped in
  0.2.12. Fresh GUI acceptance must establish actual preview and default
  session isolation; source assertions cannot establish either visual result.
- **Base consent:** current init tests cover local reference selection,
  interactive consent/refusal and the `--less-pedantic` path. The record mixes
  superseded yes/no grammar with later owner rulings. Test the settled current
  interaction and explain the remaining scope before closing; do not revive
  the rejected grammar just to satisfy historical close criteria.
- **Formation:** the recipe sets ENTRYPOINT/CMD and compares boot configuration
  with the descriptor; configuration-only repair and reuse have tests. Image
  reclamation remains a distinct unresolved policy, including images shared
  by other checkouts. Verify the repaired half and preserve the cleanup half.
- **Coordination:** the nested-directory regression and publish-keeps-claim
  tests pass. The nested test compares pre/post path-name sets, not every
  unrelated blob's identity, so strengthen acceptance evidence through the
  downloaded candidate rather than inferring byte preservation from that test.
  Never reproduce the original destructive scenario on shared coordination.

### Keep The Acceptance Work Small And Meaningful

1. **One fresh PyCharm + Codex journey:** reviewed initialization, contained
   desktop with no host X socket/cookie, declared Codex state, actual ACP
   exchange and agent edit/shell/test, node/npm/npx from terminal and child
   process, fresh Markdown/SVG previews, normal close and persistent relaunch.
   Inspect image ENTRYPOINT/CMD and second-launch reuse during the same run.
   Record human-visible outcomes and inspect mounts without exposing cookies
   or credentials. This combines checks; it does not claim other IDE/agent
   combinations were exercised.
2. **One existing-checkout journey:** candidate recovery from predecessor
   decisions, preserving explicit grants/denials and display intent. Include
   the base-selection consent interaction where applicable; no configuration
   copying or silent permission grant merely to make the test pass.
3. **One isolated coordination journey:** use downloaded RC0 with disposable
   repositories and a local bare remote. Exercise send/publish/claim/take from
   nested and relative project paths, with unrelated mail/state/claims seeded.
   Assert each intended delta and unchanged unrelated blob IDs after every
   operation. Exercise claim visibility/release without wall-clock-speed
   assumptions. This supplies candidate evidence for the repaired data-loss
   bug while the quarantined lifecycle test remains a separate design task.

These are proposed campaign checks, not completed E2E evidence. Add the
retirement rejection check to the next candidate acceptance. Stop each check
when its stated observation is established; investigate failures that change
the release decision rather than broadening into a new feature campaign.

### Validation Of This Review

243 existing focused checks passed: configuration contracts/invariants, Codex
component declarations, runtime entrypoint, project initialization, the two
coordination regressions, and selected launcher state/default/lifecycle cases.
The preceding image review's 45 image/base/materialization tests also passed.
No runtime code changed, no new containers or environments were provisioned,
and no authenticated provider/GUI acceptance is claimed by these results.
The release branch was not rebased or synchronized with main; only main's
remote-tracking ref was refreshed to verify integration facts.

## Prior Triage Input

The [saved maintenance proposal](../../wip/2026-09-18-maintenance/2026-09-21-note-proposed-bug-triage.md)
rated networking and the two configuration defects major, and other maintenance
items generally minor; those ratings were retained for later, not applied.
Its run-image-specific finding has since been superseded by that command's
removal. Its legacy `pycharm run` concern remains in the updated bug record.

The owner explicitly chose xfail plus a design-review bug for the flaky claim
test, not a quick timing fix. Its release target remains undecided. The marker
and bug are integrated in PR #131 and included in the release baseline.
