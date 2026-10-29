# Work Order: Structural guardrails for the repository with ast-grep

Origin: product-owner draft written outside the repository, 2026-10-29, reworked against the repository as it stands.
Status: draft for discussion; not assigned; implementation has not started.
Coordination owner: `project-management`. Implementation owner and target: not assigned.
Requirements: none yet. The process half of this order needs no product requirement.
A product feature built on the same tool is a separate order with its own requirement.

## Outcome

Give the repository gate a second structural check beside the existing architecture tests:
declarative rules over the Python syntax tree, run by `ast-grep`, that fail the gate in well under a second
when a change violates a named architectural invariant or introduces a known agent-authored anti-pattern.

Each rule names the invariant it enforces, the document that states it, and what to do when it fires.
The gate reports a violation as a diagnostic the author can act on without reading the rule's source.

A rule set is the product of this order, not the tool. The tool earns its place through the rules that exist
only because of it.

The motivation is the feedback loop between the gate and the agents that work in this repository: the more of
the project's opinion the gate can state mechanically, the less an agent's output depends on the reviewer catching
it, and the more work can be handed to an agent at once. Where the gate is silent, the human is the validator, and
the week of 2026-10-26 showed the cost: a day of work rewritten because agent-authored shortcuts passed the gate.

## What exists today

The gate (`nox -s build`) runs `compileall`, mypy in its default strictness, pytest, the packaging tests and the
docs contract. No linter runs. Nothing flags a bare `except`, an `except Exception: pass`, or a call that crosses
a package boundary outside the configuration package.

One architecture test exists, `tests/configuration/test_architecture.py`, written over Python's own `ast` module.
It proves two laws of `devcapsule.configuration`: the import graph is acyclic, and the core modules do not reach
the effectful adapters, the commands, launch or realization. Source layout states those laws in
`engineering-docs/development/source-layout.md`.

Measured on `main` at `6e509e2d`, package `devcapsule-src/devcapsule/` only:

| Candidate pattern | Hits | Files |
|---|---|---|
| `CapabilityPolicy.read(` outside the policy module | 13 sites | several configuration modules and commands |
| `subprocess` imported | 11 files | launch, runtime, host daemon, recursive modules, one command |
| `except Exception:` or bare `except:` | 4 | — |
| `pass` as the only statement after `except` | 13 | — |
| `print(` in package modules | 193 | — |
| `os.environ` read or written | 43 sites | — |

These counts measure merged code after human review. They do not measure what the gate let through during the
week and the human caught or rewrote afterwards; that is what the incident record below is for.

The first row is the finding of 2026-10-29: the explicit IDE override touched eight consumers of the capability
policy because the policy's derivation is reconstructed at each consumer instead of owned by one module.
Twice during that slice a consumer was missed, once caught in review, once filed as a bug. That is the class of
defect a structural rule prevents, and it is the first rule this order should write.

## Decisions already taken

The owner wants the gate, not the reviewer, to refuse agent-authored anti-patterns and structural drift, and wants
the rules to grow from what the project actually suffers. The product feature that may later offer the same to
adopters is a motive, not the justification; the order stands without it.
The tool is `ast-grep`. It is installed through the `ast-grep-cli` wheel on PyPI, added to the `dev` extra of
`devcapsule-src/pyproject.toml` and the compiled `dev-requirements.txt`, so every venv, capsule and the hosted
runner get the same binary.

Invoke it as `ast-grep`, never as `sg`. On Linux `/usr/bin/sg` is util-linux's set-group command and shadows the alias.

The existing architecture test stays. Do not port it to `ast-grep` to make the tool look busier; the test proves
graph properties, reachability and cycles, that a per-file pattern cannot express.

The product feature, agent-ready codebase verification offered to adopters in a capsule, is out of scope.
This order produces the experience and the rule set a later product order can draw on; it makes no promise about
one.

## Deliverables

### Tool and configuration

Add `ast-grep-cli` to the `dev` extra with an upper bound, recompile `dev-requirements.txt`, and record the chosen
version in the developer environment document.

Place `sgconfig.yml` at the repository root with `ruleDirs: [.ast-grep/rules]` and `testConfigs` pointing at
`.ast-grep/tests`. Rules match under `devcapsule-src/devcapsule/` and `devcapsule-src/tests/` by explicit globs
written from the real layout; there is no `src/` directory. `devcapsule-webconsole/` is a second distribution
with its own gate and is excluded from this order.

Add a `guardrails` step to the `integration` session of `devcapsule-src/noxfile.py`, inside `build`, that runs
`ast-grep scan` with the error rules and `ast-grep test` over the rule tests. Budget: one second on the hosted runner.

Done means a fresh clone, `pip install -r dev-requirements.txt`, and `nox -s build` run the rules without any
step outside the documented developer setup.

### The rule set

Write each rule from a measured need, with the ast-grep CST of a real snippet, never from guessed node kinds.
Every rule file carries:

- `id`, in the form `dc-<area>-<name>`;
- `message`, one sentence naming what is wrong and the module that owns the operation;
- `note`, the remedy and a link to the document that states the invariant;
- `severity`, `error` only when the rule has zero violations on `main` at the time it enters the gate.

A rule with existing violations enters as `warning`, with the violations listed in a baseline file beside it and a
bug or work item for the cleanup. A warning never fails the gate; the baseline shrinks and never grows, and the
gate fails when a warning rule gains a new site. Promote a rule to `error` in the pull request that empties its baseline.

First rules, to be confirmed by measurement:

1. `dc-config-policy-owner`: `CapabilityPolicy.read(` is called only inside `configuration/capabilities.py` and
   the one derivation module the implementing workstream names as the policy's owner. Warning with a baseline of
   the 13 sites; the cleanup is the modularity follow-up of the IDE override slice.
2. `dc-launch-subprocess-owner`: `subprocess` and `python_on_whales` are imported only under `launch/`,
   `container_runtime/`, `host_daemon.py`, `host_open.py` and the `recursive_*` modules. Measure whether
   `commands/project.py` and `compat.py` belong to the allowed set or to the baseline.
3. `dc-slop-blind-except`: no bare `except:`; `except Exception` only when the handler re-raises, logs through the
   project's logging, or returns a typed failure. Four sites today.
4. `dc-slop-except-pass`: no `except` whose body is `pass` alone. Thirteen sites today; some may be legitimate
   cleanup and belong in the baseline with a reason.
5. `dc-config-no-adapter-import`: the configuration core imports none of the commands, launch or realization
   modules. This duplicates half of the pytest architecture test on purpose: it is the rule that proves the
   ast-grep diagnostic is as actionable as the pytest assertion, and the two must agree. If they ever disagree,
   the pytest test wins.

### Rule intake from incidents

Rules grow from incidents, not from the tool's catalog. Each time agent output passes the gate and later costs
rework, the workstream that pays for the rework records the incident and adds the rule or the test that would have
refused it, in the same slice when that is small, otherwise as a work item named in the incident record.

An incident record states the date, the change, what the agent did wrong in one sentence, what it cost, and the
rule id or test that now covers it. Keep the records in this order's directory under
`engineering-docs/work-orders/` until the implementing workstream names a permanent home; link each from the rule's `note`.

A narrow rule that is correct beats no rule. A rule that fires on code the project considers correct is wrong and
is narrowed or dropped, never argued around with an inline suppression.

The five rules above are the first slice. The incidents of the week of 2026-10-26 are not yet recorded in the
repository; the owner supplies them, and the rules derived from them join the list before the order is assigned.
They take precedence over the five if the budget is short.

Do not write a rule for `print(` or `os.environ` in this order. The counts show those are the current design
of the CLI's output and host-access layers, not drift; a rule there needs a design decision first.

Done means every rule has a positive and a negative case under `.ast-grep/tests`, `ast-grep test` passes, and
`ast-grep scan` on `main` reports exactly the baselined warnings and no errors.

### Documentation

Add `engineering-docs/development/guardrails.md`: what the rules are, how to run them, how to read a diagnostic,
how to add a rule, the baseline procedure, and the promotion rule. Link it from `DEVELOPING.md`'s testing table,
`engineering-docs/development/README.md` and `index.md`.

Add the gate step to `WORKFLOW-LOCAL.md` where the local gate is described, as one line.

Update `AGENTS.md` only if a sentence there is now proven by a rule; replace the prose with a pointer to the rule,
do not keep both.

## Acceptance evidence

1. `nox -s build` on the implementing branch passes with the guardrails step present, timed.
2. A deliberately broken file, one per error rule, fails the gate with the rule's message and note; capture the output.
3. `ast-grep test` passes for every rule.
4. The warning rules' baselines list exactly the sites measured in this order, or a documented difference.
5. Rule 5 and the pytest architecture test agree on a synthetic violation.
6. The hosted runner runs the step; link the run.

## Execution decisions and stopping points

The implementing workstream owns rule syntax, file placement under `.ast-grep/` and the baseline file format.
Keep the rule set to the five above, or fewer if measurement removes one; do not add rules because the tool
makes it easy. A rule that fires on code the project considers correct is wrong, not the code; drop it or narrow it.

Stop and consult the owner before:

- adding a rule that would require a design decision, such as the output or host-access layers;
- changing any code in `devcapsule-src/devcapsule/` beyond what a baseline needs, which is nothing; the cleanups
  are separate slices;
- touching `devcapsule-webconsole/`;
- writing anything that reads as a product promise to adopters.

The owner assigns the workstream, priority and target before implementation starts. The gate change does not
belong on `release-0.3.0`; the target is `main` after 0.3.0, under `maintenance` or a workstream the owner names.

## Pushback recorded with the draft

The outside draft framed this as a `v0.3.x` internal process step and a precursor to a `v0.4.0` feature, named a
workstream `eng-ast-grep-dogfooding`, restated the workflow's pre-flight steps, and assumed a `src/` layout.
This order keeps the goal and drops those: the workflow is in `WORKFLOW.md`, workstreams are named by the owner in
`CURRENT-STATUS.md`, and the layout is the one in source layout.

Two complements were weighed. Neither replaces this order:

- `ruff` is the ordinary opinionated linter the repository does not have. It covers rules 3 and 4 and a few
  hundred more, in milliseconds, with no rule authoring. It cannot express rules 1, 2 and 5. Whether to add it is a
  separate owner decision; if yes, it belongs in the same gate step and the two rules move out of ast-grep.
- More pytest architecture tests over Python's `ast`, in the style of the existing one, express every rule above
  with full access to Python semantics. The case for ast-grep beside them is that a rule is one YAML file any agent
  can read, test and add in minutes, with a diagnostic the author sees at the call site; that is what lets the rule
  set grow by incident. Graph properties stay in pytest.
