# DevCapsule Workflow And Issue Trackers: Positioning

Status: adopter-facing positioning, decided 2026-08-29 by the product owner.
Referenced by the [V1 announcement](v1-announcement.md). The reasoning and
measurements behind this position are recorded in
[The workflow versus Jira and GitHub Issues](../../engineering-docs/wip/2026-08-09-project-management/2026-08-19-workflow-versus-issue-trackers.md).

## The Short Answer

The workflow DevCapsule ships is not a project-management system and does not
substitute for one. It is the agent's memory: what the agent reads to resume
work effectively, and what it writes so the next session — human or agent —
can. A tracker is where people agree; the in-tree records are what the agent
can read at the moment it acts. Adopting DevCapsule asks nobody to abandon
anything.

How much the workflow carries depends on the size of the project, and the two
scopes below are both supported positions, not a fork in the product.

## Alongside A Larger Team Process

If your project already has a team-level engineering process — project
management software like Jira, GitHub Projects and Issues, or any established
equivalent — that process remains the system of record, untouched.

In that setting, the DevCapsule workflow manages strictly the workflow
**between the human and the agent**:

- it gives the agent its memory — the relevant context needed to effectively
  support the human in what the human decides to do;
- it records the human–agent working state: the current intent, the handoff,
  what was validated, what remains;
- it deliberately does not mirror, replace, or compete with the team's
  tracker.

**In V1, moving context across that boundary is the human's responsibility.**
You bring the relevant information from the larger project's process into the
workspace — by copy and paste if need be — and you carry results back out the
same way. V1 claims no tracker integration, and this document says so plainly
rather than implying one.

## As The Process For A Small Project

For smaller projects the workflow can be scoped to be more than the
human–agent channel. It can carry the project's engineering records
themselves — requirements, decisions, bug records, validation notes, and
handoffs — as the project's working process.

**The promise is sized to a small team: one to five developers.** For that
audience the honest comparison is not against Jira, because these projects
rarely have one. Nobody stands up a Jira project for solo work, and issues on
a personal repository are usually three stale entries. For the actual target
user, the alternative to in-tree records is not a tracker; it is nothing —
which is the status quo this product exists to improve.

## What A Tracker Does Better

Conceded without argument, so the position is not an overclaim:

- search, notifications, assignment, dashboards, mobile access, permissions,
  mentions, and integrations come for free with a tracker;
- non-developers — a product manager, a designer, a support engineer — can
  read and file issues; none of them read Git refs;
- everyone already knows how a tracker works, and any in-tree convention has a
  learning cost.

Teams that outgrow the one-to-five promise should keep their tracker. That is
the position, not a fallback.

## Why The Agent's Memory Lives In The Tree

- **It is present unconditionally.** Inside a capsule the repository is there
  with no credential, no network egress, no token to keep fresh, and no rate
  limit. Every one of those is exactly the kind of exposure DevCapsule exists
  to make explicit rather than ambient.
- **It is versioned with the code.** A decision and its implementation land in
  one commit, are reviewed together, and are bisected together. "What did the
  plan say when this line was written" is answerable in-tree and unanswerable
  in a tracker.
- **The agent can write it well.** An agent edits a markdown file natively and
  reviewably. An agent updating a ticket needs API access and does it badly.
- **No vendor hostage.** It works offline, on any host, and after any
  subscription lapses.

## Roadmap: A Bridge, Not A Replacement

Larger teams keep their tracker, and the industry's chosen shape for
connecting trackers to agents is already clear: MCP bridges to Jira, GitHub,
and their peers, with agents both reading and writing tracker state.

DevCapsule's future position is on thesis: a tracker bridge, when it comes,
will be an optional, explicitly authorized component — its credential and
network grant declared in the run manifest and visible in inspection output,
never ambient. And tracker content crossing that bridge will be treated as
untrusted input, because a tracker is a surface anyone can write into.

None of that is claimed for V1. In V1 the bridge is you.
