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

## Why rules, and which

The purpose is outcomes: fewer files per change, fewer bugs of the missed-consumer class, shorter iterations.
A rule earns its place by protecting a design decision that has already changed and scattered when it did.
Parnas's criterion (1972) is the selector: hide each decision likely to change in one module, so a change to it
is an edit, not a search. An agent makes that criterion more binding, not less: its correctness on a scattered
decision is bounded by its search for every consumer, its context cost grows with the spread, the gate can verify
a decision cheaply only at one boundary, and an agent reproduces whatever pattern it finds, so spread compounds.

The rules named below are examples drawn from one afternoon's measurement. The real set comes from the discovery
step, and the owner picks it.

## Deliverables, in four slices

Slice 0 discovers the rules. Slice 1 makes the loop exist and green. Slice 2 adds the rules that need a baseline.
Slice 3 measures. Each slice is one pull request; slice 2 may be two.

### Slice 0: rule discovery

An interactive session between the owner and an agent, recorded in the order's directory as a candidate list.
Evidence in, not opinion:

- the footprint of each merged slice of the last cycle: files touched per design decision changed, from the diff
  stats, the way the IDE override slice was read on 2026-10-29;
- the bug records and the incident records: which defects were a consumer missed, a boundary crossed, or a pattern copied;
- the counts a candidate pattern has on `main` today.

Each candidate states the decision it protects, the module that should own it, the files the last change to it
touched, the bug or incident that motivates it, and the outcome expected: the footprint of the next change to
that decision. Candidates with no change history and no bug are parked, not written. The owner picks the set,
and the picked rules replace the examples in slices 1 and 2.

Record the footprint measure itself in `guardrails.md`; slice 3 reports it per rule.

### Slice 1: the loop exists

**Tool.** Add `ast-grep-cli` to the `dev` extra of `devcapsule-src/pyproject.toml` with an upper bound, recompile
`dev-requirements.txt`, and record the version in the developer environment document. Invoke it as `ast-grep`.

**Configuration.** `sgconfig.yml` at the repository root with `ruleDirs: [.ast-grep/rules]` and `testConfigs`
pointing at `.ast-grep/tests`. Rules match under `devcapsule-src/devcapsule/` and `devcapsule-src/tests/` by
explicit globs written from the real layout; there is no `src/` directory. `devcapsule-webconsole/` is a second
distribution with its own gate and is excluded.

**Gate wiring.** One pytest module, `devcapsule-src/tests/test_guardrails.py`, runs `ast-grep test` and
`ast-grep scan --json` from the repository root and fails on any error-severity match, on any warning-severity
match absent from the rule's baseline, and on a missing binary. This puts the rules inside `nox -s tests`, which
is what the hosted runner runs (`nox -s syntax tests typecheck` in `release-pex.yml`); a step in the `integration`
session would run locally only. No new nox session. Budget: one second.

**Rules that enter at `error`, zero violations required.** Examples until slice 0 replaces them.

1. `dc-slop-silent-except`: an `except` clause naming `Exception`, `BaseException` or nothing, whose body is
   `pass`, `...`, `return None` or a bare `return`, with no `raise` and no call into the project's logging. Four
   broad clauses and thirteen except-pass bodies today; the implementing workstream narrows the type or handles
   the failure at each site where the fix is local and behaviour-preserving, and baselines the rest with a reason.
   No inline suppression and no "explanatory comment" escape: the baseline file is where a reason lives.
2. `dc-exec-no-os-system`: no `os.system`. Zero sites today; the rule costs nothing and closes the door.
3. `dc-boundary-project-config-no-host-mutation`: the modules that parse and validate the project's declaration,
   `.devcapsule/devcapsule.toml`, import nothing from the adapters that write developer-owned host authorization
   state, nor from commands, launch or realization. This is the ast-grep statement of the boundary the pytest
   architecture test already proves by reachability; the two must agree, and the pytest test wins when they do not.
   The `note` names the layer that resolves host authorization and links source layout.
4. The rules derived from the incident records of the week of 2026-10-26, when the owner supplies them. They
   outrank 1 to 3 if the budget is short.

**Documentation.** `engineering-docs/development/guardrails.md`: the rules, how to run them, how to read a
diagnostic, how to add a rule with its valid and invalid cases, the baseline and promotion procedure, the incident
record form. Link it from `DEVELOPING.md`'s testing table, `engineering-docs/development/README.md` and
`index.md`. One line in `WORKFLOW-LOCAL.md` where the gate is described. `WORKFLOW.md` is the protocol and does
not change. `AGENTS.md` changes only where a sentence is now proven by a rule: replace the prose with a pointer,
do not keep both.

Done means a fresh clone, `pip install -r dev-requirements.txt` and `nox -s tests` run the rules, `ast-grep scan`
reports no error, and every rule has a valid and an invalid case that `ast-grep test` passes.

### Slice 2: structural rules with baselines

Examples until slice 0 replaces them. Each rule below has violations on `main` today, so each enters at `warning` with a baseline file beside it listing
the sites, and a cleanup work item recorded in the implementing workstream's status. A warning never fails the
gate; a new site outside the baseline does. The baseline shrinks and never grows. Promote the rule to `error` in
the pull request that empties its baseline. No refactoring in this slice: the cleanups are their own slices.

5. `dc-config-policy-owner`: `CapabilityPolicy.read(` is called only inside `configuration/capabilities.py` and
   the one derivation module the workstream names as the policy's owner. Thirteen sites. The cleanup is the
   modularity follow-up of the IDE override slice.
6. `dc-exec-subprocess-owner`: `subprocess.run`, `Popen`, `call`, `check_call`, `check_output` and the
   `python_on_whales` client are used only under `launch/`, `container_runtime/`, `host_daemon.py`,
   `host_open.py` and the `recursive_*` modules. Twenty-seven calls in eleven files today; the sites outside that
   set are `workflow_coordination.py`, `compat.py`, `commands/project.py` and `commands/_console_channel.py`.
   The repository has no single runner abstraction to route through; the rule confines, it does not redirect.
   Creating a runner is a design decision outside this order.
7. `dc-output-print-owner`: `print(` only in `commands/`, `cli.py` and the modules the owner designates as
   presenters. Measured: 193 sites, of which about forty in twelve files lie outside `commands/` and `cli.py`,
   twenty-one of them in `launch/pycharm/_launcher.py`. The owner decides whether the launcher is a presenter
   before the rule is written.

Do not write a rule for `os.environ` in this order: forty-three sites are the current design of the host-access
layer, and a rule there needs a design decision first.

### Slice 3: lessons after thirty days

Thirty days after slice 1 merges, record in `guardrails.md` under an "Operation" heading: which rules fired on a
real defect, which produced a false positive and how the rule was narrowed, the incidents added in the period,
the footprint of each change to a protected decision against the footprint before the rule, and the time the step
takes on the hosted runner. That tally is the input of a separate product order; how the tool
would be exposed in a project's `devcapsule.toml` or in the CLI is product design and is not written here.

### Rule intake from incidents

Rules grow from incidents, not from the tool's catalog. Each time agent output passes the gate and later costs
rework, the workstream that pays for the rework records the incident and adds the rule or the test that would have
refused it, in the same slice when that is small, otherwise as a work item named in the incident record.

An incident record states the date, the change, what the agent did wrong in one sentence, what it cost, and the
rule id or test that now covers it. Keep the records in `guardrails.md` until the implementing workstream names a
permanent home; link each from the rule's `note`.

A narrow rule that is correct beats no rule. A rule that fires on code the project considers correct is wrong and
is narrowed or dropped, never argued around with an inline suppression.

The incidents of the week of 2026-10-26 are not yet recorded in the repository; the owner supplies them, and the
rules derived from them join slice 1 before the order is assigned.

### Rule file contract

Every rule file carries `id` in the form `dc-<area>-<name>`; `message`, one sentence naming what is wrong and the
module that owns the operation; `note`, the remedy and a link to the document that states the invariant;
`severity` per the slice rules above. Write each rule from the ast-grep CST of a real snippet, never from guessed
node kinds.

## Acceptance evidence

1. `nox -s build` passes on the implementing branch, and `nox -s syntax tests typecheck`, the hosted runner's
   selection, runs the guardrails test; link the run. The docs contract inside `build` covers the documentation
   changes; no website build is needed because the new page lives under `engineering-docs/`.
2. `ast-grep test` passes and every rule has a valid and an invalid case.
3. `ast-grep scan` on the branch reports zero errors, and warnings equal to the baselines, or a documented difference.
4. One deliberately broken file per error rule fails the gate with the rule's message and note; capture the output.
5. Rule 3 and the pytest architecture test agree on a synthetic violation.
6. Slice 2: each baseline has its cleanup work item in the workstream status.
7. The guardrails step is timed on the hosted runner.

## Execution decisions and stopping points

The implementing workstream owns rule syntax, placement under `.ast-grep/` and the baseline file format.
Keep slice 1 to its rules, or fewer if measurement removes one; do not add rules because the tool makes it easy.

Stop and consult the owner before:

- adding a rule that would require a design decision, such as the host-access layer or a runner abstraction;
- changing code under `devcapsule-src/devcapsule/` beyond the local except-site fixes of slice 1;
- designating presenter modules for rule 7;
- touching `devcapsule-webconsole/`;
- writing anything that reads as a product promise to adopters.

The owner assigns the workstream, priority and target before implementation starts. The gate change does not
belong on `release-0.3.0`; the target is `main` after 0.3.0, under `maintenance` or a workstream the owner names.

## Pushback recorded with the draft

The outside draft, two parts, framed this as a `v0.3.x` internal process step and a precursor to a `v0.4.0`
feature, named a workstream `eng-ast-grep-dogfooding`, restated the workflow's pre-flight steps, assumed a `src/`
layout and used the `sg` alias. This order keeps the goal and drops those: the workflow is in `WORKFLOW.md`,
workstreams are named by the owner in `CURRENT-STATUS.md`, the layout is the one in source layout, and
`/usr/bin/sg` is util-linux.

From the draft's deliverables 2 to 4, kept and changed:

- The pytest wrapper is adopted over a nox step, because the hosted runner runs `nox -s tests` and nothing else.
- "Remediate or refine the ignores" becomes a split: fix locally where the fix is behaviour-preserving, baseline
  where it is a refactor. Ignore globs are not a remedy for a violation.
- The silent-except rule loses its "explanatory comment" escape; the reason goes in the baseline file.
- The print rule, which the first draft of this order refused, is admitted at warning after measurement showed the
  sites outside the presenters number about forty, not 193.
- The subprocess rule's note cannot say "route through the runner abstraction" because none exists; it confines.
- `os.system` is zero today, so its rule enters at error for free.
- The lessons note keeps the tally and drops the `v0.4.0` exposure design, which belongs to the product order.
- The checklist line goes in `WORKFLOW-LOCAL.md`, not `WORKFLOW.md` or `AGENTS.md`, since the step runs inside
  `nox -s tests` and the gate command does not change.

Two complements were weighed. Neither replaces this order:

- `ruff` is the ordinary opinionated linter the repository does not have. It covers rule 1 and a few hundred
  more, in milliseconds, with no rule authoring. It cannot express rules 3, 5, 6 and 7. Whether to add it is a
  separate owner decision; if yes, it joins the same pytest wrapper and rule 1 moves out of ast-grep.
- More pytest architecture tests over Python's `ast`, in the style of the existing one, express every rule above
  with full access to Python semantics. The case for ast-grep beside them is that a rule is one YAML file any agent
  can read, test and add in minutes, with a diagnostic the author sees at the call site; that is what lets the rule
  set grow by incident. Graph properties stay in pytest.
