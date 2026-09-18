# Intake: `maintenance` Drives Maintenance Releases; Bug Triage Has An Owner

Delivered: 2026-09-18

From: `workflow-improvements`, following up its 2026-09-16 item on the release
runbook.

## What Is Being Handed Over

Two facts that change what the 2026-09-16 item told you, both from the
reserved `maintenance` workstream that the product owner directed on
2026-09-18 and that is registered in the same round as this item.

1. **Maintenance releases of already released versions are driven by
   `maintenance`**, not by `project-management`. The 2026-09-16 item's point 6
   said otherwise; the rule as drafted for `main` now reads: the workstream
   whose deliverable is the release's headline drives; a maintenance release
   of a released version is driven by `maintenance`; `project-management`
   decides who drives only when the headline is unclear. The runbook's
   "who drives" wording follows from that once the rule lands.
2. **Bug triage has an owner and a vocabulary.** Every bug record now carries
   controlled `status`, `severity`, `target`, and `owner` fields, defined in
   *Bug Intake*. The V1 readiness assessment's finding that thirteen open bugs
   carry no triage against V1 is now answerable from the records: twelve open
   bugs are owned by `maintenance` with `severity: untriaged`, three are owned
   by `contained-display` and `component-catalog` as `fixed` pending
   validation, and the product owner's rating is the triage. The format is
   shaped to be checked by the `pre-commit` invariant work on your backlog: a
   record without the frontmatter, or an open one with `owner: none` in this
   mode, is a checkable violation.

## Why It Belongs Here

You own the release runbook and the V1 readiness ledger. Neither is edited by
`workflow-improvements`.

## What Accepting Would Mean

Folding point 1 into the same runbook edit the 2026-09-16 item asks for, and
recording in the readiness ledger that bug triage is now the owner's rating in
the `maintenance` workstream rather than an unowned gap.

## Sequencing

Nothing here is needed before the pull request carrying *The Reserved
`maintenance` Workstream* merges. The triage itself is the owner's and is the
`maintenance` workstream's first task.
