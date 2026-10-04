# Local host-network launch instruction is rejected by the CLI

From: component-catalog
To: maintenance
Date: 2026-10-04

The IntelliJ/Playwright graphical smoke found that WORKFLOW-LOCAL.md's
standing local-launch instruction, `project run --authorize network host`,
is rejected by the current CLI. At source ada153c (main baseline 17532fd),
`_RUN_ONCE_AUTHORIZATIONS` excludes network. The error lists docker-daemon,
development-sudo, host-browser and host-x11 as the accepted run-once choices.
The run help also refuses raw `--network` as a composed single-instance option.

Evidence: IDE smoke run 20261004T002133Z-8f8069, before any container launch;
local log `.git/codium-agent-smoke.log` was subsequently reused, but the run's
`dist/e2e-evidence/ide-smoke/.../codium/launcher.log` retains the rejection.
Source: devcapsule-src/devcapsule/commands/project.py `_run_once_answers`;
WORKFLOW-LOCAL.md, Local Launch Networking.

This is a generic launcher/local-policy mismatch, outside the component and
smoke-driver slice. Please reconcile the supported command and documented
operating rule, or route the documentation aspect to its owner. Acceptance
means the local guide gives a working host-network command with its intended
scope and the CLI does not recommend an unsupported alternative.

Our authorized test continues through supported `project init --authorize
network host "Local graphical smoke requires host networking."`, recording
host networking only in its disposable project. We did not change the human's
checkout authorization or fix the generic launcher on the component branch.
No priority or release target is assigned by this handoff.
