# Review brief for the Codex + gpt-6-astra pair: PR265.1 on run deriving, reporting and asking

The first pair, Claude Fable 5.1 with the owner, has opened pull request 265 ("CLI UX redesign, PR3: run derives, reports and asks; the resolve step retired"), branch `ws-maintenance/cli-ux-3-run`, against `ws-maintenance/cli-ux-2-checkout`, slice 3 of the six-slice stack that implements the CLI UX redesign work order for 0.3.0 rc4. You reviewed slices 1 and 2 as #262 and #264, each accepted without a round. Same loop, topic 9.11 of `WORKFLOW.md`. Your job is one improvement pull request against PR 265's branch.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-review, on the branch `ws-maintenance/cli-ux-3-run-review`, branched from `ws-maintenance/cli-ux-3-run`. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex nor any `/home/devcapsule/worktrees/maintenance-cli-*` worktree.

Read first, in this order: `AGENTS.md`, `WORKFLOW.md` (topic 9.11), `WORKFLOW-LOCAL.md` (*Review Partners In This Checkout* and *GitHub Integration*), the work order `engineering-docs/work-orders/2026-10-24-cli-ux-redesign.md`, sections 3.1, 3.3, 3.4 and Part 5 answers 1, 4, 12, 14, 15, 17, 22 and 23, which this slice implements; then the module docstrings of `devcapsule/commands/_run_flow.py` (what run asks and when it exits 3) and `devcapsule/configuration/derivation.py` (registration and the derived plan); then `ProjectRunCommand` in `devcapsule/commands/project.py`, its `configure`, `_run` up to `prepare_display`, `_run_flags`, and the hidden `ConfigResolveCommand`; then the `Decision` dataclass in `devcapsule/configuration/listing.py`. D-0001 section 1 (`engineering-docs/decisions/product/d-0001-*.md`) is the consent grammar run follows; D-0012 the host-access rule. The maintenance status lists the six slices; slices 4 to 6 are not yours to anticipate: the consent model (workstation trust) and the console channel are untouched here on purpose.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists, with the source installed editable. Run unit tests and mypy from `devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex"`; create that directory first with `mkdir -p`. This PR touches: `devcapsule/commands/_run_flow.py` (new), `devcapsule/configuration/derivation.py` (new), `devcapsule/commands/project.py` (run, resolve, the hint lines, show), `devcapsule/configuration/listing.py` (decisions), `devcapsule/display_client.py`; tests `test_run_flow.py` (new) and the rewritten `tests/configuration/test_invariants.py`, `test_contract.py`, `test_software_approvals.py`, `test_upgrade_recovery.py`, `test_release_compatibility.py`, `test_project_commands.py`, `test_checkout_commands.py`, `test_listing.py`. The gate type-checks `tests/` too. Run `nox -s tests` and `mypy devcapsule tests` before your final push and report the counts; the test session takes about 80 seconds.

Do not build images and do not start capsules. The existing suites' fakes (`install_external_fakes`, patched `realize_environment` and `run_pycharm`) are how a launch is exercised; `--print-command` is the farthest a real probe goes.

## The task

Review the diff of PR 265 against its base:

    gh pr diff 265

Improve it on your branch, focused on exactly three things, in this order:

1. Correctness of the new and modified lines. Ask: is anything written before a blocking decision is answered, in every path, including `--save` with a pending consent, a second checkout, `--print-command`, and a terminal closed mid-question; does `register_checkout` ever reuse or shadow another checkout's record, and is the derived name stable across launches; does a run-once `--ide` or `--agent` leave the record untouched and still write a plan the launch can run, and what does the next `config show` say; is `--save` recorded exactly as the config family records, including `--env NAME` as a pass-through token; does an interactive "not now" on a recommended host access leave nothing recorded and the secure default effective, and does "once" reach the launch's host access without reaching the record; does a `renew` decision renew exactly the answer whose recommendation changed; does the base-without-contained-desktop consent stop before materialization, in `--print-command` too; does `prepare_launch` run again after an upgrade offer with the same flags minus `--save`, and can that second derivation ask anything; is the software-approval offer still first and never asked twice; are the carriers `--set` and `--authorize` mapped without losing a justification refusal; does `config resolve` as an alias write nothing when a decision is pending; what happens on a project whose manifest is schema 1 with the IDE inside `need`. Think about an agent running `run` in a script, and about a developer with two checkouts.
2. Clarity of the new and modified lines. The standard is "obviously no deficiencies". The prompts and the status-3 text are what the user reads first; the help of `run`.
3. Test coverage of the new and modified lines. Add tests where a branch is not exercised: `--save` with a pending consent, the derived checkout name on a collision, `renew` interactively and noninteractively, a run-once agent, the second derivation after an upgrade offer, the alias `resolve` with a pending decision writing nothing, a schema-1 project. Every test must fail if the line it covers is broken. Do not pad.

Stay inside the PR's scope: the launch's flow before materialization, registration, the derived plan, the retired resolve step. Do not change the consent model (workstation trust is slice 4), the listing's rows beyond their decisions, or the manifest's vocabulary. If you believe a contract is wrong, say why in the PR body and keep your change minimal.

## What you must not do

- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, the work order, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, to any `ws-maintenance/cli-ux-*` branch other than your review branch.
- Do not rebase or force-push. Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/cli-ux-3-run-review`, each message naming the component and the evidence, ending with your `Co-Authored-By:` line in the form `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as.
2. Push the branch and open one pull request with
   `gh pr create --base ws-maintenance/cli-ux-3-run --head ws-maintenance/cli-ux-3-run-review`.
   Title: "Correctness, clarity and coverage review of #265 (PR265.1)".
   The body lists each finding as: what was wrong or unclear, where, what you changed, how the test proves it. Separate "changed" from "considered and left alone, because". List the proposals you did not implement. State the gate result with counts and what was skipped. If you find nothing to change, say so in the PR body and open the PR with the added tests only, or, if there are none, say that in your final report instead of opening an empty PR.
3. Print the PR URL as the last line of your output, or "NO PR" if you opened none.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice. Every claim about behavior must be backed by a test or a command you ran.

If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
