# Review brief for the Codex + gpt-6-astra pair: PR240.1 on the universal network node

Same collaboration as the session-logs and log-rotation reviews of October 2026 (#208, #210, #211, #212), all merged. The first pair, Claude Fable 5.1 with the owner, has opened pull request 240 ("Authorization: network is a host capability node on every project"), branch `ws-maintenance/0.3.0-network-node`, against `release-0.3.0`, the active release branch of the 0.3.0 cycle. Your job is one improvement pull request against that branch.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-review, on the branch `ws-maintenance/0.3.0-network-node-review`, branched from `ws-maintenance/0.3.0-network-node`. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex.

Read first, in this order: `AGENTS.md`, `WORKFLOW.md` (topic 9.11 is the loop you are in), `WORKFLOW-LOCAL.md` (*Review Partners In This Checkout* and *GitHub Integration*), the bug record `engineering-docs/bugs/devcapsule/2026-10-05-run-once-network-authorization-needs-a-recommendation.md`, whose *Fix, 2026-10-22* section says what this PR does and why, and the module `devcapsule/configuration/authorization.py`, whose tables are the contract.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists. Run unit tests and mypy from `devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex"`; create that directory first with `mkdir -p`. This PR touches: `devcapsule/configuration/authorization.py` (one table entry and its comment), `tests/test_project_commands.py` (one new test, one assertion in the run-once refusal test), `README.md` of `devcapsule-src`, two documentation rows under `docs/`, and two records under `engineering-docs/`. The gate type-checks `tests/` too. Run `nox -s build` before your final push and report its result with counts; it takes about fifteen minutes.

Do not build images and do not start capsules. The IDE smoke that launches a fresh project with the documented command is the first pair's acceptance step on the candidate.

## The task

Review the diff of PR 240 against its base:

    gh pr diff 240

Read `WORKSTATION_CAPABILITY_DEFAULTS` and `authorization_declarations` in `devcapsule/configuration/authorization.py` first: a node exists on every project when it is in that table; a project recommendation under `CURATED_HOST_RECOMMENDATIONS` takes precedence and attaches a justification; `AUTHORIZATION_DENY_VALUES` gives `network` its deny value `bridge`.

Improve it on your branch, focused on exactly three things, in this order:

1. Correctness of the new and modified lines. Ask: does every reader of the node set treat `network` like `docker-daemon` now, the review overlay in `devcapsule/configuration/review.py`, the resolution's `host_access` in `devcapsule/configuration/resolution.py`, the run-once path `_run_once_answers` in `devcapsule/commands/project.py`, `config list`, `config authorize`, `config unset`, `--all-recommended`, and `project init`'s elicitation, which must keep asking only the curated questions and never author a recommendation from the workstation default? Does a project that adds a network recommendation later stale a workstation-default answer, as the digest comment promises, and does removing the recommendation stale it back? Does the recursive successor (`devcapsule/recursive_successor.py`, the `authorization.get("network")` read) see the same value? Is any existing test now asserting an absence that no longer holds? Think about what the new description tells a developer who has never read the docs, and whether the deny value is named wherever a refusal mentions it.
2. Clarity of the new and modified lines. The standard is "obviously no deficiencies".
3. Test coverage of the new and modified lines. Add tests where a branch is not exercised: the stale transition when a recommendation appears, the listing's status and source for an unanswered workstation-default `network`, the `unset` path. Every test must fail if the line it covers is broken. Do not pad.

Stay inside the PR's scope: the `network` node's existence on every project and what follows from it. Do not change the run-once family, the recommendation grammar, the other nodes, or the launch. Do not widen the authorization contract; if you believe it is wrong, say why in the PR body and keep your change minimal.

## What you must not do

- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, or to any branch other than your review branch.
- Do not rebase or force-push. Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/0.3.0-network-node-review`, each message naming the component and the evidence, ending with your `Co-Authored-By:` line in the form `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as.
2. Push the branch and open one pull request with
   `gh pr create --base ws-maintenance/0.3.0-network-node --head ws-maintenance/0.3.0-network-node-review`.
   Title: "Correctness, clarity and coverage review of #240 (PR240.1)".
   The body lists each finding as: what was wrong or unclear, where, what you changed, how the test proves it. Separate "changed" from "considered and left alone, because". List the proposals you did not implement. State the gate result with counts and what was skipped. If you find nothing to change, say so in the PR body and open the PR with the added tests only, or, if there are none, say that in your final report instead of opening an empty PR.
3. Print the PR URL as the last line of your output, or "NO PR" if you opened none.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice. Every claim about behavior must be backed by a test or a command you ran.

If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
