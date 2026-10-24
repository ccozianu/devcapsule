# Second implementation review of PR #253 — Claude Code / Claude Fable 5.1

The owner broadened the existing implementation to general saved Docker
arguments, including GPUs and mounts, and requested another loop with you.
Your previous review is PR #254, accepted and merged. GPT-6 Codex extended
that result on `ws-maintenance/0.3.0-checkout-env`. This is an implementation
review; do not spend a separate round reviewing the work order.

## Checkout and context

Work only in `/home/devcapsule/worktrees/checkout-env-review`, branch
`ws-maintenance/0.3.0-checkout-env-review`, based on the new implementation tip.
Do not touch `/home/devcapsule/worktrees/checkout-env` or the original checkout.
Read README.md, DEVELOPING.md, WORKFLOW.md topic 9.11, WORKFLOW-LOCAL.md,
engineering-docs/work-orders/2026-10-23-saved-docker-arguments.md,
maintenance status's "General saved Docker arguments" section, then the diff.
`git diff f1ad30f..HEAD` isolates the generalization; PR #253 contains the
whole feature against release-0.3.0. The original env-file work order and
first review record are historical, superseded where the new order says so.

## What changed

One private JSON token list under XDG `docker-arguments` replaces the unmerged
env-file design. New config commands set-extra-docker-args (replace entire
list), list-extra-docker-args (masked, optionally JSON), remove-extra-docker-args
(clear). `set-env` remains hidden-input convenience over the SAME list;
unset-env and list-env work there too. Actual saved arguments precede raw
one-off arguments. Docker owns option semantics, duplicates and unknown options;
launcher-owned options retain the existing rejection boundary. No shell eval.

The pure devcapsule/docker_arguments.py helpers recognize env-option forms.
The configuration/docker_arguments.py adapter owns private storage and updates.
commands/project.py owns CLI/wiring; launch/pycharm/_launcher.py masks inline
extra environment values when printing a command. Actual Docker arguments
retain their values and semantics. A redacted --print-command is explicitly
a preview; the user runs project run to use the saved values. Docs state this.
The owner trusts processes/agents inside the capsule with injected credentials.

## Review priorities

Correctness, then clarity, then meaningful coverage of changed lines. Check:
- literal tokens, spaces, option ordering, replacement/removal and private permissions;
- GPU and mount arguments survive the real launcher builder;
- malformed-file repair and no accidental activation recovery;
- hidden env convenience edits preserve unrelated options;
- split/attached long and short env forms are masked in list JSON/text,
  normal warnings and print-command without changing actual launch arguments;
- option operand boundaries and repeated env assignments;
- forbidden launcher options are refused before persistence and when launching;
- host-only routing, no values in resolutions/history, and failure paths.

Do not add encryption, vaults, hostile-agent defenses, approvals, GPU runtime
provisioning, migrations for this unmerged store, or a comprehensive Docker CLI
schema. No capability/lock/workflow redesign. Docker remains the parser for
other options; do not solve unrelated old passthrough bugs unless the changed
feature makes a concrete scoped fix necessary. Record limitations honestly.
No real secrets. No containers, image builds, GPU probes or external services.
The implementor ran a fake-value Docker probe using an existing base: literal
values, empty values and a one-off env override all passed. No GPU execution
was tested; hardware/runtime setup remains the host's responsibility.

## Environment and checks

Own devcapsule-src/.venv installed from dev-requirements.txt. Initialize the
pinned website submodule with `git submodule update --init website`.
From devcapsule-src:

    .venv/bin/python -m pytest -q tests/test_saved_docker_arguments.py tests/test_checkout_environment.py tests/test_project_commands.py tests/configuration/test_architecture.py tests/test_version_sets.py --no-cov
    PYTEST_ADDOPTS="--basetemp=/tmp/checkout-args-review-tests" .venv/bin/python -m nox -s build

Run synchronously in the foreground. Do not use Bash run_in_background in
print mode. Keep the gate log OUTSIDE pytest basetemp: pytest deletes that
directory. Use /tmp for basetemp: the previous review found an unrelated
host-daemon test assumes the scratch is not on a host-backed mount.

## Delivery

For each gh shell call:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Repository ccozianu/devcapsule. Keep human author Costin Cozianu
<ccozianu@gmail.com>, with:

    Co-authored-by: Claude Fable 5.1 <noreply@anthropic.com>

Commit only on your review branch, push it and create the next review PR
against `ws-maintenance/0.3.0-checkout-env`. Title it as the generalization
review of #253 (second loop). Use a body file. State findings and evidence,
considered-and-left-alone items and reasons, unimplemented proposals, gate
counts and limitations. Open no empty PR; report no change if justified.

Do not edit status, intake, evidence, work order, workflow rules or coordination
state. Do not commit submodule pointers, IDE files, caches or generated files.
No merges, rebases, force pushes or pushes to other branches. Stop and report
access/reviewer/credential blockers. The implementor assesses your diff and
merges accepted improvements; the human merges #253. Last output line: review
PR URL, or NO PR.
