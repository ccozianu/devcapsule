---
id: R-GTM-001
title: Compelling V1 Announcement For Adopters
type: requirement
kind: concrete-requirement
status: implemented
priority: current
source_of_truth: repo
verification:
  - doc-review
  - artifact-review
external_refs: []
---

# R-GTM-001: Compelling V1 Announcement For Adopters

## Statement

The project must have a V1 announcement markdown artifact that explains the
adopter benefit clearly and compellingly, not just the implementation details
or development history.

## Why This Exists

Technical correctness is not enough to attract early adopters. The project
needs a concrete explanation of why a developer, maintainer, or small team
should care.

## Verification

This is a concrete requirement. It is satisfied when the V1 announcement exists
and can be reviewed against these criteria:

- it states who the product is for;
- it states the main user problem in plain language;
- it answers “what’s in it for me?” before deep technical detail;
- it describes the V1 outcome in terms of user value, not only architecture;
- it gives concrete examples of developer benefit;
- it is stored as a versioned markdown artifact in the repository.

### Added 2026-08-19: The Issue-Tracker Objection

Adopters will ask why engineering records live in the source tree rather than in
Jira or GitHub Projects and Issues, and will call the in-tree ceremony
unnecessary conceptual load. The announcement must answer that out loud rather
than leaving a reader to supply the objection unchallenged. It is satisfied on
this point when the announcement:

- states plainly that the workflow does not replace an issue tracker, and that
  adopting it requires abandoning nothing;
- says what the in-tree records are *for* — what the agent reads to resume work,
  and what it writes so the next session can — rather than presenting them as
  project management;
- names its audience, for whom the alternative to in-tree records is usually no
  records at all rather than a tracker; and
- concedes what a tracker does better, instead of overclaiming.

The reasoning, the measurements behind it, and the larger-team roadmap are in
the `project-management` note
[The workflow versus Jira and GitHub Issues](../../wip/2026-08-09-project-management/2026-08-19-workflow-versus-issue-trackers.md).

**Status consequence, flagged not resolved.** The current artifact,
`docs/product/v1-announcement.md`, does not mention issue trackers at all, so it
does not satisfy the criteria added above. This record's `status: implemented`
therefore needs the product owner's review; it has deliberately not been changed
here.

## Related

- `R-PRODUCT-001`
- `R-PRODUCT-004`
- `R-DOCS-002`
