# The Workflow Versus Jira And GitHub Issues

Written 2026-08-19 by `project-management`, answering an objection the product
owner raised on an adopter's behalf: projects normally manage engineering
records in Jira or GitHub Projects and Issues, so source-tree ceremony adds
conceptual load for no clear gain.

The objection will be raised publicly, so the announcement has to answer it out
loud. This note is the reasoning; the criteria that follow from it are recorded
in `R-GTM-001` and `R-PRODUCT-004`.

## Where The Objection Is Correct

Conceded without argument, because the measurements are ours:

- **Learning cost is real.** Roughly nineteen coined terms across 111KB of
  documents, with no glossary. Everyone already knows Jira.
- **A tracker gives away for free** what this approach has none of: search,
  notification, assignment, dashboards, mobile access, permissions, mentions,
  and integrations.
- **Non-developers can participate in a tracker.** A product manager, a
  designer, or a support engineer can read an issue. None of them can read a Git
  ref.
- **The ceremony cost is measured, not speculative.** Since multiple-stream
  adoption, 84% of non-merge commits touch no code; work management outnumbers
  product code 80 to 32 with workflow definition already discounted; four of
  ten pull requests existed only to deliver mail; and two intake items sat
  stranded for two days.

The answer to that last point is to remove ceremony, which the 2026-08-19
storage decision does, not to defend it.

## What The Objection Misses

It answers a different question. A tracker answers *where humans agree*. The
question this product turns on is *what the agent can read at the moment it
acts*.

Inside a capsule the repository is present unconditionally: no authentication,
no network, no token, no rate limit. A tracker is present only if the developer
provisions a credential, installs a bridge, opens network egress, and keeps the
token fresh. Every one of those is the exposure this product exists to make
explicit. `D-0005` keeps bases agent-neutral and mounts no credential directory
by default; `R-SCOPE-001` and `R-DOCKER-001` govern the rest.

**This is evidenced rather than hypothesized.** The session that produced this
note ran in an environment with no `gh` CLI and no GitHub token — which is why
six prepared deliveries could not be opened as pull requests. Had this project's
state lived in GitHub Issues, the agent could not have read the plan at all.
Every useful thing it did that day — resuming from the handoff, catching that
"awaiting a pull request" was stale after the merge, finding that a disposition
log and its `intake/` directory disagreed — came from reading files in the tree.

Three further properties a tracker cannot provide:

- **Versioned with the code.** A decision and its implementation can land in one
  commit, be reviewed together, and be bisected together. "What did the plan say
  when this line was written" is answerable in-tree and unanswerable in a
  tracker, where ticket and code drift apart.
- **No vendor hostage.** Works offline, on any host, after the subscription
  lapses. Tracker exports are lossy.
- **The agent can write it.** An agent edits a markdown file natively and
  reviewably. An agent updating a ticket needs API access and does it badly.

## The Positioning Defect This Reveals

The objection is partly invited by this project's own vocabulary. "Workstream
registry", "portfolio checkpoint", "intake dispositions", and a workstream named
`project-management` all announce a project-management system, so a reader
benchmarks it against Jira and finds it worse.

Described instead as **agent context and handoff** — what the agent reads to
resume, and what it writes so the next session can — the comparison barely
arises. That is a framing defect rather than a design defect, and its fix
belongs with the information-model task rather than being separate work.

The line to lead with: **this is not a project-management system, it is the
agent's memory.** A tracker is where people agree; the tree is what the agent
reads to resume. Adopting the workflow asks nobody to abandon their tracker.

## The Segmentation Answer, Which Is The Decisive One

V1's users are the learner or tinkerer, the serious solo developer, and small
teams of roughly two to five. **None of them has Jira.** Nobody stands up a Jira
project for solo work, and GitHub Issues on a personal repository is usually
three stale entries.

For the actual target user the alternative to in-tree records is not a tracker;
it is **nothing** — which is the status quo the product exists to improve. The
tracker comparison bites hardest for large teams, who are not V1's audience.
Stating that converts the objection from a rebuttal into a segmentation
statement.

## The Roadmap For Larger Teams

Larger teams keep their tracker. The roadmap is a bridge, not a replacement, and
the research below says the bridge is already the industry's chosen shape.

**Verified 2026-08-19.** The Atlassian Rovo MCP Server reached general
availability on 2026-02-04, exposing more than sixty tools across Jira,
Confluence, Bitbucket Cloud, Compass, and Jira Service Management to any
MCP-compatible client, with Claude, Cursor, and Gemini CLI among them.
Enterprises account for close to half of its usage, paid editions for 93%, and
roughly a third of agentic operations are writes rather than reads — so agents
are editing tracker state, not merely reading it. Atlassian opened a beta in
March 2026 in which agents appear as assignees on Jira boards alongside humans.
GitHub's MCP server covers issues and pull requests comparably.

So the answer to "do teams bridge their tracker to their agent over MCP" is yes,
and increasingly by default.

**Two findings make that bridge a DevCapsule opportunity rather than a threat.**

First, the bridge is operationally awkward exactly where this product is strong.
The local GitHub MCP server runs in a Docker container and fails opaquely when
Docker is not running; full OAuth works only in some editors, so a long-lived
personal access token is the recommended path for others; and configuration
scope errors are a common failure. A declared, reproducible environment is a
better host for that than a developer's laptop.

Second, and more important: **a tracker is an attacker-writable surface, which
makes bridging one a prompt-injection channel by construction.** Anyone who can
file an issue can write into the agent's context. This is not theoretical — in
mid-2025 a Cursor agent with privileged database access processed support
tickets containing user-supplied text as instructions, and an attacker used
embedded SQL to exfiltrate integration tokens. Industry guidance through 2026
converged on short-lived, narrowly scoped, just-in-time credentials instead of
long-lived tokens, against a backdrop of more than thirty MCP-related CVEs in
the first two months of 2026.

That is the roadmap position, and it is on thesis rather than bolted on:

- the tracker stays the human coordination surface, untouched;
- the in-tree handoff stays the agent's working memory — trusted, versioned,
  reviewed;
- the bridge is an **optional, explicitly authorized component**, on the same
  footing as the agent components under `D-0005`, so the credential and the
  network grant appear in the run manifest and in inspection output rather than
  being ambient; and
- tracker content crossing that bridge is treated as **untrusted input**,
  because it is.

The claim this earns is narrow and defensible: DevCapsule is the environment
where bridging your tracker to your agent is a declared, inspectable, blast-
radius-bounded arrangement instead of a personal access token in a home
directory. It should not be claimed for V1, since no such component exists.

## Consequences Recorded Elsewhere

- `R-GTM-001` gains criteria requiring the announcement to answer the
  objection, state the segmentation, and avoid positioning the workflow as a
  tracker replacement. The current artifact, `docs/product/v1-announcement.md`,
  does not mention trackers at all, so that record's `status: implemented` needs
  review.
- `R-PRODUCT-004` gains validation signals for minimum viable adoption and for
  not requiring an adopter to replace an existing tracker.
- The framing fix belongs to the information-model task already delivered to
  `workflow-improvements`.

## Sources

- [Atlassian Rovo MCP Server general availability](https://www.mindstudio.ai/blog/atlassian-mcp-server-ga-claude-reads-writes-jira-confluence-compass-oauth)
- [Atlassian embeds agents into Jira and embraces MCP](https://siliconangle.com/2026/02/25/atlassian-embeds-agents-jira-embraces-mcp-third-party-integrations/)
- [Jira MCP: connecting Jira to an AI coding agent](https://getunblocked.com/blog/jira-mcp/)
- [GitHub MCP server setup guidance for Claude Code](https://www.hustletoai.com/blog/ai-coding-6/github-mcp-server-claude-code-setup-guide-2026-80)
- [MCP security risks, real incidents, and controls](https://checkmarx.com/learn/mcp-security-risks-real-world-incidents-and-security-controls/)
- [The state of MCP security in 2026](https://techcommunity.microsoft.com/blog/microsoft-security-blog/the-state-of-mcp-security-in-2026/4531327)
