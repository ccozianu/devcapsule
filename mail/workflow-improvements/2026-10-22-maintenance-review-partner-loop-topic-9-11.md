# Definition change by owner direction: topic 9.11, the review-partner loop

Date: 2026-10-22
From: maintenance
To: workflow-improvements

## Handoff

The owner directed on 2026-10-22 that the mechanism by which the capsule
web console (#184 to #206) and the session diagnostics (#207 to #212) were
built, one agent implementing and an agent of another engine reviewing by
an improvement pull request, be written into the workflow files so that
any capsule agent can run it from the files alone. Maintenance wrote it,
at the owner's request, as [PR #238](https://github.com/ccozianu/devcapsule/pull/238):

- `WORKFLOW.md`, new topic 9.11 *The review-partner loop*, in the
  controlled style, with a bullet in the 0.3.0 *Changes* entry and its
  companion paragraph in `WORKFLOW-humane.md`.
- `WORKFLOW-LOCAL.md`, *Review Partners In This Checkout*, the engines,
  checkouts and commands of this repository, with its companion.
- `engineering-docs/development/review-partner-loop.md`, the brief
  template, the assessment forms, the recipes and the record of the loops.

This is a notice, not a request. The definition is yours; review the topic
when you resume and fold it into the packaged copy at the release as rule 6
of *Workflow Definition Changes* says. Nothing is asked of you before then.
If you find the generic half says something the definition should say
differently, the change is yours to make.

## Evidence

- PR #238, stacked on PR #237 (the GitHub CLI rule of the local file).
- The process record of 2026-10-12 sent to the trading-research sample
  project, the source of the lessons the companion paragraph names.
