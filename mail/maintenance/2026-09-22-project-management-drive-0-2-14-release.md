# Maintenance Drives The 0.2.14 Release

Delivered: 2026-09-22
From: `project-management`, recording the product owner's explicit choice.

The owner selected maintenance as the 0.2.14 release driver. Release preparation
and stabilization belong to maintenance, using current main as the proposed
baseline. The owner requested the current open-bug inventory before proceeding;
no release branch or tag has been created and this item does not assert that a
cut or final bug scope has already been approved.

On resumption, reconcile the saved bug triage with the delivered run-image and
configuration fixes. The residual legacy `pycharm run` host-network default needs
a release disposition. Individual bug ownership remains unchanged: coordinate
with other owners for their applicable acceptance evidence. Set release targets
from the agreed scope, not merely from the existence of an open bug record.

PR #124 merged the corrected release runbook at 388ee50. Follow the local owner
rule: main stays open; prefer a suitable merge, otherwise cherry-pick, adapt the
correction, or establish that main is unaffected, with proportionate evidence.
The current per-candidate timing remains. Project-management retains the older
branch-name migration coordination due before RC0; it need not delay the cut.

Planned candidate acceptance should cover predecessor configuration recovery,
actual launch, project run --print-command, and preservation of coordination
state when commands run from a nested directory. The last validated source tree
passed 1,045 tests, one existing xfail, type checking and nine packaged checks;
this is not downloaded-candidate acceptance.
