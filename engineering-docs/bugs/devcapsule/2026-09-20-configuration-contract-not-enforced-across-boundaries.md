---
status: confirmed
severity: untriaged
target: none
owner: maintenance
opened: 2026-09-20
requirements: [R-IDE-CONFIG-001, R-COMPAT-001, R-PRODUCT-002]
---

# Configuration Contract Is Not Enforced Across Boundaries

## Evidence and scope

The owner requested the entire configuration contract, from first initialization
through edits and CLI/base/schema upgrades, and a correctness argument mapped
to unit tests. Auditing production revision `6709756` from the CLI entrypoint
through actual launch planning found nine unmet obligation families. These are
related by the missing enforcement of a common typed, ownership-aware model;
this record keeps their closure conditions together without treating a message
fix as resolution of the contract.

The [contract](../../wip/2026-09-18-maintenance/configuration-contract.md) and
[correctness argument/test map](../../wip/2026-09-18-maintenance/configuration-correctness.md)
give the intended behavior, implementation trace and exact test IDs.

| ID | Observed counterexample | Required correction |
|---|---|---|
| G1 | Unknown checkout schema is rewritten as 1; unknown resolution schema reaches execution. | Admit supported schemas consistently before mutation or execution; refuse unsupported data without altering it. |
| G2 | Init reads an existing project Docker recommendation and persists it as a grant although only base-image consent was supplied. | Retain answer provenance; repository recommendations cannot create developer authority. |
| G3 | Workflow-only metadata makes environment resolution stale. | Fingerprint the actual semantic dependencies and read earlier fingerprints compatibly. |
| G4 | The registry rejects a duplicate ordinary/binding name, while resolve successfully publishes the same tree. | Enforce registry invariants on every interpretation path. |
| G5 | An authorization edit silently removes an unrelated unknown checkout table. | Preserve safely understood content or refuse without rewriting; never silently lose it. |
| G6 | Interactive init does not ask for a required ordinary node before resolution fails. | Route required ordinary/provider questions through the same elicitation contract. |
| G7 | Legacy `development-sudo = "false"` becomes effective true. | Validate/normalize legacy host decisions by type and domain before use. |
| G8 | Independent invalid ordinary values are still reported one at a time. | Accumulate errors by node, not merely one error per family. |
| G9 | Legacy `PYCHARM_ENABLE_SUDO=1` overrides the project's explicit `enable_sudo=False` launch option. | Preserve the effective denial through the lower launch planner. |

G2/G9 increase authority without the effective developer answer required by the
contract. G1/G5 can lose or misinterpret durable configuration. Severity and
release target have not been assigned by the owner.

G2 overlaps the already recorded interim init/regeneration behavior accepted
by the owner on 2026-09-06. Its exception and unsettled final semantics are
preserved in the correctness argument; this record does not revoke that ruling.

## Reproduction

From `devcapsule-src`:

```text
.venv/bin/python -m pytest tests/test_configuration_contract.py --no-cov -q -rx
```

There are 35 passing lifecycle/domain cases and ten strict expected failures
covering G1–G9 (G1 has two boundaries). Each expected-failure test asserts the
desired behavior and records a counterexample. These markers do not accept the
defect as correct behavior. Docker/GUI are substituted where needed; G9 runs
the real launch-configuration builder.

## Closure conditions

Turn every counterexample into a passing ordinary test, preserve the independent
positive cases, and revise the correctness argument so its preconditions are
established at public entrypoints and maintained through actual launch planning.
Validate supported historical inputs and the relevant real-host privilege/display
behavior. Establish the schema-evolution release obligations before claiming
general migration support. Owner-approved splitting may move individually
resolved obligations into linked records, but none disappears behind a green
overall test count.

No production change is made for these findings in this audit. The earlier
[upgrade-remedy fix](2026-09-19-upgrade-config-recovery-rejects-its-own-remedy.md)
remains a bounded repair; its local coverage result is not evidence that this
broader contract is fulfilled.
