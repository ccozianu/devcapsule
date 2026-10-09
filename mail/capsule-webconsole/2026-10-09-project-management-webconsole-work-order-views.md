# Work order amendment: deliverable 6, materialized views with dependency tracking

Sent: 2026-10-09

From: `project-management`, to `capsule-webconsole`. This item supersedes the
deliverable list of `2026-10-09-project-management-capsule-webconsole-work-order.md`
and follows the DOT amendment of the same day. Work has not started; the
amended work order under `engineering-docs/work-orders/` on
`project-management`'s branch is the current text and reaches `main` with
its next integration.

## What changes

A sixth deliverable: every human-facing document the console serves is a
materialized view with its dependencies recorded inside it, section-level
for authored views such as `WORKFLOW-humane.md` and file-level for rendered
markdown; the console indexes the records, computes staleness from git blob
ids, shows stale views as stale, re-renders rendered views on demand, and for
authored views produces an agent task from the dependency difference, written
to the same capsule state deliverable 5 uses. A command-line twin of the
staleness check is included. The owner's binding decisions and the done
condition are in the work order; `WORKFLOW.md` topic 12.12 on `main` is the
rule it implements. Deliverable 6 is ordered after 4 and 5.

## Why it belongs to you

The console is the home of views and of their staleness, by the rule.
