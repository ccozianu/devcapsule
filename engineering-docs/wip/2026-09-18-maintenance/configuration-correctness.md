# Configuration correctness argument and test map

Status: the nine audited gap families are repaired by the configuration refactor.
The ten former expected failures are ordinary passing regression tests. This
argument concerns the implemented V1 contract, not unspecified future features.
See [the complete contract](configuration-contract.md) for node domains,
ownership, initialization, edits, resolution and upgrade semantics.

The owner clarified that the mission includes implementation, and explicitly
supplied the single-threaded precondition: no concurrent access within one
process or between processes during an operation. That makes a read/validate/
replace operation a well-defined transition. We do not add a lock or pretend
that separate CLI commands form one transaction.

## 1. The implementation boundary

The entry path is `__main__ → cli.main → Command/Group.invoke → project`.
Argument parsing supplies an explicit command and answers; it does not grant
permissions. The relevant implementation is organized by responsibility:

| Responsibility | Implementation |
|---|---|
| Supported artifact representations and complete checkout serialization | [`configuration_documents.py`](../../../devcapsule-src/devcapsule/configuration_documents.py): `Artifact`, `admit_document`, `table`, `render_document` |
| File ownership, typed domains, source dependencies and authorization questions | [`project_configuration.py`](../../../devcapsule-src/devcapsule/project_configuration.py): manifest/lock/checkout/resolution readers, node validators, `review_authorizations`, freshness |
| A unique name and runtime effect per node | [`configuration_nodes.py`](../../../devcapsule-src/devcapsule/configuration_nodes.py): `NodeRegistry`, `build_node_registry` |
| Complete assessment and execution admission | [`configuration_review.py`](../../../devcapsule-src/devcapsule/configuration_review.py): `ConfigurationReview`, `HostAccess`, `ExecutionConfiguration.load` |
| Pure derived checkpoint and predecessor comparison | [`configuration_resolution.py`](../../../devcapsule-src/devcapsule/configuration_resolution.py): `render_resolution`, `same_effective_resolution` |
| Local edits and initialization | [`project_operations.py`](../../../devcapsule-src/devcapsule/project_operations.py): `CheckoutRecord`, `apply_configuration_answers`, initialization elicitation |
| Invocation and final launch options | [`commands/project.py`](../../../devcapsule-src/devcapsule/commands/project.py): project commands and run-once validation |
| Actual launcher configuration and Docker arguments | [`_launcher.py`](../../../devcapsule-src/devcapsule/configurations/pycharm/_launcher.py): `build_run_config`, `build_docker_args` |

`load_checkout` establishes supported representation, observed checkout path,
and matching creator/slug before a local record is edited or executed. Every
lock-dependent command obtains the same unique node registry through `lock_for`;
the pure review also constructs it, so library callers cannot skip that invariant.
Creating an empty checkout registration is not an interpretation of its node tree.

`ExecutionConfiguration.load` is shared by `project run` and
`fresh_resolved_project`. It admits all four artifacts, enforces freshness unless
force was explicit, requires a complete assessment, validates runtime fields and
surface consistency, and checks a fresh checkpoint against its derived meaning.
Only then can the command validate run-once answers and request materialization.

## 2. Preconditions and limits

- Configuration access is serialized. Each process sees stable configuration
  inputs during its operation; the owner explicitly supplied this precondition.
- Supported released configuration representations are format 1. Unknown
  formats and unknown checkout structural fields are refused, not guessed.
  A future schema needs a decoder/migration and predecessor evidence before release.
- Filesystem replacement has the host OS's atomic-rename semantics. Temporary
  local records are private from creation; replacement failure retains the old
  target and cleans up staging. There is no multi-file or power-loss transaction.
- Docker images, downloaded artifacts, display infrastructure and secret sources
  can become unavailable. Their external contracts require refusal and retained
  decisions; unit tests cannot establish host availability.
- The raw Docker passthrough is an explicit user escape from the modeled plan.
  Launcher-owned conflicting options are rejected. The argument does not promise
  isolation against arbitrary deliberate passthrough instructions.
- General workstation overlays/policy, new provider families, identity relocation
  and an unspecified historical recipe matrix are not invented by this repair.
  The contract identifies the currently implemented interface separately.

## 3. Compositional argument

### A. Admission precedes interpretation

For artifact `A` and operation `op` that reads it:

```text
{A has an unsupported representation}
    admit(A); op(A)
{refusal; no interpretation, mutation of A, or launch}
```

An integer version check distinguishes `1`, `true`, `1.0` and `"1"`. Structural
tables are checked before chained access. Checkout ownership is checked against
the observed path and project identity. Init performs this admission before
regenerating artifacts. `--force` changes freshness policy only.

`config resolve` does not read the old generated checkpoint: it may replace it
with an output derived from supported input. That is explicitly permitted output
regeneration, not a migration of unsupported input. This distinction is tested.

### B. An edit has a frame: unrelated answers retain their meaning

Let `C[n := v]` mean replacing one logical node after domain validation:

```text
{admitted C; valid answer v for n}
    edit(n, v); write(C)
{meaning(C') = meaning(C[n := v]); R unchanged}

{admitted C; invalid proposed answer}
    edit(n, bad)
{refusal; saved C and R unchanged}
```

`CheckoutRecord` retains the admitted document. Values, bindings, state and
authorizations are views into that document; the writer serializes the entire
result, including unrelated malformed answers which still need repair. Empty
answer tables already present are retained. Unknown structural extensions cause
refusal without rewriting. Formatting/comments are not part of semantic meaning.

`apply_configuration_answers` is shared by init and individual set/bind commands.
The same requiredness, provider and type rules therefore apply to both. A new
value removes its omission; an omission removes its value. An authorization
replaces the same logical legacy decision as well; unset removes both spellings.
Independent edits commute because they change disjoint logical leaves. An invalid
second CLI command does not undo a successful first command or publish a new R.

Init stages local answers until validation/elicitation succeeds, then writes C
and attempts resolution. Its project manifest and lock may already have been
written; those are repairable initialization checkpoints, not a claimed atomic
transaction across all four artifacts.

### C. Reading project advice cannot create developer authority

```text
{no developer answer for host node n}
    initialize/inspect/resolve an existing repository
{no new grant for n}
```

Existing recommendations are returned as project metadata, not placed in the
local answer cache. `_elicit_host_answers` records only command-line or prompted
developer answers. On a newly authored project an explicit answer may author a
recommendation and accept it for that checkout in one interaction. Default
omission does neither. Existing grants/denials retain their dependency fingerprints.

Required ordinary and binding questions use a separate elicitation namespace
from project identity, so `--set creator 7` cannot borrow the project creator
answer. They are derived from the node registry, not a fixed list of init flags.
Missing required answers are collected across reachable families. Existing valid
local-base selections are carried without replacing them with the recommendation
or asking for consent again; resolution still verifies the recorded identity.

The owner's instruction to implement this contract supersedes the consent-
conflating portion of the 2026-09-06 interim init ruling. Project ownership of
manifest/lock regeneration is retained. The former contradiction is resolved
explicitly rather than silently reclassified as intended behavior.

### D. Resolution either publishes a complete plan or preserves the old one

```text
{admitted, uniquely named inputs}
    assess(P, L, C); resolve
{one complete R = derive(P, L, C), or refusal with old R intact}
```

Every ordinary, directory, secret and authorization family is assessed; each
family gathers independent node errors. Adopted state is validated as a directory
mapping, and overlap with a binding is refused. Two node names cannot control one
runtime effect. Legacy host decisions have explicit domains; Python truthiness
is not an interpreter for permissions.

`render_resolution` is pure and refuses an incomplete assessment. The only
publication occurs after this assessment and any local-base identity inspection.
It does not read secret values, download components or start containers. The
same pure derivation checks fresh output and compares predecessor meaning.

Recovery has a finite progress measure: the number of pending authorizations.
With stable dependencies, accepting one offered valid choice settles exactly that
node and does not unsettle independent nodes. Executable-choice and journey tests
check that progress, including denial and immutable local-base recovery. Missing
external images are a stated precondition failure, not a fabricated success.

### E. Denial survives composition into the real launcher

```text
{current effective decision is deny; no explicit run-once allow}
    assess → HostAccess → PycharmRunOptions → build_run_config → Docker arguments
{the host capability remains denied}
```

`HostAccess` is immutable. It overlays validated legacy decisions, current
recorded authorizations, then explicit permitted run-once answers. Both domain
membership and scalar type are checked: `"false"` and `1` are not boolean grants.
Absence and false remain distinct. Current bindings and secret source names also
come from the assessment, even with `--force`; old output cannot restore a
revoked mapping.

Project launch sets `inherit_legacy_configuration=False`. The lower builder
therefore cannot introduce extra state directories, token files, token-variable
bindings or privileges from its compatibility environment. Platform observations
and explicitly bound secret sources remain usable. Independently, an explicit
`enable_sudo=False` overrides legacy environment truth even for the legacy
launcher; only an absent option inherits that command's environment setting.

The generated runtime is shape-checked before materialization. A fresh source
fingerprint is insufficient: the derived content must also match, with typed
canonical comparison (`true` differs from `1`). A stale forced plan must still
name the lock's surface and a valid runtime. Display selection occurs against
the verified base before building, preserving the earlier recovery contract.

### F. A CLI upgrade does not itself require new decisions

```text
{supported released inputs; unchanged effective configuration}
    interpret with the new CLI
{same user values, authority, selected artifacts and state bindings}
```

No freshness or authorization dependency includes the CLI version. New outputs
use the scoped manifest projection. A predecessor's unlabelled whole-manifest
fingerprint is accepted on exact match; on mismatch, its complete derived
meaning is compared with today's pure derivation while lock/checkout checks
remain in force. Workflow metadata and display-name changes can therefore remain
fresh without repinning, rewriting local decisions or prompting for consent.

The v026.2, v026-era formation and v0.2.11 fixtures are checked-in historical
inputs. They establish the tested supported cases, not a theorem about arbitrary
future schemas/recipes. Every future representation change must extend admission
and prove preservation for its released predecessors. D-0009 still permits a new
matching-runtime image build when launcher bytes change; that is distinct from a
configuration change or consent renewal and is explained before materialization.

## 4. Obligation-to-test map

Paths are relative to `devcapsule-src`. Parameterized tests state the condition
partitions directly. The [earlier recovery case map](upgrade-recovery-contract.md)
adds the host/base/acquisition/display cross-products and full recovery journeys.

| Obligation | Conditions and executable evidence |
|---|---|
| C1: checkout isolation | `tests/test_configuration_contract.py::test_second_checkout_cannot_inherit_the_first_checkouts_authority`; `tests/test_project_commands.py::test_named_checkout_registration_selects_distinct_record_and_reports_missing` |
| C2: schema and ownership admission | `tests/test_configuration_invariants.py::test_schema_admission_distinguishes_version_from_truthiness` (4 artifacts × 8 invalid versions); `tests/test_configuration_invariants.py::test_unsupported_artifact_refuses_without_side_effects` (4 artifacts × 5 public paths); `tests/test_configuration_invariants.py::test_every_edit_admits_checkout_before_replacing_it` (all five edit paths); `tests/test_configuration_invariants.py::test_malformed_checkout_table_is_an_actionable_error` |
| C3: unique names/effects and typed values | `tests/test_configuration_nodes.py::test_a_name_declared_twice_fails_at_construction`; `tests/test_configuration_contract.py::test_resolution_cannot_publish_an_ambiguous_node_tree`; `tests/test_configuration_invariants.py::test_two_nodes_cannot_control_one_runtime_effect`; `tests/test_configuration_contract.py::test_scalar_value_domain_partition` |
| C4: edit frame and sequential composition | `tests/test_configuration_contract.py::test_ordinary_node_transition_table` (3 states × 3 operations); `tests/test_configuration_contract.py::test_independent_changes_commute_and_require_one_final_resolve` (all 6 orders); `tests/test_configuration_contract.py::test_a_failed_second_edit_does_not_undo_the_first_or_publish_it` |
| C5: preservation, privacy, failed writes | `tests/test_configuration_invariants.py::test_unknown_checkout_fields_are_never_discarded`; `tests/test_configuration_invariants.py::test_invalid_unrelated_answers_survive_an_edit_until_repaired`; `tests/test_configuration_invariants.py::test_checkout_writer_round_trips_every_supported_scalar`; `tests/test_configuration_invariants.py::test_checkout_writer_nan_and_unsupported_scalar`; `tests/test_configuration_invariants.py::test_private_atomic_replace_preserves_the_previous_file_on_failure` |
| C6: initialization and owner provenance | `tests/test_project_init.py::test_noninteractive_init_reaches_the_full_postcondition`; `tests/test_project_init.py::test_repair_completes_a_hand_authored_manifest`; `tests/test_project_init.py::test_repeated_init_without_answers_still_refuses`; `tests/test_configuration_contract.py::test_init_cannot_treat_repository_recommendations_as_developer_answers`; `tests/test_project_init.py::test_init_denial_changes_checkout_without_rewriting_recommendation` |
| C7: one elicitation through shared carriers | `tests/test_configuration_contract.py::test_init_elicits_a_required_ordinary_value_once`; `tests/test_configuration_invariants.py::test_required_configuration_cannot_inherit_an_identity_answer` (5 identity spellings); `tests/test_configuration_invariants.py::test_init_and_individual_edits_have_the_same_local_effect`; `tests/test_configuration_invariants.py::test_init_retains_a_current_local_base_without_reasking`; `tests/test_configuration_invariants.py::test_missing_required_nodes_are_batched_across_init_families` |
| C8: complete assessment/publication | `tests/test_configuration_invariants.py::test_invalid_nodes_are_batched_within_and_across_families`; `tests/test_configuration_contract.py::test_independent_invalid_values_are_reported_together`; `tests/test_upgrade_recovery.py::test_conflicting_state_bindings_do_not_publish_partial_resolution`; `tests/test_configuration_invariants.py::test_incomplete_assessment_cannot_be_serialized_or_treated_as_compatible` |
| C9: authorization dependency/recovery | `tests/test_upgrade_recovery.py::test_host_answer_state_table_and_executable_choices`; `tests/test_upgrade_recovery.py::test_base_state_table`; `tests/test_upgrade_recovery.py::test_acquisition_decisions_use_the_same_review_contract`; `tests/test_upgrade_recovery.py::test_upgrade_recovery_commands_converge_to_the_intended_launch`; `tests/test_upgrade_recovery.py::test_local_base_recovery_keeps_immutable_identity_not_mutable_tag` |
| C10: typed permission precedence and revocation | `tests/test_configuration_invariants.py::test_permission_precedence_is_typed_and_preserves_denial` (5 nodes, valid/invalid domains and each precedence level); `tests/test_configuration_invariants.py::test_removing_a_decision_cannot_reveal_a_legacy_grant`; `tests/test_configuration_contract.py::test_legacy_host_values_are_typed_before_authorization`; `tests/test_upgrade_recovery.py::test_force_cannot_resurrect_a_revoked_host_permission` |
| C11: real downstream denial boundary | `tests/test_configuration_invariants.py::test_project_launch_cannot_inherit_unbound_paths_or_credentials`; `tests/test_configuration_invariants.py::test_explicit_sudo_decision_overrides_legacy_environment`; `tests/test_configuration_contract.py::test_launcher_environment_cannot_override_explicit_sudo_denial`; `tests/test_configuration_invariants.py::test_force_cannot_resurrect_directory_or_secret_access` |
| C12: refuse invalid runtime before effects | `tests/test_configuration_invariants.py::test_invalid_derived_plan_fails_before_materialization`; `tests/test_configuration_invariants.py::test_fresh_source_digests_do_not_authorize_tampered_output`; `tests/test_configuration_invariants.py::test_force_still_requires_a_coherent_execution_plan`; `tests/test_configuration_invariants.py::test_project_mount_is_validated_before_resolution_or_materialization`; `tests/test_upgrade_recovery.py::test_invalid_run_once_choices_cannot_trigger_a_build` |
| C13: scoped freshness and old encodings | `tests/test_configuration_invariants.py::test_metadata_only_changes_are_fresh_but_runtime_changes_are_stale` (legacy/scoped); `tests/test_configuration_invariants.py::test_unused_toml_native_metadata_does_not_enter_runtime_dependencies`; `tests/test_configuration_invariants.py::test_unsupported_fingerprint_representation_is_refused`; `tests/test_release_compatibility.py::test_v0262_checkout_resumes_with_no_user_action`; `tests/test_upgrade_recovery.py::test_released_checkout_runs_unchanged_under_new_client` |
| C14: materialization/display identity | `tests/test_materialization.py::test_materialization_reuses_only_verified_canonical_image`; `tests/test_materialization.py::test_validate_base_rejects_wrong_identity`; `tests/test_runtime_artifact.py::test_runtime_update_changes_formation_identity_without_changing_components`; `tests/test_upgrade_recovery.py::test_display_decision_table`; `tests/test_upgrade_recovery.py::test_display_denial_stops_before_materialization` |
| C15: secret delivery/history boundary | `tests/test_project_runtime_plan.py::test_project_runtime_plan_contains_only_in_container_contract`; `tests/test_pycharm.py::test_bound_secret_must_exist_on_host`; `tests/test_project_commands.py::test_project_run_records_known_good_configuration_only_on_success`; `tests/test_config_history.py::test_first_success_records_one_private_generation` |

## 5. Original audit disposition

| Gap | Correction and regression |
|---|---|
| G1 | Shared artifact admission; unknown checkout/resolution regressions pass. |
| G2 | Explicit local-answer provenance, separate from existing repository advice. |
| G3 | Scoped new fingerprints and semantic interpretation of legacy fingerprints. |
| G4 | Registry invariants enforced by every lock reader and by pure assessment. |
| G5 | Full admitted-document writer; unsupported structure refused intact. |
| G6 | Required ordinary/binding nodes participate in registry-driven elicitation. |
| G7 | Typed legacy decisions; no `bool("false")` permission conversion. |
| G8 | Error accumulation by node, including binding/secret/adopted-state families. |
| G9 | Explicit false wins in the actual launcher; project configuration excludes ambient compatibility options. |

The audit's tests remain in `test_configuration_contract.py`, with no expected-
failure markers. The refactor additionally closes related consequences of the
same rules: legacy-grant resurrection on unset, stale host bindings under force,
ambient path/token injection, duplicate runtime effects, identity-question name
collisions, saved local-base re-elicitation, tampered generated output, and unsafe
project-mount representations.

## 6. Verification and acceptance

Run the repository gate from `devcapsule-src`:

```text
.venv/bin/python -m nox -s build
```

The final validation counts and measured coverage are recorded in the selected
[status file](CURRENT-STATUS.md). The gate includes compilation, shell syntax,
pytest, mypy, source CLI smoke, PEX construction and packaged-executable tests.
Host-sensitive tests are explicitly outside that gate; no container or GUI was
launched in this work.

Coverage is evidence about executed conditions, not a universal proof. The case
map and arguments above establish the intended compositions; the new admission,
assessment/execution and pure-resolution boundaries are measured separately so
coverage of an isolated helper cannot be mistaken for coverage of its callers.
The entire CLI is not claimed to have 100% coverage. Future schema changes and
actual host upgrade/display acceptance retain their stated release obligations.
