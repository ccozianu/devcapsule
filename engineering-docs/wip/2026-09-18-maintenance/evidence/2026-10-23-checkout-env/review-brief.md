# Implementation review: checkout environment, Claude Code / Claude Fable 5.1

GPT-6 Codex implements the owner's checkout-local environment feature for
0.3.0 on `ws-maintenance/0.3.0-checkout-env`, targeting `release-0.3.0`.
Review the implementation PR for that head branch. The owner asked you to
improve the implementation through the reviewer loop, not review the work
order as a separate deliverable.

## Checkout and reading order

Your checkout is `/home/devcapsule/worktrees/checkout-env-review`, branch
`ws-maintenance/0.3.0-checkout-env-review`, based on the implementation tip.
Do not touch `/home/devcapsule/worktrees/checkout-env` or the original checkout.
Read README.md, DEVELOPING.md, WORKFLOW.md topic 9.11, WORKFLOW-LOCAL.md,
engineering-docs/work-orders/2026-10-23-checkout-environment.md,
the maintenance status section "Checkout environment slice — 2026-10-23",
then configuration/environment.py, the added config commands and run wiring
in commands/project.py, runtime_configuration.py's LaunchConfiguration,
and the added/changed tests. Python paths are under devcapsule-src/devcapsule.
The new tests are devcapsule-src/tests/test_checkout_environment.py.

## Task

Improve the changed lines, in this order: correctness, clarity, test coverage.
Inspect the actual diff against origin/release-0.3.0. Check persistence,
checkout identity, failure handling, concurrent updates, names-only output,
CLI integration and launch wiring. Verify no values enter configuration
history, reports or printed launch commands. Managed files live in the XDG
`environments` tree because the `projects` configuration tree is mounted
into the capsule. The Docker client reads the env-file, not the daemon.
Inspect precedence and the documented lifecycle. Check host/capsule command
routing. list-env currently uses MUTATES to request execution on the host,
since the host file is intentionally not mounted; keep any improvement small.

The owner explicitly trusts agents and processes inside the capsule with
injected credentials. Do not add vaults, encryption, hostile-agent defenses,
extra approval prompts, or unrelated security machinery. Raw Docker options
remain outside the resolved plan and can echo inline values. General raw-argv
redaction is outside this slice. No new schema or component secret-binding
mechanism is requested. Do not widen the work into environment sharing,
automatic migration, runtime environment introspection or general config fixes.

## Validation

Your own devcapsule-src/.venv is installed from dev-requirements.txt.
From devcapsule-src:

    .venv/bin/python -m pytest -q tests/test_checkout_environment.py tests/test_project_commands.py tests/configuration/test_architecture.py --no-cov
    PYTEST_ADDOPTS="--basetemp=/home/devcapsule/worktrees/checkout-env-review-scratch" .venv/bin/python -m nox -s build

Initialize the pinned website submodule with `git submodule update --init website`
so the docs-contract gate runs. Run the gate synchronously in the foreground.
Do not use Claude Bash run_in_background: the process dies with print mode.
Do not start containers, build images, access real credentials, or run Docker
probes. The implementor already ran a fake-value probe on an existing base:
literal punctuation/spaces, empty values and explicit --env precedence passed.
No real PostgreSQL, OAuth, or SMTP credentials have been used.

## Delivery and authorship

For every gh invocation activate:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Use `gh pr list --head ws-maintenance/0.3.0-checkout-env --json number,url`
to find PRn. Review it with `gh pr diff NUMBER`. Keep the human Git author
Costin Cozianu <ccozianu@gmail.com>; add:

    Co-authored-by: Claude Fable 5.1 <noreply@anthropic.com>

Commit improvements on your review branch, push it, and open PRn.1 against
`ws-maintenance/0.3.0-checkout-env` in ccozianu/devcapsule. Use a body file.
State each finding, the change and its proof; considered-and-left-alone
items with reasons; unimplemented proposals; gate counts and limitations.
Open no empty PR. If no change is justified, report that explicitly.

Do not edit status files, intake, evidence, work order, workflow rules or
published coordination state. Do not commit submodule pointers, IDE files,
venvs, caches or generated artifacts. Do not merge, rebase, force-push or
push to any branch except your review branch. Stop and report any access,
credential, or reviewer blocker. Your report's last line must be the PR URL
or NO PR. The implementor will read your diff and assess it; only the human
merges the implementation PR.
