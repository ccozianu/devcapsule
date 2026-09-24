# Help new projects start with an installed workflow

From: maintenance
To: workflow-improvements
Date: 2026-09-24
Requested action: acknowledge the owner-requested non-blocking onboarding work.

The website declaration exists but WORKFLOW.md is absent. The owner wants a
batteries-included setup that helps new users start with the workflow installed.
The owner says the historical initialization was agent-authored outside the
normal path; maintenance did not reconstruct that history. Do not treat this as
proof that normal init was exercised or failed. This improvement is explicitly
not a 0.2.14 blocker. Define supported interactive/unattended setup, mode choice,
repeat behavior and preservation of existing workflow/version/user files.

Canonical work item: engineering-docs/work-orders/2026-09-24-workflow-installation-onboarding.md
on release-0.2.14. The separate absence of the public devcapsule command inside
the runtime is a confirmed 0.2.14 blocker owned by maintenance; it prevents
normal manual workflow installation too. No onboarding code changed.
