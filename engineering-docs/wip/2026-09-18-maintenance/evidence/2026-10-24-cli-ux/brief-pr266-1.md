# Review brief for the Codex + gpt-6-astra pair: PR266.1 on workstation trust and host access

The first pair, Claude Fable 5.1 with the owner, has opened pull request 266 ("CLI UX redesign, PR4: workstation trust, one acceptance per channel; host answers kept"), branch `ws-maintenance/cli-ux-4-trust`, against `ws-maintenance/cli-ux-3-run`, slice 4 of the six-slice stack that implements the CLI UX redesign work order for 0.3.0 rc4. You reviewed slices 1 and 2 as #262 and #264, each accepted without a round, and slice 3 as PR265.1. Same loop, topic 9.11 of `WORKFLOW.md`. Your job is one improvement pull request against PR 266's branch.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-review, on the branch `ws-maintenance/cli-ux-4-trust-review`, branched from `ws-maintenance/cli-ux-4-trust`. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex nor any `/home/devcapsule/worktrees/maintenance-cli-*` worktree.

Read first, in this order: `AGENTS.md`, `WORKFLOW.md` (topic 9.11), `WORKFLOW-LOCAL.md` (*Review Partners In This Checkout* and *GitHub Integration*), the work order `engineering-docs/work-orders/2026-10-24-cli-ux-redesign.md`, section 3.2 and Part 5 answers 3, 4, 21 and 23, which this slice implements; the decisions D-0011 and D-0012 under `engineering-docs/decisions/product/`; then the module docstring of `devcapsule/configuration/trust.py` (what a channel is, what the record covers), `review_authorizations` and `_trusted_channel` in `devcapsule/configuration/authorization.py`, `_access_rows` in `devcapsule/configuration/listing.py`, the `trust` branch of `_settle` and `accept_channel` in `devcapsule/commands/_run_flow.py`, and the `ConfigTrust*` commands in `devcapsule/commands/project.py`. The maintenance status lists the six slices; slices 5 and 6 are not yours to anticipate: the console channel and the documentation are untouched here on purpose.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists, with the source installed editable. Run unit tests and mypy from `devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex"`; create that directory first with `mkdir -p`. This PR touches: `devcapsule/configuration/trust.py` (new), `authorization.py`, `listing.py`, `storage.py`, `derivation.py`, `resolution.py`, `review.py`, `approvals.py`, `devcapsule/commands/_run_flow.py`, `_software_approvals.py`, `project.py`, `devcapsule/environment_realization.py`; tests `test_trust.py` (new), `test_run_flow.py`, `test_software_approvals.py`, `test_listing.py`, `test_upgrade_recovery.py`, `test_project_commands.py`, `tests/configuration/test_adt.py`, `test_contract.py`, `test_architecture.py`. The gate type-checks `tests/` too. Run `nox -s tests` and `mypy devcapsule tests` before your final push and report the counts; the test session takes about 80 seconds.

Do not build images and do not start capsules. The existing suites' fakes are how a launch is exercised; `--print-command` is the farthest a real probe goes.

## The task

Review the diff of PR 266 against its base:

    gh pr diff 266

Improve it on your branch, focused on exactly three things, in this order:

1. Correctness of the new and modified lines. Ask: what exactly does one acceptance cover, and is that what the prompt says; can a lock, by naming an origin or a terms URL, widen what the user accepted without a new question, and can it narrow it so the user is asked again needlessly; is a base outside DevCapsule's repository, a local image override, and a per-checkout denial each handled as the docstring says; does the trusted status reach every reader of the review: the listing, `config check`, the derived plan, the resolution file, the environment realization and the software-approval offer, with no path still reading the per-checkout consent alone; what does a schema-1 or rc3 launcher do with a checkout that has no per-checkout consent because this launcher trusted the channel; is `trust.toml` written atomically and never by a read-only command; what does `--trust` write when another decision is still pending, and is the status-3 text truthful about it; does a superseded host answer stay effective and never ask, and does the listing say what changed; are acquisitions whose version moved still the software-approval question when the vendor is not trusted, and never when it is; what does `trust withdraw` do to a running capsule's plan and to the next launch; can a channel id collide with a component id in a way that confuses `accept`. Think about a developer with three projects on one laptop, and about a laptop shared through one user account.
2. Clarity of the new and modified lines. The standard is "obviously no deficiencies". The acceptance statement and the `trust list` output are what the user reads first.
3. Test coverage of the new and modified lines. Add tests where a branch is not exercised: a lock whose artifact origins change after acceptance, a foreign base, a local image override with a trusted channel, the resolution and the realization reading the trust, the superseded host answer end to end, a corrupt `trust.toml`. Every test must fail if the line it covers is broken. Do not pad.

Stay inside the PR's scope: the trust record, the review's reading of it, the listing's and the launch's trust question, the three commands. Do not change the manifest's vocabulary, the checkout verbs of slice 2 or the run flow beyond the trust decision. If you believe a contract is wrong, say why in the PR body and keep your change minimal.

## What you must not do

- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, the work order, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, to any `ws-maintenance/cli-ux-*` branch other than your review branch.
- Do not rebase or force-push. Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/cli-ux-4-trust-review`, each message naming the component and the evidence, ending with your `Co-Authored-By:` line in the form `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as.
2. Push the branch and open one pull request with
   `gh pr create --base ws-maintenance/cli-ux-4-trust --head ws-maintenance/cli-ux-4-trust-review`.
   Title: "Correctness, clarity and coverage review of #266 (PR266.1)".
   The body lists each finding as: what was wrong or unclear, where, what you changed, how the test proves it. Separate "changed" from "considered and left alone, because". List the proposals you did not implement. State the gate result with counts and what was skipped. If you find nothing to change, say so in the PR body and open the PR with the added tests only, or, if there are none, say that in your final report instead of opening an empty PR.
3. Print the PR URL as the last line of your output, or "NO PR" if you opened none.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice. Every claim about behavior must be backed by a test or a command you ran.

If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
