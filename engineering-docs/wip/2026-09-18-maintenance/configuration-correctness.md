# Configuration correctness argument and test map

Audit target: production code at `6709756` on `ws-maintenance/triage`, after
the upgrade-remedy fix. This follow-up changes specification, tests and records,
not production behavior. The specification is
[`configuration-contract.md`](configuration-contract.md).

**Result: the complete implementation does not yet satisfy the contract.**
The argument below establishes restricted properties and identifies nine gap
families with ten executable counterexamples. It does not turn expected test
failures into accepted behavior. The counterexamples are tracked in the
[configuration lifecycle bug](../../bugs/devcapsule/2026-09-20-configuration-contract-not-enforced-across-boundaries.md).

## 1. What counts as evidence

A proof obligation names a property that must hold at an operation boundary.
Code inspection explains why its branches preserve that property; tests exercise
the branches and their composition through public commands. A branch-coverage
percentage alone establishes neither the specification nor that callers honor
the callee's preconditions.

We distinguish:

- **Established within stated preconditions:** the implementation follows the
  argument and the named cases exercise its meaningful partitions.
- **Refuted:** a concrete supported operation violates the obligation.
- **Open:** the feature, compatibility policy or sufficiently independent
  evidence needed for the argument does not exist yet.

Assumptions: configuration files are edited serially, the filesystem provides
the usual replace semantics, SHA-256 collision resistance is adequate, and
external Docker/vendor/runtime primitives obey their separately tested
interfaces. No proof here covers malicious local administrators, arbitrary raw
Docker passthrough, concurrent configuration writers, remote artifact retention
or actual GUI quality. Unsupported/malformed input is not assumed away where
the public interface must reject it.

## 2. Entrypoint-to-effect trace

This is the execution path, not a list of keyword matches:

| Boundary | Implementation | Obligation passed to the next stage |
|---|---|---|
| Invocation | `__main__` → `cli.main` → command framework `Group.invoke` / `Command.invoke` | Parse mechanics and carriers, retain explicit project context; report `CliError` as exit 2. |
| Context | `ProjectCommand.make_context`, `manifest_for`, `discover_project`, `checkout_record_paths` | Select nearest manifest or explicit path and the record for the canonical observed checkout. |
| Schema / vocabulary | `validate_manifest`, `lock_for`, `build_node_registry` and typed declarations | Supported representations, one name/family, constrained domains; every caller must use these checks. |
| Initialization | `initialize_project`, `Elicitor`, `_elicit_*` | Distinguish authored recommendations from developer answers; complete missing state without losing existing decisions. |
| Local editing | `ConfigSet/Bind/Authorize/UnsetCommand` → `CheckoutRecord.write` | Validate before persisting one change; preserve every other owned input. |
| Assessment | `review_configuration` → value, binding, secret and authorization validators | All independent failures represented, no partial answer map usable as a complete plan. |
| Resolution | `resolve_checkout` → render + `atomic_write` | Only a complete valid resolution is published; no download/build/launch. |
| Run preflight | `ProjectRunCommand.run`, `stale_resolution_inputs`, `_run_once_answers` | Supported fresh plan and valid temporary answers; no stale or removed consent revived. |
| Realization | `realize_environment`, `parse_locked_environment`, base validation, materializer | Exact selected artifacts/identity; acquisition consent checked before external effects; display reviewed before build. |
| Launch planning | `project_runtime_plan`, `PycharmRunOptions`, `build_run_config`, `build_docker_args` | Preserve upstream decisions in actual mounts, privileges, networking, display and secret delivery. |
| Completion | `run_pycharm` result → `record_known_good_configuration` | Snapshot on zero exit, deduplicate, preserve sensitive-file permissions; history failure does not fail the run. |

The implementation files are under
[`devcapsule/`](../../../devcapsule-src/devcapsule/), chiefly
[`commands/project.py`](../../../devcapsule-src/devcapsule/commands/project.py),
[`project_operations.py`](../../../devcapsule-src/devcapsule/project_operations.py),
[`project_configuration.py`](../../../devcapsule-src/devcapsule/project_configuration.py),
[`configuration_review.py`](../../../devcapsule-src/devcapsule/configuration_review.py)
and [`configurations/pycharm/_launcher.py`](../../../devcapsule-src/devcapsule/configurations/pycharm/_launcher.py).

## 3. The compositional argument

Let `S = (P, L, C, R)` be the stored state, and let `Answers(C)` include
ordinary values, explicit omissions, bindings, authorizations and legacy choices.
These triples are specifications: the braces state preconditions and
postconditions, not assertions that the code already enforces them everywhere.

### A. Editing preserves the rest of the state

```text
{supported C; correct checkout; unambiguous node n; valid proposed answer v}
    edit(n, v)
{P and L and R unchanged; Answers(C') = Answers(C) with only n updated}
```

The operation chooses the appropriate validator, changes the corresponding
in-memory collection and calls `CheckoutRecord.write`. For modeled valid
content, the writer serializes every other collection unchanged. This explains
why ordinary edits do not grant permissions and why a directory binding survives
an authorization change. It also explains why `none` must be modeled as an
omission rather than a value that would be overwritten by a default.

For independent nodes `a` and `b`, each operation changes a disjoint map entry
and neither changes the other's declaration. Therefore `edit(a); edit(b)` and
`edit(b); edit(a)` have the same semantic result. By induction, any sequence of
valid independent edits preserves all untouched answers. A later refused edit
does not undo earlier successful commands. This is a sequence of atomic file
replacements, not a multi-command transaction.

**Evidence:** the new ordinary-state table covers absent/value/omitted crossed
with set/omit/unset; six orderings cover ordinary/binding/authorization edits;
the failed-second-edit test checks the intermediate durable state. Existing
tests cover required-node refusal and the individual typed domains/providers.

**Limits:** G1 admits an unknown checkout schema, G4 bypasses registry uniqueness,
and G5 discards unmodeled content during serialization. The general triple is
therefore refuted outside the modeled, admitted subset. Atomic replacement
cannot repair an incorrect serialized result.

### B. Resolution is a complete checked derivation

```text
{supported P, L, C; selected checkout; coherent typed registry}
    resolve
{either complete R' derived from those inputs, or old R retained with diagnostics}
```

`review_configuration` obtains ordinary values/effects, directory bindings,
secret source names and authorization reviews, then checks state overlap.
`require_ready` guards consumption; `resolved_authorizations` independently
refuses consumption of an incomplete review. `resolve_checkout` writes the
resolution only after this assessment and local-base inspection succeed.
Thus a stale base cannot be hidden by fixing the first stale host answer,
and a failed local identity check cannot publish a new plan.

**Evidence:** independent family errors, overlap refusal and saved-output
preservation tests; the complete recovery journeys execute each proposed answer
and check a strictly decreasing pending-authorization set. With stable inputs,
each accepted choice removes one pending authorization and does not alter the
others. The finite set reaches empty, after which resolution succeeds. This is
the termination argument for recovery, conditional on choosing valid answers
and on any required local image still being available.

**Limits:** G4 means the assumed coherent registry is not checked on this path.
G7 shows legacy host values escape typed validation. G8 shows that collecting
one exception per family does not collect every independent invalid node within
the family. The narrow authorization recovery proof survives; the whole-tree
completeness claim does not.

### C. Authorization cannot be created by another owner's data

```text
{no developer answer for host node n}
    read/inspect/resolve project recommendation n
{no host grant for n}
```

The authorization reviewer treats absence as absence, compares each decision
with its own dependency fingerprint, and retains false/string denial values
without conflating them with missing answers. Base recovery constructs a current
accepted value instead of replaying an old published digest. Local-image
recovery uses the recorded image identity. Selected vendor acquisitions use the
same required-decision rule as their registry entries.

These local properties hold on the normal configuration path. They are not
enough to establish the triple for **initialization**: `_elicit_recommendations`
returns recommendations found in the existing manifest, and `initialize_project`
stores any without an existing local record as authorizations. That is G2.
Preserving an existing denial fixed one branch, but did not establish that a
previously unanswered recommendation is safe on another branch.

### D. Launch preserves a checked decision

```text
{valid effective decision for n is deny; no explicit run-once allow}
    plan and launch
{the corresponding host capability remains denied}
```

`ProjectRunCommand` reads current authorizations even with `--force`, and
run-once values are validated before realization. Display selection is checked
against the verified base before building. The current checkout's decisions,
rather than stale resolved grants, feed launch options. Tests establish these
facts at the `PycharmRunOptions` boundary.

To complete the proof, every downstream transformation must preserve them.
`build_run_config` initializes sudo from `PYCHARM_ENABLE_SUDO` and only changes
it when the supplied option is true; passing false cannot clear the inherited
true. G9 is a direct counterexample at the next boundary. G7 separately shows
that `bool("false")` creates an allow from malformed legacy input. Consequently
the full denial-preservation claim is false even though the options passed by
the project command are correct for current typed authorizations.

### E. A client upgrade preserves old input meaning

For every supported released predecessor `v`, we need:

```text
interpret(new_client, artifacts_from_v) = previous_configuration_meaning
```

The actual comparison is values, authority, artifact selection and state—not
an invariant image ID when the launcher executable intentionally changes.
The existing historical fixtures test unchanged project/configuration bytes;
formation tests independently demonstrate that changing the runtime executable
changes the derived image identity without selecting new components.

This proves specific unchanged-version-1 cases. It does **not** establish a
general old-schema interpreter. There is no versioned decoder/migration chain;
some readers check exactly 1, while mutation/run omit some checks entirely (G1).
Catalog contracts and materialization recipe acceptance also belong to the
compatibility surface. A test intentionally rejecting an earlier recipe is
evidence of a boundary, not proof of the no-user-action upgrade guarantee.

A future schema change needs a separate preservation argument for every
migration edge, followed by composition of those edges. In-memory normalization
or durable migration could both satisfy the contract. Choosing a mechanism does
not remove the obligation, and synthetic “old” data generated by new code cannot
be its only evidence.

## 4. Obligation-to-test map

Test paths below are relative to `devcapsule-src`. `test_configuration_contract.py`
contains the new whole-lifecycle obligations;
[`test_upgrade_recovery.py`](../../../devcapsule-src/tests/test_upgrade_recovery.py)
contains the earlier 71-case recovery table. Full node IDs are included so each
claim can be selected directly with pytest.

| Obligation / conditions | Evidence | Result and limit |
|---|---|---|
| **C1: checkout isolation** — explicit/discovered path, default/named/missing checkout | `tests/test_project_commands.py::test_project_resolve_registers_default_checkout_and_list_uses_registry`; `tests/test_project_commands.py::test_named_checkout_registration_selects_distinct_record_and_reports_missing`; `tests/test_configuration_contract.py::test_second_checkout_cannot_inherit_the_first_checkouts_authority` | Established for valid records; malformed/schema admission is a separate obligation. |
| **C2: unique family and provider vocabulary** — unknown name, wrong carrier, provider syntax, duplicate names | `tests/test_configuration_nodes.py::test_unknown_node_lists_the_declared_vocabulary`; `tests/test_configuration_nodes.py::test_wrong_carrier_family_names_the_right_spelling`; `tests/test_configuration_nodes.py::test_bind_value_rejects_wrong_or_missing_provider`; `tests/test_configuration_nodes.py::test_a_name_declared_twice_fails_at_construction` | Constructor works; public resolution bypass is refuted by G4. |
| **C3: ordinary typed values** — valid/invalid strings, integers, booleans, sizes, reserved words | `tests/test_configuration_contract.py::test_scalar_value_domain_partition`; `tests/test_project_commands.py::test_project_config_set_uses_declared_metadata_and_resolves_runtime_effect` | Establishes listed domain partitions and memory derivation; does not claim generic runtime delivery for every declared value. |
| **C4: edits preserve unrelated input** — absent/value/omitted, nine transitions; six independent edit orders; refused second edit | `tests/test_configuration_contract.py::test_ordinary_node_transition_table`; `tests/test_configuration_contract.py::test_independent_changes_commute_and_require_one_final_resolve`; `tests/test_configuration_contract.py::test_a_failed_second_edit_does_not_undo_the_first_or_publish_it` | Established for modeled content. G1/G5 refute general preservation across unsupported representations/content. |
| **C5: requiredness and denial are distinct** — required unset/omission refused, optional denial retained | `tests/test_project_commands.py::test_unset_refuses_mandatory_nodes_and_removes_optional_ones`; `tests/test_project_commands.py::test_set_none_records_an_explicit_omission`; `tests/test_project_commands.py::test_authorize_records_denial_as_a_value` | Established for these carriers. Init's missing required ordinary prompts remain G6. |
| **C6: init reaches a usable checkpoint** — empty/partial/complete, supplied/existing/default/prompt/missing answers | `tests/test_project_init.py::test_noninteractive_init_reaches_the_full_postcondition`; `tests/test_project_init.py::test_repair_completes_a_hand_authored_manifest`; `tests/test_project_init.py::test_repeated_init_without_answers_still_refuses`; `tests/test_elicitation.py::test_command_line_wins_over_every_other_source`; `tests/test_elicitation.py::test_noninteractive_batch_failure_lists_every_missing_answer` | Engine ordering established; not every node is routed through it (G6), and recommendation provenance is lost (G2). |
| **C7: shared complete assessment** — independent family errors, conflict, invalid/unknown authorization, refusal preserves R | `tests/test_upgrade_recovery.py::test_independent_value_binding_secret_and_authorization_errors_are_collected`; `tests/test_upgrade_recovery.py::test_conflicting_state_bindings_do_not_publish_partial_resolution`; `tests/test_upgrade_recovery.py::test_review_handles_invalid_and_removed_host_nodes` | Established for these partitions. G4/G7/G8 limit whole-tree claims. |
| **C8: consent validity and recovery progress** — five host nodes × allow/deny × current/stale; ten base states; two vendor acquisitions × four states | `tests/test_upgrade_recovery.py::test_host_answer_state_table_and_executable_choices`; `tests/test_upgrade_recovery.py::test_base_state_table`; `tests/test_upgrade_recovery.py::test_acquisition_decisions_use_the_same_review_contract` | Every offered host alternative is executed. External local-image availability remains conditional. |
| **C9: whole recovery journey** — manifest/lock/both change × X11 unanswered/true/false; local tag identity; missing local image | `tests/test_upgrade_recovery.py::test_upgrade_recovery_commands_converge_to_the_intended_launch`; `tests/test_upgrade_recovery.py::test_local_base_recovery_keeps_immutable_identity_not_mutable_tag`; `tests/test_upgrade_recovery.py::test_local_recovery_refusal_preserves_the_record` | CLI through realization and launch options, with external effects replaced. It does not prove the lower launcher's treatment of those options (G9). |
| **C10: freshness respects dependencies** — semantic input change vs formatting/irrelevant metadata; known vs unknown schemas | `tests/test_project_commands.py::test_manifest_edit_after_lock_never_blocks_commands_and_resolve_reconciles`; `tests/test_configuration_contract.py::test_unknown_project_schema_is_refused_without_mutation`; G1/G3 tests below | Current whole-tree freshness and some gates established; scoped-dependency and universal schema-admission claims refuted. |
| **C11: runtime does not grant or persist extra authority** — run-once invalid input, force after revocation, display six-way partition | `tests/test_upgrade_recovery.py::test_invalid_run_once_choices_cannot_trigger_a_build`; `tests/test_upgrade_recovery.py::test_force_cannot_resurrect_a_revoked_host_permission`; `tests/test_upgrade_recovery.py::test_force_uses_current_legacy_host_decisions`; `tests/test_upgrade_recovery.py::test_display_decision_table`; `tests/test_upgrade_recovery.py::test_display_denial_stops_before_materialization` | Established through project options/base preflight. G7/G9 refute the unrestricted end-to-end claim. |
| **C12: state and secrets stay developer-owned** — bindings and values survive recovery, values absent from persistence and image plan, late unavailable secret | `tests/test_upgrade_recovery.py::test_recovery_preserves_values_bindings_secrets_and_adopted_state`; `tests/test_project_runtime_plan.py::test_project_runtime_plan_contains_only_in_container_contract`; `tests/test_pycharm.py::test_selected_codex_state_and_explicit_secret_are_delivered`; `tests/test_pycharm.py::test_bound_secret_must_exist_on_host` | Covers declared environment provider and modeled state. Secret availability is a later launch check; not all launch feasibility is proven before building. |
| **C13: artifact and runtime identity** — cache hit/miss/conflict, wrong base, new launcher bytes | `tests/test_materialization.py::test_materialization_reuses_only_verified_canonical_image`; `tests/test_materialization.py::test_materialization_rejects_conflicting_canonical_tag`; `tests/test_materialization.py::test_validate_base_rejects_wrong_identity`; `tests/test_runtime_artifact.py::test_packaged_launcher_supplies_itself_despite_source_override`; `tests/test_runtime_artifact.py::test_runtime_update_changes_formation_identity_without_changing_components` | Identity mechanism established at unit seams; actual release artifacts and GUI need external validation. |
| **C14: supported-client upgrade continuity** — v026.2 inspection/resolution; v026-era formation inspection; v0.2.11 unchanged launch planning | `tests/test_release_compatibility.py::test_v0262_checkout_resumes_with_no_user_action`; `tests/test_release_compatibility.py::test_v026_formation_artifacts_are_inspectable_despite_manifest_digest`; `tests/test_upgrade_recovery.py::test_released_checkout_runs_unchanged_under_new_client` | Explicitly partial historical coverage. All use format 1; no cross-format migration theorem follows. |
| **C15: history records successful configuration only** — zero/nonzero result, deduplication, private snapshots | `tests/test_project_commands.py::test_project_run_records_known_good_configuration_only_on_success`; `tests/test_config_history.py::test_first_success_records_one_private_generation`; `tests/test_config_history.py::test_distinct_content_appends_and_dedup_covers_all_generations` | Establishes trigger, bytes, permissions and deduplication; does not promise reproducibility without run-once choices or under changed external state. |

## 5. Counterexamples that prevent the full argument

Each test below asserts the desired contract. It has `xfail(strict=True)` so
an unexpected pass forces review/removal of the marker. These are **known unmet
obligations**, not skipped cases and not evidence that the product is correct.
Failure types are constrained so unrelated setup exceptions do not count as
the expected counterexample.

| Gap | Counterexample and violated boundary | Executable obligation |
|---|---|---|
| **G1 — inconsistent schema admission** | Mutating a version-99 checkout rewrites it as version 1. A fresh resolution relabeled version 99 still reaches launch. Manifest/lock reject 99, so this is path-dependent validation. | `tests/test_configuration_contract.py::test_unknown_checkout_schema_cannot_be_rewritten`; `tests/test_configuration_contract.py::test_unknown_resolution_schema_cannot_be_executed` |
| **G2 — recommendation becomes consent** | With a repository Docker recommendation and no local record, `init --authorize base-image default` also records `docker-daemon = host-socket`. No Docker answer was supplied. | `tests/test_configuration_contract.py::test_init_cannot_treat_repository_recommendations_as_developer_answers` |
| **G3 — unrelated metadata invalidates resolution** | Adding workflow metadata makes the saved environment resolution stale although it consumes none of that metadata. Whole-manifest hashing causes it. | `tests/test_configuration_contract.py::test_workflow_metadata_is_not_a_configuration_dependency` |
| **G4 — registry invariant not enforced by all callers** | Declare ordinary `home`, colliding with the managed-home binding. Registry construction rejects the tree, but `config resolve` writes a successful resolution. | `tests/test_configuration_contract.py::test_resolution_cannot_publish_an_ambiguous_node_tree` |
| **G5 — local edits erase unmodeled content** | Add an unknown checkout table, then change one authorization. The command succeeds and silently drops that table. It neither preserves it nor refuses unsupported content. | `tests/test_configuration_contract.py::test_edit_must_preserve_unknown_content_or_refuse_without_writing` |
| **G6 — initialization does not elicit all required nodes** | A hand-authored required integer node and supplied base consent reach resolve with no ordinary-value question, despite interactive input providing the answer. Init refuses after its earlier writes. | `tests/test_configuration_contract.py::test_init_elicits_a_required_ordinary_value_once` |
| **G7 — untyped legacy authority** | Legacy `[host] development-sudo = "false"` resolves successfully and reaches project launch options as true through `bool("false")`. | `tests/test_configuration_contract.py::test_legacy_host_values_are_typed_before_authorization` |
| **G8 — serial errors remain within a family** | Two independently invalid ordinary values yield only the first value's error. The new review batches families, not every node. | `tests/test_configuration_contract.py::test_independent_invalid_values_are_reported_together` |
| **G9 — lower planner overrides denial** | `PycharmRunOptions(enable_sudo=False)` plus `PYCHARM_ENABLE_SUDO=1` produces `PycharmRunConfig(enable_sudo=True)`. Correct upstream options do not imply correct execution. | `tests/test_configuration_contract.py::test_launcher_environment_cannot_override_explicit_sudo_denial` |

G2 and G9 require priority because they increase authority without the effective
developer answer required by the contract. G1/G5 threaten configuration
preservation across schema evolution. The rest prevent a single compositional
argument, even when a particular normal journey succeeds. No production fixes
for these follow-up findings are claimed by this audit.

G2 overlaps the init/regeneration behavior the owner explicitly accepted as an
interim compromise on 2026-09-06, recorded in the linked project-management
handoff. That exception must remain visible: it explains why observed behavior
can be temporarily accepted while still failing the broader ownership contract.
This audit does not quietly revoke the interim ruling or adopt it as the final
security model.

## 6. Why the earlier 100% coverage result was insufficient

The upgrade repair measured statements/branches in `configuration_review.py`
and its authorization helpers. That measurement remains correct. It says those
functions executed every instrumented branch in the selected tests.

It does not establish that:

- every public path constructs the registry or validates artifact versions;
- init preserves the **source** of an answer when moving between owners;
- serializers retain unknown representations;
- every family validator accumulates all errors;
- a downstream launcher honors an explicit false; or
- a future reader understands an older schema or recipe.

G4 and G9 are particularly useful checks on the method: a correct constructor
does not help a caller that never invokes it, and a correct argument to a mocked
callee does not prove the real callee's behavior. The new tests target those
composition boundaries instead of adding more examples to the already-covered
recovery branches.

## 7. Validation and the next proof step

The focused audit module has **35 passing cases and ten strict expected
failures**. All use isolated temporary configuration directories and existing
test tools. No container, image download or GUI session is needed to reproduce
the counterexamples. Run from `devcapsule-src`:

```text
.venv/bin/python -m pytest tests/test_configuration_contract.py --no-cov -q -rx
```

The full local gate passed: mypy, 739 tests, source CLI smoke, PEX construction
and nine packaged-executable tests. There are 18 deselected host-sensitive
tests and 11 expected failures (ten audit obligations plus one pre-existing
expected failure). Its success means the implementation's existing checks
remain green and the known failures remain explicitly identified; it does not
close them. Relative document links and all 61 named test references were also
checked against the working tree.

To make the full argument true, the next implementation should establish an
admitted typed configuration at one boundary, retain answer ownership/provenance,
and pass one effective launch decision into a planner that cannot override it
through another input path. Each G test must then become an ordinary passing
test. Schema evolution additionally needs an explicit supported-version policy
and real predecessor fixtures before a format change ships. Workstation
precedence, missing-lock handling and regeneration ownership remain the explicit
product-design boundaries in the contract, not assumptions hidden in the proof.
