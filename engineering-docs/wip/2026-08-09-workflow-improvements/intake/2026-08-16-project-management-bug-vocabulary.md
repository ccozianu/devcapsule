# Intake: A Shared Vocabulary For Bugs And Their Properties

Delivered: 2026-08-16

From: `project-management`, at the product owner's request.

## What Is Being Handed Over

Bug records need a shared vocabulary and a defined set of properties, so that
questions about them can be answered from the records rather than by reading all
of them.

## Why It Belongs Here

Record formats and their maintenance rules are workflow protocol. The requesting
workstream needs the answer but should not define the vocabulary it wants to
query.

## Evidence

On 2026-08-16 the product owner asked which bugs are high priority. No bug can
answer, and the reason is structural rather than a matter of a few missing
entries.

Across the thirteen records in `engineering-docs/bugs/devcapsule/`:

- **No record carries a priority or severity field.** Zero of thirteen.
- `Status:` is free prose with no shared vocabulary. Observed values include
  `open`; `open; diagnosed and evidenced, no fix implemented`;
  `reproduced; accepted V1 backlog item`;
  `observed in external dogfood; low-priority V1 review`;
  `V1 workaround implemented and automated; external GUI validation pending`;
  `accepted parity gap; first shared state-layout slice implemented, broader
  parity still pending`; and `reopened; open pending an explicit network option`.
  One record's status line has wrapped into prose and no longer parses as a
  status at all.
- Requirement references exist but are not uniform, so tracing a bug to the
  requirement it threatens is manual.

Root requirement records already demonstrate the shape that works: frontmatter
plus markdown, with a controlled `status` vocabulary defined in `REQUIREMENTS.md`
(`proposed`, `accepted`, `implemented`, `validated`, `deferred`, `rejected`).
Bugs have no equivalent.

## Consequences Already Observed

- The
  [V1 readiness assessment](../../2026-08-09-project-management/2026-08-16-v1-readiness-assessment.md)
  recorded that thirteen open bugs carry no triage against V1, so the release
  can neither be declared nor refused on evidence.
- The product owner's stated condition for starting their own projects — v026
  plus the high-priority bugs — currently names an empty set, because priority
  is not expressible.
- `index.md` was missing one bug entirely until 2026-08-16, which suggests the
  index and the directory can disagree without anything noticing.

## Sender's Analysis

Offered as analysis, not as constraints on this workstream's judgment.

- The properties that would have answered the actual questions asked this week
  are priority or severity, a controlled status vocabulary, the release target,
  the requirements threatened, and whether the bug blocks a named release.
- Whatever vocabulary is chosen, something should check that it is used, since
  the same unenforced-invariant problem already let a bug go unindexed. This
  pairs with the documentation-gate gap the readiness assessment records as
  unowned.
- Deciding that free-text status is sufficient, and that priority lives
  elsewhere such as in a release ledger, is a valid outcome and should be
  recorded explicitly rather than left implicit.

## What Accepting Would Mean

A defined bug record format and controlled vocabulary in `WORKFLOW.md`, applied
to the existing thirteen records, or an explicit decision that the current form
is sufficient and why.
