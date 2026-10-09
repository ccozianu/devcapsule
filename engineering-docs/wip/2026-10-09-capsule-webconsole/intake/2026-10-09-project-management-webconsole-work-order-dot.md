# Work order amendment: diagrams in DOT, not Mermaid

Sent: 2026-10-09

From: `project-management`, to `capsule-webconsole`. This item supersedes the
diagram notation in `2026-10-09-project-management-capsule-webconsole-work-order.md`,
delivered earlier today. Everything else in that work order stands.

## What changes

Deliverable 4 and binding decision 5 named Mermaid as the diagram notation.
The owner decided on 2026-10-09 that the project uses the DOT language only,
rendered by Graphviz and related software; see `WORKFLOW.md` topic 9.6 rule 6
on `main`. The work order under `engineering-docs/work-orders/` is amended
accordingly on `project-management`'s branch and reaches `main` with its next
integration.

- Deliverable 4 done condition: fenced `dot` blocks in rendered markdown
  render as Graphviz diagrams.
- Implementation: a vendored Graphviz build for the browser, such as `viz.js`
  or `d3-graphviz`, beside `markdown-it`. No Mermaid.

## Why it belongs to you

The console is the renderer the rule relies on for inline DOT, since GitHub
does not render it.
