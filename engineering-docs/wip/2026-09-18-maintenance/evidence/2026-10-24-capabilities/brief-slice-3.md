# Implementation brief for the Codex + gpt-6-astra pair: slice 3 of the capabilities and components work order

Same loop as slices 1 and 2: you implement; Claude Fable 5.1 reviews, with the owner, Costin Cozianu, who merges. The work order is `engineering-docs/work-orders/2026-10-24-capabilities-and-components.md`; its Part 1 rulings and Part 5 decisions are settled, with the two corrections recorded in it during slice 2 (the resolution table under `[capabilities.resolution]`; a resolution recommendation takes no reason). Slice 1 is PR #276, slice 2 is PR #277, both accepted after one round; this slice stacks on slice 2. Where the order is silent, choose the smallest thing and say what you chose in the PR body. Do not reopen the model.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-impl-3, on the branch `ws-maintenance/capabilities-3-docs`, branched from `ws-maintenance/capabilities-2-commands` at its accepted tip. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex except as the documentation check below says, nor any other `/home/devcapsule/worktrees/*` worktree.

Read first: the work order, Part 3, Part 4 and Part 5 items 1, 2, 6, 7 and 10; the current pages `docs/configuration/capabilities.md`, `docs/configuration/project-versus-personal.md`, `docs/configuration/software-approvals.md`, `docs/reference/cli.md` (the command tree and its *Retired spellings* table), `docs/reference/configuration-nodes.md`, `docs/README.md`; the changelog `engineering-docs/releases/v0.3.0/changelog.md` (*New in candidate 4*); `commands/project.py` for every retired spelling and hidden alias, with the rc4 pattern of a hidden command that prints a replacement; `tests/` for the tests that drive those spellings (`grep -rn "capabilities\", \"--local\|agent\", \"add\|tool\", \"omit\|--agent\|require\", \"tool\|set-env\|set-extra-docker-args\|config need\|--sdk-major" tests/`).

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists with the source installed editable. Create `/opt/devcapsule-gate/pytest-codex-impl-3` with `mkdir -p` and run every pytest and nox invocation from `devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex-impl-3"`. The gate is the full one, `.venv/bin/python -m nox -s build`, before your final push. The documentation has its own check: from `/workspace/301e4208ef81-ChatGPT_Codex/website` (a checkout of the website with its `node_modules`; read and run only, change nothing there) run `CONTENT_DIR=/home/devcapsule/worktrees/maintenance-impl-3 npm run check:content`; it validates the pages' structure and references and must pass. A typed version such as "0.3.0" in a page is refused; write `{{version}}`. Do not build images and do not start capsules.

## The task: slice 3 of three, "the documentation, the aliases' disposition and the changelog"

1. **Delete the retired spellings** (Part 5 item 6, the owner's decision): the rc4 hidden aliases (`config capabilities --local/--without/--required/--optional`, `config need`, `init --need/--required/--optional/--local`, `init --less-pedantic`, `config set-env/unset-env/list-env`, `config set-extra-docker-args/list-extra-docker-args/remove-extra-docker-args`, `config unset`, `config list`, `config resolve`, `run --force`, `run --force-config`) and the spellings slice 2 retired (`config agent add|remove`, `config tool omit|restore`, `config require|offer|drop tool`, `run --agent`). Each becomes a refusal of one line that names the replacement and exits 2, writing nothing; `selection_catalog`'s three agent names go with them, the listing's `agent` kind being the only thing that still needs to tell an agent from a tool, and it reads that from the capability table's providers, not from a list of names. Rewrite the tests that used an alias as a fixture step to use the current command; delete the tests of alias behavior; keep one test per deleted spelling that asserts the refusal, the replacement in the message and that nothing was written. `config capabilities --recover` is not an alias; it stays.
2. **The documentation says capability, component, IDE, minimum, resolution.** Rewrite `docs/configuration/capabilities.md` and `docs/configuration/project-versus-personal.md` for the model: the project requires, offers or recommends capabilities and may recommend a resolution; a requirement may carry a minimum, `name>=version`, one relation; the developer omits, adds, chooses a provider with `use`, and chooses the IDE; the IDE owns the lifetime of the container and can make use of the display, never "owns the display"; agents are ordinary capabilities with a vendor channel; the SDK major does not exist. Update `docs/reference/cli.md`: the command tree as slice 2 left it, the *Retired spellings* table replaced by one short paragraph saying the old spellings refuse and name their replacement. Update every other page under `docs/` that names `config agent add`, `config tool omit`, `require tool`, `--agent`, `sdk-major` or `TOOL=MAJOR` (grep for them); `docs/configuration/software-approvals.md` where it speaks of agents as a kind; `docs/reference/configuration-nodes.md` where it lists the SDK major.
3. **A conceptual entry page for the configuration section.** Write `docs/configuration/index.md`: what a DevCapsule configuration is, as a concept, before any detail: the project's manifest and lock in Git, the developer's checkout record on their computer, the workstation's records (defaults and trust), and how `run` derives a launch from the three; one screen of prose, then a short list pointing to the detail pages. Give it front matter like its neighbours (`description`, `weight` 1, `updated`). Link it from `docs/README.md`'s question table as the configuration section's entry in place of `inspect.md`.
4. **The changelog.** Add *New in candidate 5* to `engineering-docs/releases/v0.3.0/changelog.md`, for adopters: one model of capabilities and components; the owner's commands take capabilities, with a minimum; the resolution recommendation; the developer's `add`, `omit`, `restore`, `use`, `run --with`, `--use`; the SDK major removed, with how old files read; the retired spellings deleted, with the replacement rule; rc4 compatibility as the order's Part 5 item 4 states it. Move what *Not in candidate 4* said about the retired spellings into the done column.
5. **The prose standard.** The owner found the rc4 documentation written in machine prose and has booked a language review of every page. Do not add to that debt. Write every sentence as a person explains a thing to a colleague: one idea per sentence, the concrete noun first, no sentence that restates the one before it, no "This ensures", "seamlessly", "robust", "leverage", no bullet that is a paragraph, no heading that is a question. Read each page aloud before you commit it; if a sentence could open a product brochure, cut it.

## The care the owner asked for (Part 6), as acceptance

- Every deleted spelling has its refusal test; `grep -rn` for each old spelling in `devcapsule/` finds only its refusal, and in `docs/` finds nothing but the replacement paragraph.
- The documentation check passes on your worktree; every page under `docs/configuration/` and `docs/reference/cli.md` describes a command that exists at your tip, verified by running it.
- No kind returns: the grep of slice 1 still holds; `selection_catalog` is gone; the listing derives `ide`, `agent` and `tool` rows from the capability table and the component's own declarations.
- Files written by rc4 and by slices 1 and 2 keep reading as before; the tests of slices 1 and 2 pass unchanged except where they drove a deleted spelling.

## What you must not do

- Do not change the model, the manifest shape, the checkout record, the catalog or the resolver. Do not rename the IDE role (D-0014 is tabled). Do not touch the web console.
- Do not edit `CURRENT-STATUS.md` files, `intake-dispositions.md`, the `evidence/` directory, the work order, or run `devcapsule workflow publish`. Do not edit anything under `/workspace/301e4208ef81-ChatGPT_Codex`.
- Do not commit the `website` submodule pointer, `.idea/` files, `*.egg-info`, `.nox/`, `dist/` or `__pycache__`.
- Do not merge anything. Do not push to `main`, to `release-0.3.0`, to the slice-1 or slice-2 branch, or to any branch other than `ws-maintenance/capabilities-3-docs`. Do not rebase or force-push.
- Do not build images or run capsules.

## Deliverable

1. Commits on `ws-maintenance/capabilities-3-docs`, each message naming the component, the change and the evidence, ending with `Co-Authored-By: <model name> Codex <noreply@openai.com>`, the model name being the one you actually run as.
2. Push the branch and open one pull request with
   `gh pr create --base ws-maintenance/capabilities-2-commands --head ws-maintenance/capabilities-3-docs`.
   Title: "Capabilities and components, PR3: the retired spellings deleted, the documentation on the model, the configuration entry page, the candidate-5 changelog".
   The body lists what changed by the five points above, the choices you made where the order was silent and why, what you considered and left alone, the greps, the documentation check's result and the full gate's counts with what was skipped. End the body with `🤖 Generated with Codex`.
3. Print the PR URL as the last line of your output, or "NO PR" with the reason.

Write the PR body and your report at about 80% ASD-STE100: one fact per sentence, about twenty words, active voice. Every claim about behavior must be backed by a test or a command you ran.

The reviewer will read the diff and the pages, run the full gate and the documentation check, and post findings as comments on the PR and into your resumed session; expect up to three rounds. If you cannot proceed, because of a blocker like network or credentials, stop and say exactly what blocked you. Do not work around a blocker.
