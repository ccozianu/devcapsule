# Remove run-image and print the normal launch for debugging

From: project-management
To: maintenance
Date: 2026-09-22
Authority: owner explicitly chose removal and simplified the replacement to stdout.

Implement this bounded change for 0.2.14 preparation. Remove project run-image;
add project run --print-command using the ordinary final Docker argument builder.
The accepted contract is at:
https://github.com/ccozianu/devcapsule/blob/44166ebf9a801db4341aea9306a6267f7bd8ec60/engineering-docs/wip/2026-08-09-project-management/2026-09-21-design-editable-project-launch.md

Stdout contains only safely quoted shell command text and explanatory # comments;
progress and preparation diagnostics go to stderr. Explain transient files,
sockets and environment dependencies that manual execution must handle. Comments
precede the continued command, since comments between continuation lines corrupt
shell syntax. No editor integration, replay bundle, retained-resource mechanism,
universal subprocess interception, project-container execution or successful-use
recording in print mode. Normal authorized preparation remains possible and must
be documented honestly. Avoid update selection/prompts just to print current use.

This belongs to maintenance as the owner of the run-image network/parity defect.
Check retained callers of its shared host-network default before retiring the bug.
Use focused argv/stdout/lifecycle tests and the required build gate; no new real
Docker environment is needed merely for text rendering. Preserve normal launch.

The owner has not yet selected maintenance for this checkout; project-management
has only finalized and delivered the task. This assignment does not authorize a
release tag or reopen the paused component-upgrades operational work.
