---
status: fixed
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

G2 overlapped the interim init/regeneration behavior accepted on 2026-09-06.
The owner's subsequent instruction to implement the complete contract supersedes
its consent-conflating portion. Reading repository advice now creates no grant;
explicit recommendation authoring and local consent remain distinguishable.
Project ownership of manifest/lock regeneration is retained.

## Reproduction

From `devcapsule-src`:

```text
.venv/bin/python -m pytest tests/configuration/test_contract.py --no-cov -q -rx
```

The original module now has **45 passing cases**, including all ten former
counterexamples without expected-failure markers. The complementary
`tests/configuration/test_invariants.py` has **128 passing cases**, partitioned
by schemas, ownership, edits, permissions, runtime admission and compatibility.
Docker/GUI are substituted only where needed; launcher policy tests execute
the real configuration builder.

## Implementation and validation

2026-09-20: refactored on `ws-maintenance/triage`. Shared artifact admission,
complete local-document serialization, registry enforcement, registry-driven
elicitation, typed host decisions, a pure checkpoint projection and one execution
admission boundary replace the inconsistent paths. Init and individual set/bind
commands share answer operations. Project launch cannot inherit legacy path,
credential or privilege options. Current bindings and decisions remain effective
under `--force`; unset cannot revive legacy grants. Local records use private
staging and atomic replacement. Access is serialized by the owner's explicit
precondition; no cooperative lock is needed under that assumption.

The full `nox -s build` gate passed: **877 tests, mypy, source CLI smoke, PEX
construction and nine packaged tests**. Eighteen host-sensitive tests were
excluded; one unrelated expected failure remains. The document-admission,
assessment/execution and pure-resolution modules each have 100% statement and
branch coverage. The proof/test map states the supported conditions and limits;
this is not a claim of 100% coverage of the entire CLI.

## Closure conditions

Implementation and unit proof obligations G1–G9 are met. `fixed` is not a
release/closure claim: owner PR integration and actual host privilege/display
acceptance remain. Future schema or recipe changes must meet the release's
predecessor-compatibility obligation; unspecified future formats are refused.

The related [upgrade-remedy fix](2026-09-19-upgrade-config-recovery-rejects-its-own-remedy.md)
now composes with these enforced boundaries. Reopen if any supported lifecycle
again loses an unrelated decision, invents authority, or bypasses admission.
