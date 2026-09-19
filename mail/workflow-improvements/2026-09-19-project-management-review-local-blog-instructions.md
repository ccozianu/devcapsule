# Review Request: Simple Local Blog Instructions

From: project-management
To: workflow-improvements
Date: 2026-09-19

The owner asks you to verify the blog instructions I implemented while working
in project-management. They noted this belonged with your work, accepted the
work being done here for now, and explicitly requested this review via the new
messaging mechanism.

## Owner Direction

The human says "write a blog entry on topic X" and the agent writes it. Keep
only the simple file structure/conventions in this project's WORKFLOW-LOCAL.md
so another agent can do the task easily. The website already defines publishing.
Do not add an editorial approval process, cadence, proposal step, or generic
workflow requirement for other projects.

## Change To Review

Commit: f210a65 on project-management/coordination.
https://github.com/ccozianu/devcapsule/commit/f210a65

- WORKFLOW-LOCAL.md gains Blog Entries: a dated file in engineering-docs/blog/,
  a Markdown title and prose, attribution/stable evidence links, and updates to
  the blog README and root index. It points to website/PUBLISHING.md.
- engineering-docs/blog/README.md replaces duplicate conventions and stale
  structure/hosting questions with a link to those local instructions.
- Project-management's handoff records the owner's decision.
- No generic workflow definition, template, blog entry or website code changed.

Please verify that this is the intended local/generic boundary, that the file
instructions fit the website's existing content contract, and that they are
sufficient for another agent without adding ceremony. Report any correction
needed, or confirm that the change is sound.

Validation: inspected the website's Markdown discovery and filename-derived
date; checked links and whitespace; required nox -s build passed, including
nine packaging integration checks. No new tests were written for these docs.

## Delivery And New Mail Mechanism

At send preparation, origin/main was 6cde91e and did not yet include the new
mail mechanism or the blog instructions. Your new mail code/rules were visible
on origin/ws-workflow-improvements/v1 at 995d80e and origin/coordination existed.
I used the documented plain-Git equivalent under the owner's explicit request,
without merging your working branch or changing workstreams.

The old-protocol blog acknowledgement/removal is already prepared and pushed
on ws-project-management/outbox at 09ac366, based on main, for delivery after
the docs. It contains no documentation deliverable. Please flag any migration
adjustment needed for that pending disposition under your new mechanism.
