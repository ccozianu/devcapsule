# Review brief for the Codex + gpt-6-astra pair: PR263.1 on the checkout's verbs and the truthful listing

The first pair, Claude Fable 5.1 with the owner, has opened pull request 263 ("CLI UX redesign, PR2: the checkout's verbs, launcher-owned memory and cpus, the truthful listing, exit 3"), branch `ws-maintenance/cli-ux-2-checkout`, against `ws-maintenance/cli-ux-1-manifest`, slice 2 of the six-slice stack that implements the CLI UX redesign work order for 0.3.0 rc4. You reviewed slice 1 as #262, accepted without a round. Same loop, topic 9.11 of `WORKFLOW.md`. Your job is one improvement pull request against PR 263's branch.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-review, on the branch `ws-maintenance/cli-ux-2-checkout-review`, branched from `ws-maintenance/cli-ux-2-checkout`. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex, nor /home/devcapsule/worktrees/maintenance-cli-1, nor /home/devcapsule/worktrees/maintenance-cli-2.

Read first, in this order: `AGENTS.md`, `WORKFLOW.md` (topic 9.11), `WORKFLOW-LOCAL.md` (*Review Partners In This Checkout* and *GitHub Integration*), the work order `engineering-docs/work-orders/2026-10-24-cli-ux-redesign.md`, sections 3.2, 3.4, 3.7 and Part 5 answers 6, 12, 13, 20, 22 and 24, which this slice implements; then the module docstrings of `devcapsule/configuration/listing.py` (the listing's contract: rows, sources, pending, no writes), `devcapsule/configuration/launcher_values.py` (memory and cpus and the precedence), `devcapsule/configuration/workstation.py`; then in `devcapsule/commands/project.py` the `CheckoutDocuments` dataclass with `_load_checkout_documents` and `_assess`, `_set_value`, the `env` and `docker-args` groups, `_hidden_alias`, and `ConfigCheckCommand`. `DecisionPending` is in `devcapsule/compat.py` and mapped to exit status 3 in `devcapsule/cli.py`. The maintenance status, `engineering-docs/wip/2026-09-18-maintenance/CURRENT-STATUS.md`, section "The CLI UX redesign in rc4", lists the six slices; slices 3 to 6 are not yours to anticipate: `project run` and `config resolve` are untouched here on purpose.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists, with the source installed editable. Run unit tests and mypy from `devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex"`; create that directory first with `mkdir -p`. This PR touches: `devcapsule/configuration/listing.py` (new), `launcher_values.py` (new), `workstation.py` (new), `values.py`, `review.py`, `model.py`, `resolution.py`, `fingerprints.py`, `freshness.py`, `execution.py`, `storage.py` (the workstation file), `docker_arguments.py` (pass-through variables), `devcapsule/commands/project.py` (the listing and every checkout verb), `devcapsule/compat.py`, `devcapsule/cli.py`, `devcapsule/launch/pycharm/_launcher.py` (`--cpus`), `environment_realization.py`, `version_sets.py`; tests `test_listing.py` (new), `test_checkout_commands.py` (new), and the rewritten `test_project_commands.py`, `tests/configuration/test_contract.py`, `test_checkout_environment.py`, `test_saved_docker_arguments.py`, `test_cli.py`. The gate type-checks `tests/` too. Run `nox -s tests` and `mypy devcapsule tests` before your final push and report the counts; the test session takes about 80 seconds.

Do not build images and do not start capsules. `--print-command` is the farthest a launch probe goes.

## The task

Review the diff of PR 263 against its base:

    gh pr diff 263

Improve it on your branch, focused on exactly three things, in this order:

1. Correctness of the new and modified lines. Ask: does `config show` write nothing in every state, unregistered, registered without an IDE, with a stale resolution, inside a capsule; does `config check` exit 3 exactly when a row is pending and 0 otherwise, and does its `--json` still carry the contract line; is every row's EFFECTIVE the value the next launch would use, in particular `memory` and `cpus` under each precedence, the alias of a legacy `runtime.memory-limit` declaration (its recommendation, a recorded answer under the old name, `required = true` on it), host access when the project recommends and the answer is unanswered, denied, stale or invalid, host-x11 on a base before recipe 8; does `set NAME default` forget exactly the checkout's answer and nothing else, and does `set` of an alias name refuse with the right remedy; does `env set --from-host` write `--env NAME` and never a value, does `env list` never print a value, and what does `redact_environment` do with a pass-through token; does `docker-args set` still refuse every launcher-owned spelling including the new `--cpus` ones and the attached short forms; do the hidden aliases behave exactly as the new verbs, including their capsule-access declaration and their exit statuses; does `deny` refuse the base and the vendor downloads, and `forget` of an answer that was never given; does `ide` of a component id (`codium`) record the capability name; can `agent add` or `tool omit` write when the project is in the legacy `need` form with the IDE inside; is the workstation file validated on read and refused when malformed, and what happens to `config show` then; does the resolution's `workstation-config` digest stay `absent` for a plan written before this slice so an older plan is still fresh when no default is set, and does a changed default stale the plan; does run-once `--set cpus` reach Docker. Think about a developer with two checkouts of one project, and about an agent running `config check` in a script.
2. Clarity of the new and modified lines. The standard is "obviously no deficiencies". The listing's words are what the user reads first: every SOURCE and PENDING string, and the help texts of `show`, `check`, `set`, `default`, `env`, `docker-args`, `deny`, `forget`.
3. Test coverage of the new and modified lines. Add tests where a branch is not exercised: the listing inside a capsule (`RuntimeConfiguration`), a malformed workstation file, the stale-plan digest with and without defaults, `redact_environment` with a pass-through token, the `--cpus` argument in the launcher's Docker command, each hidden alias's exit status, `deny` on a required consent. Every test must fail if the line it covers is broken. Do not pad.

Stay inside the PR's scope: the checkout's verbs, the launcher-owned values, the listing, the pending exit status. Do not change `project run`'s flow, the resolve step, the consent model (slice 4) or the manifest's vocabulary (slice 1). If you believe a contract is wrong, say why in the PR body and keep your change minimal.

## What you must not do

- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, the work order, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, to `ws-maintenance/cli-ux-0-work-order`, to `ws-maintenance/cli-ux-1-manifest`, or to any branch other than your review branch.
- Do not rebase or force-push. Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/cli-ux-2-checkout-review`, each message naming the component and the evidence, ending with your `Co-Authored-By:` line in the form `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as.
2. Push the branch and open one pull request with
   `gh pr create --base ws-maintenance/cli-ux-2-checkout --head ws-maintenance/cli-ux-2-checkout-review`.
   Title: "Correctness, clarity and coverage review of #263 (PR263.1)".
   The body lists each finding as: what was wrong or unclear, where, what you changed, how the test proves it. Separate "changed" from "considered and left alone, because". List the proposals you did not implement. State the gate result with counts and what was skipped. If you find nothing to change, say so in the PR body and open the PR with the added tests only, or, if there are none, say that in your final report instead of opening an empty PR.
3. Print the PR URL as the last line of your output, or "NO PR" if you opened none.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice. Every claim about behavior must be backed by a test or a command you ran.

If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
