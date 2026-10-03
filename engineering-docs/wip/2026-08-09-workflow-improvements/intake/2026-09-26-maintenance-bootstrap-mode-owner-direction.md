# Owner direction on the bootstrap mode bug; supersedes today's earlier item on its "shape is open" point

Sent: 2026-09-26
From: `maintenance`, carrying the owner's ruling of the same day.

The record `engineering-docs/bugs/devcapsule/2026-09-26-bootstrap-cannot-choose-the-workflow-mode.md`
(`ws-maintenance/post-0.2.14` at `0152ae3`) now carries the owner's direction:
it is a usability bug; when the tooling installs a workflow it asks the user
which mode to use and does the needful, with the answer on the command line
for unattended runs and no silent default; and a `[workflow] mode` without an
installed `WORKFLOW.md` is void, so nothing may write or infer a mode for a
project that has no workflow. That touches the bootstrap specification, the
generic definition's *Workflow Declaration* and the `AGENTS.md` fallback, and
`project init`. Sequencing is yours with project-management; 0.2.15 is the
init fix alone.
