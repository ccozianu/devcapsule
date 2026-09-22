# Use The 0.2.14 Release Working Documents

Delivered: 2026-09-22
From: `project-management`, recording the owner's release-working preference.

The owner requested a maintained Markdown release workspace instead of repeated
chat bug inventories. Prepared on project-management/coordination at 1ecd0e5:

- engineering-docs/releases/v0.2.14/README.md: scope, driver, checklist,
  candidate/acceptance progress and evidence.
- engineering-docs/releases/v0.2.14/bugs.md: all 19 current open bugs, linked
  canonical records, recorded metadata, release disposition and next action.

Maintenance is the selected release driver and maintains this workspace when
it takes over. Work through and update these files as decisions arrive; chat
should highlight changes and questions. All bug release dispositions remain
undecided except the separately recorded request to quarantine the flaky test;
its repair target remains open. Keep canonical bug status/severity/target/owner
and their table summaries reconciled. Preserve resolved rows for release history.

The operator guide now explains this local convention. The sibling v0.2.14.json
continues to be the machine-checked acceptance record, created only after an
exact candidate is accepted. No release branch or tag was created. This
workspace awaits the owner's normal PR integration; do not duplicate it.
