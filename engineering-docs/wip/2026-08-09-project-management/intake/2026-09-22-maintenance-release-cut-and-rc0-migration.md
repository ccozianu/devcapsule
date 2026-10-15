# 0.2.14 Is Cut; Finish The Pre-RC0 Branch Migration Coordination

Delivered: 2026-09-22
From: `maintenance`, now driving release 0.2.14 at the owner's direction.

Created release-0.2.14 from integrated preparation merge
21371084f7137624aed6c0581b12495a04b04fbb (PR #131). First release commit 36fa74e
sets version 0.2.14, registers the release routing and accepts both release
handoffs. The owner ruled that none of the listed bugs prevents starting;
fix or defer them as stabilization proceeds. The release working overview and
bug table are the continuing work surface. Initial build passed, including the exact-revision PEX and nine packaged checks; candidate
publication waits for the initial release PR's main disposition.

Please reconcile the pre-RC0 legacy branch-name migration retained in your
queue. Check current published/remote state before renaming: some ws-prefixed
refs already exist while main's registry still contains old associations.
Route each change through its owning workstream. Maintenance has explicitly
transitioned from ws-maintenance/triage to the retained release ref.
No RC or final tag has been created by this handoff. Routine bug work is not
held until the administrative migration is complete.
