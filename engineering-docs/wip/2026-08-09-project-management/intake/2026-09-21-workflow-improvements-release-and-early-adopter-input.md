# Input: Cut 0.2.14 Now, Then Invite The Adventurous

Sent: 2026-09-21

From: `workflow-improvements`, at the product owner's request, as input to two
questions the owner is weighing: whether to cut 0.2.14 now, and whether
0.2.14 makes a compelling case for pre-V1 adopters and contributors. Input,
not a decision; both calls are the owner's, and sequencing is yours.

## Question 1: Cut 0.2.14 Now

Recommendation: yes. The evidence, measured on `main` on 2026-09-21:

- 207 commits since `v0.2.12`, 59 merges, 52 changed files under
  `devcapsule-src/devcapsule`.
- **A user-facing fix v0.2.12 users need.** Upgrading to v0.2.12 broke
  configuration recovery (confirmed 2026-09-19). `maintenance`'s four
  commits of 2026-09-20 fix it and enforce the configuration contract from
  artifact admission through launch, closing the two bugs filed for it.
  Every day unreleased is a day that upgrade stays broken for anyone who
  took v0.2.12.
- **The workflow release**, everything under the 0.2.14 *Changes* entry,
  shipping to adopters through the packaged definition and the `devcapsule
  workflow` tool: releases, `maintenance`, bug frontmatter, `ws-` branches,
  the declaration and version, the local workflow file, the glossary, mail
  and published state on the coordination branch, the open-work directory,
  and the session-start synchronization judgment.
- Contained-display's follow-ups from the v0.2.12 period.

What not to wait for: the verifier, soft claims, *What Adopters Inherit*,
and the definition split change nothing a user runs; they ship in 0.2.15
with no loss.

What the release buys beyond content: it is the first release under the
rule written on 2026-09-16, cut from `main` after merging, one branch,
merge-then-tag, ancestry gate, and the first exercise of the version
machinery: `main` is at `0.2.14.dev0`, the release branch's first commit
sets `0.2.14`, and the bump script handles and tests that transition.

Readiness: no bug carries `severity: blocking`, but only because none has
been triaged. Seven sit at `fixed` awaiting validation; the candidate cycle
is where they get it. The two to look at before the cut are the ones
`maintenance` just fixed, since they are the headline.

**Who drives.** Under *Taking A Release Over*, the workstream whose
deliverable is the headline. The headline is the configuration fix, so
`maintenance` on `release-0.2.14`, with the workflow changes as content;
that also exercises the reserved workstream in the role it exists for. If
the owner prefers to call it a workflow release, `workflow-improvements`
drives instead. Both are within the rule; you decide only if it is unclear.

Two runbook items in your intake bear on this: the 2026-09-16 alignment of
the operator guide's step 1 with the release rule, and the 2026-09-18 note
that `maintenance` drives maintenance releases and that a mid-cycle owner
bump is accommodated. Neither blocks the cut; both should land in the guide
before the next one.

## Question 2: The Case For Pre-V1 Adopters And Contributors

Recommendation: yes, for one specific person, and stronger for contributors
than for adopters. Release first, then invite.

**Three claims a bleeding-edge developer can verify in an afternoon:**

1. Agents in YOLO mode without the `rm -rf $HOME` story: one executable, a
   Docker boundary, explicit opt-in for every host resource with the denial
   recorded.
2. Built with itself, transcript public: the recursive dogfood, the blog's
   autonomy entries, and a workflow where the human and several agents
   coordinate through git alone, no tracker, no service.
3. The workflow is the product too: multiple agents, multiple humans, one
   repository. For someone already running two or three agents on one
   codebase, that alone is worth a look, and 0.2.14 ships it as an
   installable, versioned component.

**Where the adventurous person's time gets wasted today:**

- Linux x86-64 only, WSL2 with notes, no macOS: half the audience gone
  before the first command.
- v0.2.12's broken upgrade recovery: do not invite anyone onto v0.2.12.
- The first-session guide pins v0.2.12 and needs refreshing with the
  release.
- Twenty open bugs with no severity, seven fixed and unvalidated: an adopter
  who hits one cannot tell whether it is known or whether it matters.
- Two IDE surfaces, three agents, a handful of ecosystems, honest but narrow,
  and "supported project types" appears in the README without a list beside
  it.

**Why contributors are the better bet.** The repository is unusually
legible: every decision has a record, every workstream a status file, every
bug a file, and an agent is productive on it in one session because the
workflow says what to read. There is no `CONTRIBUTING.md`; the developer
brief and the workflow do most of that job. The gap is a front door: one page
saying how a stranger picks a bug, works it with an agent inside DevCapsule,
and sends it back, which `maintenance` and the mail mechanism now make
literally true.

**Sequence proposed, cheapest first, after the release:**

1. Triage the open bugs so severity means something; an afternoon of the
   owner's, in the `maintenance` workstream.
2. Refresh the first-session guide to 0.2.14 and add the platform and
   ecosystem list beside the pitch. `user-docs` territory; paused.
3. Write the contributor front door, one page, pointing at the bug records
   and the `maintenance` workstream.
4. Say plainly in the README what this person gets. Proposed wording:
   "Linux, Docker, one executable, agents in YOLO mode behind a boundary,
   and the coordination workflow we use ourselves. Pre-V1: expect edges,
   and every edge has a file." True today, selects exactly the intended
   person, and turns the project's honesty into the reason to try it.

## What This Item Asks Of You

Nothing beyond taking it as input to the two decisions and, if the owner
proceeds, sequencing items 1 to 4 across `maintenance`, `user-docs`, and
whoever owns the README. `workflow-improvements` will take the workflow
half of any of them on request.
