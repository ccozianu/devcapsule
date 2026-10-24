# Review brief for the Codex + gpt-6-astra pair: PR268.1 on the console's configuration channel

The first pair, Claude Fable 5.1 with the owner, has opened pull request 268 ("CLI UX redesign, PR5: the console writes through the launcher; the listing at launch inside the capsule"), branch `ws-maintenance/cli-ux-5-console`, against `ws-maintenance/cli-ux-4-trust`, slice 5 of the six-slice stack that implements the CLI UX redesign work order for 0.3.0 rc4. You reviewed slices 1 to 4 before. Same loop, topic 9.11 of `WORKFLOW.md`. Your job is one improvement pull request against PR 268's branch.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-review, on the branch `ws-maintenance/cli-ux-5-console-review`, branched from `ws-maintenance/cli-ux-5-console`. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex nor any `/home/devcapsule/worktrees/maintenance-cli-*` worktree.

Read first, in this order: `AGENTS.md`, `WORKFLOW.md` (topic 9.11), `WORKFLOW-LOCAL.md` (*Review Partners In This Checkout* and *GitHub Integration*), the work order `engineering-docs/work-orders/2026-10-24-cli-ux-redesign.md`, section 3.5 and Part 5 answers 7 and 16, which this slice implements; D-0010 (runtime introspection is read-only) and D-0012 under `engineering-docs/decisions/product/`; then the module docstrings of `devcapsule/configuration/console_channel.py` (the contract and the classification), `devcapsule/configuration/console_requests.py` (the deferred store), `devcapsule/commands/_console_channel.py` (the watcher, the child process, the results); `channel_watcher`, `prepare_temp_runtime_files` and `cleanup_temp_runtime_files` in `devcapsule/launch/pycharm/_launcher.py`; `_show_inside_capsule` and the `ConfigConsole*` commands in `devcapsule/commands/project.py`; the `console` branch of `_settle` in `devcapsule/commands/_run_flow.py`; then, on the console's side, `devcapsule-webconsole/CONFIGURATION-CHANNEL.md`, `devcapsule_webconsole/configuration.py`, the three routes in `app.py`, and the `configuration` page of `static/console.js`. The maintenance status lists the six slices; slice 6 (removals, documentation, changelog) is not yours to anticipate.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists, with the source installed editable. Run the launcher's unit tests and mypy from `devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex"`; create that directory first with `mkdir -p`. The console's checks run from `devcapsule-src` as `.venv/bin/python -m nox -s webconsole` (its own environment, pytest and mypy). Run `nox -s tests`, `mypy devcapsule tests` and `nox -s webconsole` before your final push and report the counts.

Do not build images and do not start capsules. The channel is exercised through directories: `tests/test_console_channel.py` writes requests and reads results; the launcher's mount test (`test_launcher_mounts_live_configuration_directory_and_private_snapshot_read_only` in `tests/test_pycharm.py`) checks the directory, its mount and the listing; the console's `tests/test_configuration_channel.py` drives the routes through the test client.

## The task

Review the diff of PR 268 against its base:

    gh pr diff 268

Improve it on your branch, focused on exactly three things, in this order:

1. Correctness of the new and modified lines. Ask: is every file in the channel complete when visible, on both sides, and is a partial or planted file (a symbolic link, a FIFO, a huge file, a name outside the contract) harmless to the launcher's watcher and to the console's reader; can two requests share a name, and what happens when the console restarts mid-run and starts numbering again; does the watcher's child process inherit anything it should not (the environment, the terminal), can it block the launcher's exit, and what happens to a request written in the last second before the capsule stops; is the classification complete and right: name a verb or sub-verb that widens what the next launch reaches and is applied at once, or one that only narrows and is deferred; does a deferred request survive `config forget`, a re-registration of the checkout, a second checkout of the same project, and does `console apply` run exactly the recorded tokens; is the in-capsule `config show` truthful when the channel directory exists but the listing does not, or the listing is from another checkout; does the launch listing written at launch include the run-once IDE or agent of that launch, and the console's own earlier deferred requests; can the console's `POST` be reached from another origin, from a page without the token, or with a body that is valid JSON but not a request; what does the page do when the channel is absent (an older launcher) or when the launcher never answers. Think about an agent inside the capsule that wants `docker-daemon host-socket` at the next launch.
2. Clarity of the new and modified lines. The standard is "obviously no deficiencies". The result texts and the page's notice are what the user reads first; `CONFIGURATION-CHANNEL.md` is the contract both sides must be readable against.
3. Test coverage of the new and modified lines. Add tests where a branch is not exercised: the watcher's stop with a request pending, a symbolic link or FIFO as a request, a result the console cannot read, the second checkout's deferred store, the page's refusal paths. Every test must fail if the line it covers is broken. Do not pad.

Stay inside the PR's scope: the channel, the watcher, the deferred requests, the in-capsule listing, the console's routes and page. Do not change the trust model of slice 4, the run flow beyond the console decision, or the manifest. If you believe the boundary (widenings deferred to the host) is wrong, say why in the PR body and keep your change minimal; the owner decides it.

## What you must not do

- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, the work order, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, to any `ws-maintenance/cli-ux-*` branch other than your review branch.
- Do not rebase or force-push. Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/cli-ux-5-console-review`, each message naming the component and the evidence, ending with your `Co-Authored-By:` line in the form `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as.
2. Push the branch and open one pull request with
   `gh pr create --base ws-maintenance/cli-ux-5-console --head ws-maintenance/cli-ux-5-console-review`.
   Title: "Correctness, clarity and coverage review of #268 (PR268.1)".
   The body lists each finding as: what was wrong or unclear, where, what you changed, how the test proves it. Separate "changed" from "considered and left alone, because". List the proposals you did not implement. State the gate results with counts and what was skipped. If you find nothing to change, say so in the PR body and open the PR with the added tests only, or, if there are none, say that in your final report instead of opening an empty PR.
3. Print the PR URL as the last line of your output, or "NO PR" if you opened none.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice. Every claim about behavior must be backed by a test or a command you ran.

If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
