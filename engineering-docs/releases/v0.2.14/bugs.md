# 0.2.14 — Bug Triage

[Release overview](README.md)

Reconciled: 2026-09-22 against integrated bug records at cut `2137108`.
19 tracked records: 17 open (nine reported/confirmed, eight fixed but not closed)
and two retired after verifying their command/implementation was removed.
All have workstream owners. All currently have `target: none`; 16 have
`severity: untriaged`, three have `severity: minor`; among the 17 open records,
14 are untriaged and three are minor.

Owner decision, 2026-09-22: none of this current list blocks starting the
release. The owner further confirmed that the bug list itself does not prevent
publication: fix or verify a selected few while validating major end-user E2E
journeys. Resolve or defer bugs during stabilization. Rows remain undecided
until their individual disposition is recorded; this is not blanket closure
or a decision that every bug must be fixed in 0.2.14.

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
| [Codium runtime-option parity](../../bugs/devcapsule/2026-07-13-codium-run-option-parity.md) | maintenance | retired | untriaged | Retired — removed implementation | Local RC0 rejects the old command; candidate tree lacks its launcher/assets. See linked retirement evidence. |
| [Codium ambient passwordless sudo](../../bugs/devcapsule/2026-07-16-codium-ambient-sudo-default.md) | maintenance | retired | untriaged | Retired — removed implementation | Local RC0 rejects the old command; candidate tree lacks its launcher/assets. See linked retirement evidence. |
| [Multiline Dockerfile quoting](../../bugs/devcapsule/2026-07-16-pycharm-build-multiline-exec-rendering.md) | maintenance | reported | untriaged | Undecided | Narrow to any remaining generic multiline-rendering failure. |
| [Legacy PyCharm host networking](../../bugs/devcapsule/2026-07-23-pycharm-ambient-host-network.md) | maintenance | confirmed | untriaged | Undecided | Decide whether legacy `pycharm run` needs a fix for 0.2.14; run-image replacement is complete. |
| [Codex ACP missing CODEX_HOME](../../bugs/devcapsule/2026-08-03-codex-acp-missing-home.md) | maintenance | fixed | untriaged | Undecided | Reconcile fresh-state ACP exchange and persistence acceptance. |
| [Component tooling missing from PATH](../../bugs/devcapsule/2026-08-03-component-tooling-runtime-path.md) | maintenance | confirmed | untriaged | Undecided | Reconcile runtime evidence; current exports may supersede the failure. |
| [Manual ecosystem setup for fresh clones](../../bugs/devcapsule/2026-08-03-ecosystem-aware-project-bootstrap.md) | maintenance | confirmed | untriaged | Undecided | Decide scope; manual setup works, broader bootstrap needs product planning. |
| [JetBrains X11 alpha-compositing warning](../../bugs/devcapsule/2026-08-03-jbr-slow-x11-alpha-compositing.md) | maintenance | reported | minor | Undecided | No user-visible failure recorded; decide deferral. |
| [JetBrains embedded-browser preview](../../bugs/devcapsule/2026-08-03-jcef-sandbox-container-preview.md) | maintenance | fixed | untriaged | Undecided | Reconcile fresh-configuration Markdown/SVG preview acceptance. |
| [PyCharm native-launcher warning](../../bugs/devcapsule/2026-08-03-jetbrains-native-launcher.md) | maintenance | reported | minor | Undecided | No functional failure recorded; decide deferral. |
| [Exited containers not cleaned up](../../bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md) | maintenance | reported | untriaged | Undecided | Decide scope for visible retention and owned cleanup. |
| [X11 host-session credential exposure](../../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md) | contained-display | fixed | untriaged | Undecided | Owner to reconcile closure with contained display shipped in 0.2.12. |
| [Base-image consent versus selection](../../bugs/devcapsule/2026-09-02-authorize-base-image-conflates-consent-with-selection.md) | maintenance | fixed | untriaged | Undecided | Reconcile current wording, semantics and acceptance. |
| [Formation entrypoint and image lifecycle](../../bugs/devcapsule/2026-09-02-formation-identity-claims-an-entrypoint-the-recipe-never-sets.md) | component-catalog | confirmed | untriaged | Undecided | Owner to separate implemented entrypoint correction from remaining image cleanup. |
| [Incomplete Codex installation](../../bugs/devcapsule/2026-09-05-codex-installed-as-a-single-plucked-binary.md) | component-catalog | fixed | untriaged | Undecided | Reconcile fresh-state installation and actual agent-command acceptance. |
| [Upgrade recovery rejects its own remedy](../../bugs/devcapsule/2026-09-19-upgrade-config-recovery-rejects-its-own-remedy.md) | maintenance | fixed | untriaged | Undecided | Integrated; existing owner/graphical acceptance supports closure. |
| [Configuration contract across boundaries](../../bugs/devcapsule/2026-09-20-configuration-contract-not-enforced-across-boundaries.md) | maintenance | fixed | untriaged | Undecided | Integrated; existing owner/graphical acceptance supports closure of repaired failures. |
| [Nested-directory coordination data loss](../../bugs/devcapsule/2026-09-22-workflow-nested-directory-loses-coordination.md) | workflow-improvements | fixed | untriaged | Undecided | Integrated; real nested-directory or RC acceptance pending. |
| [Flaky claim lifecycle test](../../bugs/devcapsule/2026-09-22-workflow-claim-test-flakiness.md) | workflow-improvements | confirmed | minor | Undecided | Owner requested xfail and testing-design review; quarantine prepared, repair scope remains open. |

## Prior Triage Input

The [saved maintenance proposal](../../wip/2026-09-18-maintenance/2026-09-21-note-proposed-bug-triage.md)
rated networking and the two configuration defects major, and other maintenance
items generally minor; those ratings were retained for later, not applied.
Its run-image-specific finding has since been superseded by that command's
removal. Its legacy `pycharm run` concern remains in the updated bug record.

The owner explicitly chose xfail plus a design-review bug for the flaky claim
test, not a quick timing fix. Its release target remains undecided. The marker
and bug are integrated in PR #131 and included in the release baseline.
