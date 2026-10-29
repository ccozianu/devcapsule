# Work Order: Explicit IDE Requirement Override

Origin: product-owner direction during the 0.3.0rc8 IDE investigation, 2026-10-28.
Status: ready for assignment; implementation has not started.
Coordination owner: `project-management`. Implementation owner and release target: not assigned.
Requirements: R-CONFIG-001; its mandatory-constraint rule needs the explicit exception described below.

## Outcome

Allow a developer to choose another IDE for one session when the project requires a particular IDE:

```bash
devcapsule project --path /path/to/checkout run --ide codium --force
```

Keep the project's requirement and the checkout's saved IDE unchanged. Materialize the requested IDE as needed.
The next plain `project run` must use the saved choice, subject to the project's ordinary requirements.

An IDE can be a legitimate requirement. A project that develops a plugin for that IDE is one example.
Do not remove the ability to require an IDE or migrate existing requirements into recommendations to avoid the conflict.

## Decisions already taken

The owner selected explicit overrides instead of forbidding IDE requirements.
Use `--force` as the public escape hatch for the IDE policy conflict.
The first implementation covers this case; the mechanism should permit deliberate extension to other policy checks later.
Do not turn this work into a general bypass of every command failure.

Force means that the developer accepts a named departure from the project contract for this launch.
It does not mean that the project requirement was satisfied.
Warn which required IDE is bypassed and which IDE will run.
Keep the departure visible in the launch's recorded configuration and diagnostics where those records describe contract satisfaction.

## Deliverables

### Launch behavior

Add `--force` to `project run` and propagate it through launch preparation and subsequent plan derivation.
Accept component names such as `codium` and capability names such as `frontend-ide` through the same selection path.
Without force, refuse a conflicting required IDE with an actionable diagnostic that names the explicit override.
Do not fail later with an internal error about two interactive surfaces.

With force, produce one coherent runtime plan whose selected interactive surface is the requested IDE.
Exclude the replaced IDE from active surface contributions that would invalidate that plan.
Preserve unrelated capabilities, SDK requirements, provider choices, and persistent IDE state.
Reconcile dependencies needed by remaining capabilities rather than blindly removing the old IDE's dependency closure.
If a remaining real dependency makes the requested environment impossible, explain that dependency and refuse.

An ordinary IDE override that does not conflict with a project requirement must continue to work without force.
Force must not select an arbitrary replacement when no alternate IDE was requested.
Check `--print-command` through the same override path and preserve its documented side-effect rules.

Done means the override survives every derivation used by a real launch and reaches environment materialization and runtime planning.

### Scope and persistence

The override applies to one launch. Do not rewrite the shared manifest or platform lock to weaken the requirement.
Do not save an exception or change the checkout's default IDE as a side effect of this command.
Downloaded artifacts and the alternative IDE's own persistent settings may remain available for later use.
Keep each IDE's settings in its existing separate namespace.

Force must not grant host access, accept vendor terms, approve software, skip artifact-integrity checks, or invent missing components.
Ordinary consent and dependency checks still apply to the requested environment.
These checks protect a different contract from the overridable IDE policy.

The interaction with `--save` needs an owner decision before implementation of that combination.
The default scope of this work is a transient override; do not silently persist a requirement waiver.

Done means a following plain launch returns to ordinary selection, including after a failed or interrupted forced launch.

### Contracts and documentation

Update R-CONFIG-001 and affected normative contracts to distinguish normal requirement enforcement from an explicit launch exception.
Retain ordinary refusal for unmet mandatory constraints outside the named override.
Record the owner's choice in the normal decision records and link the resulting records from the implementing workstream.
Update CLI help and current user documentation with the command, warning, scope, and persistence behavior.
Do not advertise proposed behavior as available before implementation.

Done means requirements, CLI help, diagnostics, and documentation describe the same behavior.

## Acceptance evidence

Use an isolated checkout fixture with a required PyCharm IDE and a saved PyCharm choice.
Prove the following through the built executable and the derived runtime plan:

1. A conflicting Codium launch without force fails with the named policy diagnostic before materialization.
2. `--ide codium --force` selects Codium; `--ide frontend-ide --force` selects the same surface.
3. The forced plan has one interactive surface and preserves unrelated mandatory tools.
4. Shared configuration and the saved IDE remain unchanged; a following plain launch selects PyCharm.
5. An interrupted or failed forced launch does not leave a saved waiver or change the next launch's IDE.
6. Required consent, artifact validation, and real dependency failures still prevent launch with force.
7. Existing IDE overrides without a requirement conflict continue to work without force.
8. The agreed `--save` behavior and the print-command path obey the same explicit contract.

Add focused regression tests at the policy and plan boundaries, plus built-CLI coverage for flag propagation.
Run the repository gate from WORKFLOW-LOCAL.md before delivery.
Use a recorded IDE smoke session to prove that Codium opens the project and that the next ordinary session returns to PyCharm.
Use isolated project state for acceptance; do not migrate the working DevCapsule checkout as a test fixture.
Identify executable versions and distinguish plan evidence from an observed GUI launch.

## Execution decisions and stopping points

The executing workstream owns internal representation, code placement, and test design.
Give each bypass an explicit policy identity or equivalent narrow handling; do not catch arbitrary errors and continue.
Avoid a framework larger than the first use requires.

The owner assigns the workstream, priority, and release target before implementation starts.
Consult the owner on `--save` semantics, additional overridable checks, or a need to alter host-access or integrity guarantees.
If current implementation work has changed this path, reconcile with that work before editing shared code.
Do not broaden the override to other commands as part of this order without owner direction.

## Evidence and starting points

The investigation used `/usr/local/bin/devcapsule0`, reporting `0.3.0rc8`, build mnemonic `v0.3.0-rc8`,
source revision `8d41fabe9f7ecc439e6854a0e89e9a9586fd4edf`.
Its run help documents transient `--ide` choices and persistence through `--save`.
An isolated project with Python required and PyCharm selected derived Codium for both accepted spellings.
Its saved checkout record stayed unchanged, and a subsequent plain plan selected PyCharm.

The DevCapsule checkout inspected during that investigation instead declared `python-ide` in legacy `capabilities.need`.
After staging outstanding trust answers in memory, plan derivation rejected the alternate surface with:

```text
component 'pycharm' is an interactive surface and cannot accompany the selected surface 'codium'
```

This is preparation evidence from the built executable, not a completed GUI acceptance run.
No project configuration was changed by the investigation.

Mainline evidence was read at local `main` and `origin/main`, both `29815c958ce29e78d88f175ce4cd60f9cc2acdf3`.
That is the locally available mainline baseline, not a claim about subsequently published commits.
The author also read R-CONFIG-001, WORKFLOW.md topic 12.11, and WORKFLOW-LOCAL.md.
Recheck the receiving branch and live work before implementation.

Relevant source paths are `devcapsule-src/devcapsule/commands/project.py`, `commands/_run_flow.py`,
`configuration/derivation.py`, `configuration/capability_selection.py`, and `components/catalog.py`.
Existing tests in `devcapsule-src/tests/test_run_flow.py` cover transient choices but do not establish the required-IDE override.
