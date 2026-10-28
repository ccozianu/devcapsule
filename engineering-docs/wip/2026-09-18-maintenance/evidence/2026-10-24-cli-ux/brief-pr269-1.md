# Review brief for the Codex + gpt-6-astra pair: PR269.1 on the documentation and the removals

The first pair, Claude Fable 5.1 with the owner, has opened pull request 269 ("CLI UX redesign, PR6: what goes away, the user pages, the command reference, the candidate-4 changelog"), branch `ws-maintenance/cli-ux-6-docs`, against `ws-maintenance/cli-ux-5-console`, slice 6, the last, of the stack that implements the CLI UX redesign work order for 0.3.0 rc4. Same loop, topic 9.11 of `WORKFLOW.md`. Your job is one improvement pull request against PR 269's branch.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-review, on the branch `ws-maintenance/cli-ux-6-docs-review`, branched from `ws-maintenance/cli-ux-6-docs`. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex nor any `/home/devcapsule/worktrees/maintenance-cli-*` worktree.

Read first: `AGENTS.md`, `WORKFLOW.md` (topic 9.11), `WORKFLOW-LOCAL.md` (*Review Partners In This Checkout* and *GitHub Integration*), the work order `engineering-docs/work-orders/2026-10-24-cli-ux-redesign.md`, Part 3 (the user's view), Part 4 (what goes away) and the owner's answers in Part 5; then the diff. The pages are read by adopters, so the owner's documentation rule applies: visitor-first, one fact per sentence, commands exactly as the executable accepts them.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists, with the source installed editable. The documentation's check is the website's content contract: from `/workspace/301e4208ef81-ChatGPT_Codex/website` (the pinned website with its `node_modules`; read it, do not edit it), run `CONTENT_DIR=/home/devcapsule/worktrees/maintenance-review npm run check:content`. Every command a page names must be one the executable accepts: verify each with `devcapsule-src/.venv/bin/devcapsule project ... --help` and, where a page shows output, by running the command on a throwaway project under `/opt/devcapsule-gate/pytest-codex` with `XDG_CONFIG_HOME` set there. Do not build images and do not start capsules.

## The task

Review the diff of PR 269 against its base:

    gh pr diff 269

Improve it on your branch, focused on exactly three things, in this order:

1. Correctness of every page against the executable on the branch: each command, flag, value and output line the pages show; each claim about what is recorded where, what asks and what writes; the precedence of memory and cpus; what an acceptance covers; what the console can and cannot change; the retired spellings and what each answers now. Run the commands. A page that promises something the launcher does not do is the finding that matters most.
2. Completeness against the work order's Part 3 and Part 4: name any user-facing behavior of slices 1 to 5 that no page documents, and any Part 4 removal the pages still contradict. The reference page `docs/reference/cli.md` should let a reader find every command.
3. Clarity: the standard is "obviously no deficiencies"; a sentence an adopter would have to read twice is a finding.

Stay inside the PR's scope: the pages, the reference, the changelog section. Do not change code; if a page can only be made true by a code change, say so in the PR body with the page and the line, and leave the page saying what the launcher does today.

## What you must not do

- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, the work order, or run `devcapsule workflow publish`.
- Do not commit the `website` submodule pointer, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, to any `ws-maintenance/cli-ux-*` branch other than your review branch.
- Do not rebase or force-push. Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/cli-ux-6-docs-review`, each message naming the page and the evidence, ending with your `Co-Authored-By:` line in the form `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as.
2. Push the branch and open one pull request with
   `gh pr create --base ws-maintenance/cli-ux-6-docs --head ws-maintenance/cli-ux-6-docs-review`.
   Title: "Correctness, completeness and clarity review of #269 (PR269.1)".
   The body lists each finding as: what was wrong or missing, which page and line, what you changed, how you verified it. Separate "changed" from "considered and left alone, because". List the code changes you believe a page needs. State the content check's result.
3. Print the PR URL as the last line of your output, or "NO PR" if you opened none.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice.

If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
