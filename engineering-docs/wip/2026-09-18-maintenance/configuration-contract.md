# Configuration lifecycle contract

Status: complete contract for review, requested by the owner on 2026-09-20.
The [correctness argument](configuration-correctness.md) separately assesses
the implementation. A requirement written here is not a claim that the code
already satisfies it.

## 1. What configuration must accomplish

A project describes the environment collaborators should receive. A developer
chooses personal settings and what that environment may access on their
machine. Resolving combines those inputs into an inspectable plan. Running
executes that plan, with any explicit choices for this invocation. Upgrading
the tool must preserve the meaning of decisions the developer already made.

Five principles follow:

1. An input has an owner. Reading another owner's input does not acquire their
   authority, and generated output cannot become an independent authority.
2. A choice has a type and a meaning. Absence, explicit omission, denial,
   acceptance and an invalid answer are different states.
3. Derived facts depend only on their actual inputs. A change outside that
   dependency set cannot invalidate them.
4. Changes are explicit, localized and recoverable. A failed validation cannot
   publish a partially valid plan or silently discard unrelated decisions.
5. A new reader must preserve the semantics of supported older input. A new
   version number alone does not make an earlier user decision obsolete.

These principles come from adopted [D-0001](../../decisions/product/d-0001-capability-first-cli-model.md),
[R-COMPAT-001](../../requirements/devcapsule/r-compat-001-client-upgrades-require-no-user-action.md),
[D-0007 and amendments](../../decisions/product/d-0007-resolution-matrix-model-and-interface.md),
[D-0008](../../decisions/product/d-0008-known-good-configuration-history.md),
[D-0009](../../decisions/product/d-0009-launcher-delivers-identical-runtime.md),
and the explicitly settled sections of the
[V1 design](../../design-notes/devcapsule/v1-user-experience.md).
[D-0004](../../decisions/product/d-0004-configuration-resolution-and-guided-run.md)
remains a proposal; its implemented resolution/run split informs the operational
profile below, without making its unimplemented proposals accepted features.

## 2. The inputs and their authority

| Symbol | Artifact or input | Owner and meaning |
|---|---|---|
| `P` | Repository `.devcapsule/devcapsule.toml` | Project identity, capability needs, ordinary declarations and project settings, host recommendations and justifications. No authority over a developer's host. |
| `L` | Repository `.devcapsule/devcapsule.<platform>.lock` | One project-selected environment: platform, exact base and component artifacts, acquisition metadata and recipe. A reproducibility record, not permission to execute. |
| `W` | Workstation defaults and restrictive policy | Developer/workstation authority. D-0001 defines this layer; the current CLI does not implement the general `config.toml` overlay/policy mechanism. |
| `C` | Developer-owned checkout TOML | Ordinary answers, omissions, state and secret-source bindings, and explicit authorization decisions for this observed checkout. |
| `O` | Explicit invocation answers | Developer-owned, temporary overrides in the subset supported for this command. Never stored in `C` or the generated resolution. |
| `K` | Trusted schema, component catalog, runtime contracts and matrix delivered by the CLI | Defines node types and effects; provides selections when explicitly generating a lock. It must interpret standing locks compatibly. It cannot turn new recommendations into consent. |
| `E` | External observations | Platform, local image identity/capabilities, path existence, secret availability, environment variables and Docker state. These determine feasibility; they are not implicit new grants. |
| `R` | Generated `devcapsule.resolved.toml` | Derived plan plus source fingerprints. A cache/checkpoint of resolution, **not another input layer**. |

Managed state, downloads, built images and successful-run history are outputs
or resources. They do not add configuration precedence. A platform lock selects
formation inputs; it is not a generic overlay over the manifest.

There is one logical typed tree, distributed across these owners. It is not a
recursive TOML merge. For each node we need its canonical name, family, domain,
requiredness, owner, allowed sources, dependency set, default/absence behavior,
and runtime effect. Recommendations are metadata beside a node, never values
in the ordinary precedence chain.

For an ordinary node, D-0001's precedence is:

```text
safe default < workstation default < project value < checkout answer < run-once answer
```

The last **specified** answer wins, subject to all applicable restrictive
policy. An explicit omission is a specified answer, not a missing one. Security
authorization instead uses the decision rules in section 5; project content
cannot win a precedence contest and grant itself access.

## 3. The current V1 tree and storage

The implemented tree has these concrete branches. Quoted names such as
`"runtime.memory-limit"` are canonical leaf names, not arbitrary Python or
TOML traversal expressions.

```text
Repository manifest P
  devcapsule-schema-version
  project: name, creator, slug, mount
  capabilities.need[]
  configuration.values.<name>: type, required?, description?, runtime-effect?
  host.<curated-boundary>.recommended: value, justification, enables?
  workflow / workflow-type and other project metadata

Platform lock L
  devcapsule-lock-format-version, platform, resolution-matrix-version
  capabilities-digest; historical manifest-digest (not a loading gate)
  base: immutable reference, optional recognizable build mnemonic / identity
  components: interactive-surface and per-component exact artifact metadata
  materialization: recipe, recipe-version
  or historical image.reference instead of formation inputs

Checkout input C
  devcapsule-checkout-schema-version
  project: creator, slug
  checkout.path
  configuration.values.<name> = typed scalar
  configuration.omitted-values[]
  configuration.bindings.host-directory.<logical-resource> = path
  configuration.bindings.host-environment.<logical-secret> = variable name
  authorization.<node>: value, recommendation-digest
  authorization.base-image: reference, lock-digest, optional image-id
  state.adopted.<resource> = path                  (legacy explicit binding)
  host.<node> = value                            (legacy explicit decision)

Generated resolution R
  devcapsule-resolved-schema-version
  sources: manifest, platform-lock, checkout-input, workstation-config
  runtime: selected component, project mount, image or derived runtime effects
  configuration: normalized values and explicit omissions
  state: adopted mappings and resolved bindings
  secret.bindings.host-environment: source names only
  authorization: effective recorded decisions / selected base
  host: retained legacy decisions
```

All four artifact format versions are currently `1`. These are independent
of CLI package version, matrix version, image recipe version, image metadata
version and runtime-plan version. Equality of one pair implies nothing about
another pair's compatibility.

`creator` and `slug` address the developer's project directory under
`$XDG_CONFIG_HOME/devcapsule/projects/<encoded-creator>/<encoded-slug>/`.
The usual XDG fallback is `~/.config`. The default checkout uses
`devcapsule.checkout.toml` and `devcapsule.resolved.toml`; additional checkouts
use paired `checkouts/<name>.checkout.toml` and `.resolved.toml` files.
Canonical observed source path selects the record. Identity alone cannot
transfer permissions to another clone. Identity relocation remains an explicit
open design issue; changing an address is not consent to inherit a different
record.

Local records are written mode `0600`. They must contain no secret values.
Directory state and caches use the XDG data/state/cache roots according to
lifecycle, outside the configuration tree.

The current ordinary-value implementation accepts declarations and checkout
answers; it does not implement arbitrary project default values or the general
workstation overlay. An arbitrary declared value has no magical effect on a
container: delivery requires defined metadata. The currently implemented
ordinary runtime effect is `docker.memory-limit`. The lower launcher also
reads legacy environment settings; those inputs must respect the same authority
and precedence rules and are part of the correctness audit.

## 4. Ordinary values, absence and bindings

| Family | Accepted domain / source | Meaning when unanswered |
|---|---|---|
| Ordinary `set` | Declared nonempty string, integer excluding booleans, boolean, or positive memory size `B/KiB/MiB/GiB/TiB` | Required: incomplete. Optional: absent in current V1; a declared safe default may apply in an implementation that supports one. |
| Directory `bind` | A selected component's declared resource, with `host-directory:PATH` naming an existing canonical directory | Use the declared managed-state convention; never discover and mount the developer's host home implicitly. |
| Secret `bind` | A selected component's declared secret, with `host-environment:VARIABLE` matching its permitted source name | Required: incomplete. Optional: no delivery. A bound but unavailable source prevents the use that needs it. |
| Authorization | Curated decision domain, described below | Safe denial for optional host access; missing mandatory executable/acquisition consent prevents realization. |

The ordinary node state machine is:

| Operation | Resulting state |
|---|---|
| `set n v` | Validate `v`, store a typed value, clear any explicit omission. |
| `set n none` | For an optional node, remove a value and record explicit omission. Refuse for a required node. |
| `unset n` | Remove an optional recorded answer/omission and return to silence. Refuse required nodes or nodes with no recorded answer. |
| `set n default` | Resolve a declared default immediately and store the concrete answer; refuse if no default exists. Current ordinary declarations have no implemented default. |

`default` is never a deferred instruction to follow future defaults. `none`
is family-specific: ordinary omission, host/acquisition denial, or invalid for
a base with no denial state. They are reserved input words, not string values
to persist under another interpretation.

Bindings are not innocuous scalar values. `bind` is the explicit developer act
authorizing that resource mapping; it must name exposure, sensitivity and
sharing consequences. A secret binding stores only a provider reference;
resolution neither retrieves nor serializes the value. Runtime delivery occurs
late through the declared channel. Current environment delivery exposes the
secret to capsule processes and Docker inspection, but not in CLI diagnostics,
the image, or persisted TOML. Supplying a secret does not authorize networking.

## 5. Authorization and trust

For a security-sensitive node, the relevant states are unanswered, allowed,
denied, stale, invalid and no longer declared. These are not truthy/falsy
values. In particular, the string `"false"` is not permission.

| Node | Explicit allow / selection | Explicit denial | Decision binding |
|---|---|---|---|
| `docker-daemon` | `host-socket` | `none` | Current recommendation or stable built-in capability question |
| `network` | `host`, where declared | `bridge` | Current project recommendation |
| `development-sudo`, `host-browser` | `true` | `false` | Current recommendation or stable built-in capability question |
| `host-x11` | `true` | `false` | Built-in host-session question; never project-authorized |
| `base-image` | Exact lock-recommended published digest; or explicitly inspected local immutable identity | No persisted denial state; declining leaves the environment incomplete | Entire selected lock, and local image identity where applicable |
| Selected vendor acquisition | `true` after review | `false`; selected acquisition then cannot proceed | Acquisition name and exact component metadata |

An authorization is valid only for its recorded value, observed checkout and
decision dependencies. The old answer remains visible after those dependencies
change, but cannot silently be treated as renewed consent. A stale denial stays
a denial in the review: keeping it is a valid choice, not an instruction to
accept the new recommendation.

Project recommendations can be accepted explicitly with `authorize n default`.
That selects the recommendation **now**. It does not mean “always accept what
this project recommends.” An unrelated ordinary value edit cannot renew or
invalidate a host decision. A component/lock edit may invalidate base trust
even when the base reference itself stays the same: the adopted base decision
covers the selected formation, not just its label.

A local base tag is a locator; its inspected image ID is the trust identity.
Moving the tag cannot change the accepted bytes. Recovery may offer the recorded
immutable ID if still present and valid. It cannot promise that Docker still
has that image. Another published digest requires reviewed project metadata;
an old published digest is not a valid recovery answer under a new lock.

Legacy direct `[host]` decisions are developer-owned input, not project grants.
They still need type/domain validation. A current explicit denial outranks a
legacy/workstation allow. No later planner may reinterpret it through Python
truthiness or replace it with an inherited environment value.

## 6. Starting from zero

There are three owner-side initialization states:

1. **No manifest or lock:** derive safe identity fields and environment facts;
   ask for intent that cannot be derived; create the project artifacts.
2. **Partial initialization:** honor existing authored content and complete
   missing artifacts. An interrupted attempt is repairable without deleting
   configuration or authorizations.
3. **Already complete:** ordinary init refuses with the deliberate alternatives.
   The implemented exception accepts supplied checkout answers and resolves
   them; `--regenerate` explicitly asks for a new lock from the current matrix.

When initialization succeeds, valid `P`, usable `L`, this checkout's valid `C`
and fresh `R` exist. “Runnable” means configuration-complete; registry/network
availability, Docker, display availability and successful component execution
remain external preconditions. Init does not build the environment.

For each required answer, look in this order: explicit command line, earlier
answer in this invocation, a still-valid answer in the owning artifact, a
safe derivable default, and finally an interactive prompt. Noninteractive
omission of required decisions reports all reachable missing questions and
their exact remedies. It grants nothing. A saved local-image choice is an
existing answer too; it must not be replaced merely because it is not the
recommended base.

An owner may author a host recommendation and explicitly accept it for their
own checkout in one interaction. Those are two writes with distinct authority.
Reading a recommendation from an existing manifest is not that interaction.
Neither a collaborator running init nor a deleted local configuration directory
may cause repository recommendations to become local grants automatically.

For a new checkout with `P` and `L` already present, create/register separate
local input, show the required choices, accept safe managed state, collect
developer decisions, and resolve. A second checkout needs its own record; it
does not inherit another checkout's consent.

The lockless-consumer case and the ownership boundary of `init --regenerate`
versus `config need` have contradictory/unfinished historical specifications.
The current CLI refuses a missing platform lock, and `config need` edits the
project's need and lock. This contract does not silently decide a new fallback
environment or a checkout-local capability experiment; see section 11.

## 7. Changing one or several options

Each `set`, `bind`, `authorize` or `unset` operation validates the relevant
artifact/schema and proposed answer before replacing `C`. It must preserve
unrelated answers, grants, denials, bindings and state. Unsupported content
must be preserved when safely understood, or cause refusal without rewriting;
silently dropping it is not a migration strategy.

For several options, perform several such edits and one final `config resolve`.
Intermediate `C` may be incomplete; it remains inspectable. A sequence of CLI
commands is **not** an all-or-nothing transaction: if the second command fails,
the first successful change remains. The old `R` is not silently refreshed by
each edit. Commands accepting multiple carriers must validate them consistently
with the same node domains and disclose their commit boundary.

Two valid edits to independent nodes commute: either order produces the same
semantic answers. Replacing one node twice leaves the last explicit answer.
Neither property allows bypassing cross-node constraints, such as a resource
being both adopted and directory-bound, two names controlling one effect, or
a name belonging to two families.

Project capability/lock updates are separate acts. Ordinary checkout edits
must not rewrite the repository. `config need` is the current explicitly
documented exception despite its placement under `config`; it grows the
project's need, regenerates its lock and then attempts local resolution.
It and init use per-file writes and may leave repairable partial state after
refusal. There is currently no multi-artifact rollback transaction.

## 8. Resolution, inspection and execution

**Resolve:** interpret supported versions, select the observed checkout,
derive the unique typed node registry, validate all node answers and cross-node
constraints, then publish one complete `R`. Missing/invalid answers are not
silently replaced by grants or recommendations. Independent errors should be
reported together. Resolution may establish safe records/state and inspect a
selected local base; it must not download components, build, launch or read
secret values.

**Inspect:** show recorded choices, recommendations, omissions and pending
decisions even when configuration has drifted. Unknown schemas must be reported
as unsupported, not interpreted as known. A malformed file may prevent complete
inspection, but the error must identify that input without losing it. Current
`config list` creates an empty local record and unresolved placeholder when
absent; that limited side effect must not be confused with the pure assessment
function or with resolving/granting anything.

**Run:** require supported, valid input and an explicit resolution checkpoint;
verify freshness, validate permitted run-once answers, then plan and perform
external work. Runtime consumers must preserve the decisions established by
validation. The current run-once subset is host authorization and declared
memory-limit effects; persistent base/acquisition decisions and binding changes
are not run-once operations. General `--bind` and arbitrary ordinary run-once
values are not implemented.

Normal V1 run refuses missing/stale `R` and names resolve. `--force` is a
conspicuous one-run stale-output exception, not a permission or schema bypass.
Raw Docker options after `--` are an explicit escape from the modeled plan;
conflicting launcher-owned options are refused. The ordinary configuration
correctness claim excludes arbitrary deliberate passthrough effects.

Before component acquisition/build, validate the selected base's platform and
identity and explain display selection. Explicit X11 true selects host X11;
false requires a contained-capable base or refusal. An unanswered choice uses
contained display on a capable base; historical bases retain their documented
X11 behavior. Preserving that historical behavior is distinct from inventing
an explicit grant for a new base. Report the selected transport and alternatives.

Materialization verifies immutable inputs and reuses only an exact formation.
The invoking executable's digest belongs to formation identity under D-0009;
a CLI upgrade can legitimately cause a new image build without changing project
pins or requiring new consent. Explain such a build before it starts.

After a successful zero-exit run, D-0008 records verbatim local input/resolution
history, deduplicated by content; failure to record warns without changing the
run's exit status. A snapshot alone does not prove that a future run will
succeed under different external state or without the run-once choices used.

## 9. Freshness and upgrade transitions

Three concepts must remain separate: **supported format**, **fresh derived
output**, and **still-valid authorization**. A fresh digest does not establish
supported schema or valid consent. A stale plan does not imply every user
answer is stale.

| Change | Required behavior |
|---|---|
| TOML formatting/comments/key order only | No semantic change or reconsent. |
| Ordinary value/binding change | Preserve unrelated decisions; invalidate affected local derivation; resolve explicitly. |
| Recommendation value/justification changes | Show the old answer and current question; renew/change exactly the affected authorization. |
| Lock/base/component change | Preserve personal configuration; reassess base and affected acquisition decisions; keep unrelated host decisions. |
| Workflow or unrelated descriptive metadata change | Must not invalidate environment derivation that does not consume it. |
| New CLI/matrix, unchanged project and checkout | Continue ordinary work without requiring a new configuration decision or rewriting pins. A new matching-runtime formation may be needed. |
| Old known schema read by a new CLI | Decode/normalize compatibly with the same effective values and permission boundaries; no user-action requirement merely because representation is old. |
| Unknown future/unsupported schema | Identify the unsupported artifact, refuse mutation/execution, and leave bytes intact. Never guess a version or downgrade it while editing an unrelated node. |
| Changed local image behind an accepted tag | Refuse identity mismatch; do not authorize new bytes. |

Fingerprints identify semantic dependencies, not file timestamps or release
numbers. The current implementation hashes complete parsed `P`, `L` and `C`
for resolution; that is conservative but violates the narrower scoped-digest
requirement for irrelevant metadata. Authorization fingerprints are separately
scoped to their questions, with base trust deliberately covering the lock.

## 10. The schema-evolution obligation

For each artifact type and every **supported released predecessor**, a new
reader needs a defined interpretation. Call it `decode(version, bytes)`. If
representation changes, a normalization/migration `N` is correct only if:

```text
effective_values(N(old)) = effective_values(old)
allowed_host_access(N(old)) = allowed_host_access(old)
selected_artifacts(N(old)) = selected_artifacts(old)
```

The equalities are semantic: a byte-for-byte image match is not promised when
D-0009 intentionally replaces the runtime executable. State bindings, denials,
explicit omissions and exact artifact trust must retain their meaning.
Applying normalization twice must not accumulate changes. Unknown fields cannot
be silently discarded, and former implicit defaults cannot become broader
permissions.

A reader may normalize in memory or perform an explicitly designed durable
migration. The contract does not require one mechanism. Durable migrations must
be recoverable and must never relabel unconverted content as a newer schema.
Derived output may be regenerated compatibly, but a CLI-only upgrade may not
make the user perform that repair. Existing digest algorithms/interpretations
must remain readable or be migrated without falsely presenting a changed
question. Migration must not silently re-lock against the current matrix.

Before any schema, component-contract, recipe or default change ships, the
release must exercise artifacts generated by supported older releases against
the new client. Using the new client to generate both sides proves nothing
about migration. A justified exception must be explicit in that release's notes
under R-COMPAT-001; a generic refusal is not the exception policy.

No successor configuration schema or general migration framework currently
exists. The version-1 historical fixtures establish specific compatibility
cases, not this universal future obligation. The code cannot yet supply a
general proof for a future schema bump.

## 11. Explicit scope limits and unresolved choices

The following remain visible design obligations, not choices made by this audit:

- The general workstation overlay/restrictive policy and generic project value
  defaults are adopted architecture without a complete implemented interface.
- The missing-platform-lock consumer experience and the exact project/local
  mutation boundary of regeneration require reconciliation with the
  [existing owner-accepted interim behavior](../../wip/2026-08-09-project-management/intake/2026-09-06-component-catalog-init-regenerate-versus-config-semantics.md).
- Identity relocation, fully specified retention/restore semantics and the
  supported historical release/recipe matrix are not implemented as one policy.
- No API can guarantee that a removed registry artifact, missing local image,
  absent display or missing secret becomes available. Correctness requires
  actionable failure while retaining decisions.
- The argument assumes serialized configuration edits and stable inputs during
  one operation. The current implementation has per-file atomic replacement,
  not cross-process transactions, a multi-file commit or a locked snapshot for
  an entire running session. Concurrent mutation needs a separate contract.

These boundaries prevent a proof from depending on a feature that is only a
proposal, or on an assumption nobody stated.
