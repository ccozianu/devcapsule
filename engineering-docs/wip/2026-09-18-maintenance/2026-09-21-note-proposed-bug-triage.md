# Proposed Maintenance Bug Triage

Date: 2026-09-21

Status: reviewed with the owner, who said the list makes sense and asked to
retain it for later. Severity/status fields have not been changed. The owner
redirected this slice to the early-adopter blog before final triage and pause.

## Proposed Ratings And Dispositions

Release targets remain unset for project-management to shape 0.2.14. Severity
is distinct from release importance; managed updates remain a high-priority
UX concern without an accepted 0.2.14 gate.

| Existing record (date and slug) | Severity | Proposed next action |
|---|---|---|
| 2026-07-13 codium-run-option-parity | minor | Retire the removed `codium_with_claude` path's record; identify any current specific gap separately. |
| 2026-07-16 codium-ambient-sudo-default | major historically | Retire: offending launcher/assets removed; shared hardening covers current surfaces. |
| 2026-07-16 pycharm-build-multiline-exec-rendering | minor | Narrow to generic multiline rendering; original Node tooling now joins commands on one line. |
| 2026-07-23 pycharm-ambient-host-network | major | Keep confirmed; current `run-image` still defaults to host networking and rejects explicit network passthrough. Recommend fixing before 0.2.14; release decision remains open. |
| 2026-08-03 codex-acp-missing-home | minor | Keep fixed pending specific fresh-state ACP acceptance; directory creation was an available workaround. |
| 2026-08-03 component-tooling-runtime-path | minor | Current tooling exports appear to supersede the failure; reconcile existing runtime evidence before closing. |
| 2026-08-03 ecosystem-aware-project-bootstrap | minor | Keep open as a capability gap; manual setup works and broader bootstrap requires product planning. |
| 2026-08-03 jbr-slow-x11-alpha-compositing | minor | Keep as an observation; no user-visible failure is recorded. |
| 2026-08-03 jcef-sandbox-container-preview | minor | Keep fixed pending explicit fresh-configuration Markdown/SVG preview acceptance. |
| 2026-08-03 jetbrains-native-launcher | minor | Keep open; warning without a recorded functional failure. |
| 2026-08-15 detached-successors-not-cleaned-up | minor | Keep open; visible retention and owned cleanup are missing, while deliberate evidence retention must survive. |
| 2026-09-02 authorize-base-image-conflates-consent-with-selection | minor | Keep fixed; reconcile remaining acceptance and grammar notes. |
| 2026-09-19 upgrade-config-recovery-rejects-its-own-remedy | major | Close based on merged fixes, regression tests, graphical upgrade acceptance and owner-reported successful live use. |
| 2026-09-20 configuration-contract-not-enforced-across-boundaries | major | Close identified repaired failures; broader coverage remains a separate follow-up. |

All records live under `engineering-docs/bugs/devcapsule/`. Three other-owner
records remain: X11 credential exposure (`contained-display`), formation
entrypoint/image lifecycle and incomplete Codex installation layout
(`component-catalog`). Their owners should reconcile acceptance and closure;
the formation record mixes an implemented correction with unresolved image
cleanup. No ownership changes were made.

## Current Networking Evidence

Inspected the source at `a6ad13c`, whose implementation matches merged main
`7d1df73`. A read-only Python probe patched only `run_pycharm`, invoked
`cli.main(['project', '--path', existing_directory, 'run-image',
'triage-image:unused'])`, and inspected the launch options. It returned 0 and
passed `network_mode='host'` without an explicit network choice. Calling
`reject_launcher_owned_docker_options(['--network', 'bridge'])` refused the
override and recommended the project authorization mechanism, which
`run-image` does not expose.

The production trace is `ProjectRunImageCommand.run` constructing
`PycharmRunOptions` without `network_mode`, whose default in
`launch/pycharm/_launcher.py` is `host`. The same module refuses `--network`
passthrough. This probe launched no Docker container and changed no host
configuration. The normal lock-driven `project run` supplies its reviewed
network choice separately; this finding is about the expert compatibility path.

## Resume

Return to the proposed batch with the owner, apply the settled ratings and
dispositions with supporting notes, and prepare maintenance's pause for
project-management to shape the release. Do not mistake this saved proposal
for applied bug metadata or an agreed release scope.
