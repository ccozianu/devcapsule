---
status: closed
severity: minor
target: none
owner: maintenance
opened: 2026-09-22
closed: 2026-09-22
requirements: []
---

# Codex commits omit human and agent attribution

## Evidence and expected behavior

The owner reported that Claude-assisted commits show co-authorship in GitHub,
while Codex-assisted commits do not. Commit `1c6d2c9`, merged by PR #125, has
author `PyCharm Docker User <costin@pop-os.localdomain>` and no co-author trailer.
Claude commit `90c52b3` has a `Co-Authored-By` trailer naming its model and agent.
The checkout's effective author and committer used the container placeholder;
the owner's GitHub merge commits use `Costin Cozianu <ccozianu@gmail.com>`.

The owner requires the human as primary author and the contributing Codex
model as co-author, with the actual model name first and `Codex` last.
This is an owner-adopted contributor convention, not a new product requirement.

## Fix and validation

Set this checkout's local `user.name` and `user.email` to the owner's identity
above. `git var GIT_AUTHOR_IDENT` and `GIT_COMMITTER_IDENT` both resolve correctly.
Added a durable rule to `WORKFLOW-LOCAL.md` requiring agent trailers, active-model
verification and preservation through squash merges. This session's recorded
model is `gpt-6-astra`; its trailer uses
`GPT-6 Astra Codex <noreply@openai.com>`. The address is a project attribution
convention. On 2026-09-22 the owner confirmed that the GitHub display shows
the expected attribution on the pushed fix. This is manual acceptance of the
desired display, not a separate assertion about account ownership.

[GitHub's multi-author documentation](https://docs.github.com/en/pull-requests/how-tos/commit-changes/creating-a-commit-with-multiple-authors)
defines the trailer format and account-email association. The current
[Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
did not establish a co-author configuration toggle; the repository instruction
sets the required commit behavior. No global hook attributes unrelated human
or other-agent commits to Codex. Existing merged commits are left intact.

## Closure and reopen criteria

Closed after the author and parsed trailer were verified on pushed commit
`1fbe6fa` and the owner confirmed the expected GitHub display on 2026-09-22.
The repository policy still awaits owner PR integration; this closure records
acceptance of the working fix, not an unverified mainline delivery.

Reopen if a future agent commit loses the trailer, uses another session's model
name, or inherits a placeholder author.
