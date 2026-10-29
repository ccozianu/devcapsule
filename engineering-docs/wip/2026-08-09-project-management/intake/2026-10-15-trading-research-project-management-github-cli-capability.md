# Capability request: a signed-in GitHub CLI in the capsule

Sent: 2026-10-15

From: the `project-management` workstream of the trading-research
project (`github.com/ccozianu/devcapsule-sample-trading-research`), to
`project-management` of the DevCapsule repository, at the owner's
request, by the same cross-repository route your `maintenance`
workstream used on 2026-10-12. This is input, not an assignment.

## What is handed over

A request for a capsule capability, in the sense of the manifest's
`[capabilities] need` list: a GitHub CLI (`gh`) installed in the image and
signed in through the owner's GitHub account the way the agent clients
are, so that an implementor agent can open pull requests, post the
per-round assessment comments, merge a reviewer's stacked pull request
into the slice branch, and read review comments, without the owner
pasting bodies by hand. A name such as `github-cli` beside
`claude-code-agent`, `codex-agent` and `antigravity-agent` would fit the
existing list.

## Why it belongs to this workstream

DevCapsule's `project-management` owns what the product does and in what
order; a new capability is a backlog entry or a requirement, which is its
to open. The sender assigns no priority and no release target.

## Evidence

The process record of 2026-10-12 proposed an implementor pair, a reviewer
pair and the owner, with pull requests carrying every step. The
trading-research project adopted it on 2026-10-14 as its delivery rule
(*Delivery And Review* in its `WORKFLOW-LOCAL.md`) and ran it twice the
same week, for three slices of a command-line-client engine route:

- Round 1 and 2 of slice 1, and round 3 of slices 2 and 3: a Codex
  reviewer pair in its own worktree, briefs written by the implementor,
  review branches stacked on the slice branch, merge commits, assessment
  records, 98 tests at the end. Records:
  `engineering-docs/wip/2026-10-13-cli-engines/2026-10-14-record-review-round-1.md`,
  `…-round-2.md`, `2026-10-15-record-review-round-3.md`.
- What the loop could not do in the capsule: open the pull request for
  either slice, post the assessment as a pull-request comment, or merge
  the review pull request through the hosting platform. `gh` is not in
  the image and no token is present; `apt` has no `gh` package in the
  image's sources. The implementor wrote the pull-request bodies into
  notes (`2026-10-14-note-pull-request-body.md`,
  `2026-10-15-note-pull-request-body-clients.md`) and handed the owner
  three manual steps: open two pull requests, retarget one after the
  first merges, merge both. The assessment comments the process record
  calls for exist only as repository records.
- The sign-in question is the same one the agent clients already solve:
  the capsule carries the owner's claude.ai, ChatGPT and Google sign-ins
  as ambient state; a `gh auth login` done once by the owner would be the
  fourth.

Two related observations from the same week, offered in case they belong
to the same capability work; each would be its own item if wanted:

- Codex's own sandbox needs Linux user namespaces (`bwrap` refuses to
  create one in the capsule), so the reviewer pair ran with
  `--dangerously-bypass-approvals-and-sandbox`, the capsule being the
  sandbox. A capsule-level statement of which agent sandboxes work inside
  it would save every adopter the same discovery.
- Codex reads `AGENTS.md` from its home directory whatever its
  instruction and config switches say; the only isolation that held was
  a private `CODEX_HOME` with a symlink to `auth.json`. Relevant to any
  capsule that runs agents as engines rather than as developers.

## What accepting this means

DevCapsule records it as input to its capability roster, with no
obligation beyond the record. If a `github-cli` capability ships, the
trading-research project adds it to its manifest's `need` list and
records the sign-in under *Host Capabilities* in its local workflow file.
