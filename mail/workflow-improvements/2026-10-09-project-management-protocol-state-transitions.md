# Review the protocol layer above git for safe transitions between consistent states

Sent: 2026-10-09

From: `project-management`, to `workflow-improvements`. Owner request taken
in this checkout on 2026-10-09 after two transient failures and one
interruption during a workstream switch; the owner asked for a review item.

## What is handed over

The coordination tooling has two layers. The git layer is failsafe: every
write to `coordination` is a compare-and-swap push (`--force-with-lease`
against the fetched tip), a lost race is refetched and retried, and other
push failures raise. The owner's finding is that the layer above it,
the commands that move the project between consistent states, has not
been reviewed as a set of transitions. Each command performs several steps
across two or three stores (the coordination branch, the working tree and
index, and GitHub), and the question for each is: what are its intermediate
states, is each one recoverable, and does a second run from each one
converge?

Commands in scope, in `devcapsule/workflow_coordination.py` and
`devcapsule/commands/workflow.py`: `mail take`, `mail send`, `publish`,
`claim` and its release, and, at the next layer up, the pull-request steps
agents run with `gh` under *Successful Completion*.

## Evidence from 2026-10-09

- `mail take` was interrupted at the harness level: the agent's tool call
  was reported rejected while the process ran to completion. Ten items were
  on disk and staged and the removal commit was on `coordination`; a second
  take reported no mail. This is the designed outcome: local copies are
  written and staged before the branch is touched, a differing existing copy
  is refused, and a failed push leaves the mail in place (`take`, lines
  208–257). The property is good; it is proved by reading, not by a test.
- The GitHub API was unreachable for about ten seconds (`no route to host`).
  `gh` failed immediately; the agent's shell loop retried. Nothing in the
  tooling retries a connection-class failure: `_push` retries only a lease
  rejection and raises on anything else, and `_fetch_tip` does not retry.
  An agent that took the first failure as final would have stopped, or
  assumed a pull request absent and opened a duplicate.
- `publish` pushes to `coordination` first and then rewrites the
  `Definition read:` stamp in the working tree. A failure between the two
  leaves the published copy ahead of the committed one; the next publish
  converges, but no test covers that window.

## What accepting means

1. For each command above, write the transition diagram: stores touched,
   order of writes, the state after each step, and the recovery from each
   state (idempotent rerun, explicit recover, or refusal with the evidence
   preserved). Record it beside the merge-strategy note under
   `engineering-docs/implementation-notes/workflow/`.
2. Add tests that interrupt each command between steps (a failing push
   after the local write, a failing local write after the push) and assert
   convergence on rerun. The claim-expiry flake shows the clock-dependent
   path is the least covered.
3. Add a bounded backoff for connection-class failures in `_fetch_tip` and
   `_push`, distinct from the lease-rejection retry, and state the bound in
   the command's output when it gives up.
4. Add to `AGENTS.md`, under the reporting contract: a tool call reported
   interrupted or rejected has an unknown outcome; the agent re-observes
   state before acting again rather than assuming the command did not run.
5. Decide whether the `gh` steps of *Successful Completion* get the same
   treatment (check for an existing pull request before creating one;
   retry the API once) or whether that stays the agent's responsibility.

## Why it belongs to you

The commands are the packaged definition's tooling and the rules they
implement are the definition's; the sender has no implementation remit.
