# Capability configuration: implementation and test correctness argument

Review date: 2026-10-06. Branch: `ws-component-catalog/intellij-idea`.
Implementation and tests reviewed at commit
`99ff26ac564368427f77773ac0a4c2beaa257eea`, the branch HEAD when this review
started. The documentation commit containing this argument is necessarily later.
Every source link below fixes both the commit and its original line numbers;
none follows a moving branch. Paths are relative to the repository root.

**Conclusion:** the implementation supports the mandatory-closure, ownership,
validation and bounded-degradation arguments below, under their stated
preconditions. A universal claim of correctness would be false: this review
reproduced loss of an optional tool's local version pin when toggling its
omission. The existing passing tests do not cover that sequence. The
[counterexample and reproduction](../../bugs/devcapsule/2026-10-06-optional-omission-loses-local-version-pin.md)
are part of this review, not a fix to the cited snapshot.

## 1. Contract and scope

The independent specification is [R-CONFIG-001, lines 17–79][requirement]:
projects own mandatory/optional capabilities and SDK constraints; developers
own personal tools; supported commands author configuration; readers may omit
unsupported optional functionality without weakening mandatory requirements,
integrity or host-access boundaries. There are no task/workstream profiles.

The proof obligations concern policy parsing, effective-lock construction,
command persistence and launch admission. They assume schema-admitted documents,
policy values produced through the validating entry points, a finite internally
consistent component catalog, and ordinary filesystem rename semantics. Direct
construction of the frozen value objects does not itself validate their fields.
SDK and artifact identities depend on trustworthy catalog/lock metadata; these
functions do not inspect an installed SDK's executable to establish its version.

For persistence reasoning, assume one writer and recovery on the same platform.
The implementation provides neither a configuration-wide interprocess lock nor
power-loss durability. Reader tolerance is a property of readers containing this
implementation; it cannot retrofit these semantics into already shipped binaries.
The self-hosting baseline/candidate transition and a real next-session container
launch remain separate acceptance obligations.

## 2. Argument for the implementation

### 2.1 Representation invariants

Let `R` be required project capabilities, `O` optional project capabilities,
`L` local selections, and `W` local omissions. After parsing:

- Names are nonempty, trimmed strings without NUL, deduplicated and sorted.
- `R ∩ O = ∅`; legacy `need` and new `required` cannot coexist.
- Every SDK-major constraint names an element of `R` and has a positive integer
  value. The exact-type check excludes Python's boolean-as-integer case.
- `L ∩ W = ∅`, and validation against the project requires `W ⊆ O`.

Each condition is checked before return in
[`configuration/capabilities.py:15–75`][policy]. Parsing deliberately does not
consult the catalog, so an unknown optional name survives as intent. This is
limited tolerance, not arbitrary-schema acceptance: unknown local selection
fields are refused. Normalized ordering gives deterministic value comparison.

### 2.2 Mandatory provider closure cannot be weakened by optional omission

Define `P(c)` as the transitive component dependency closure of capability `c`.
[`resolution_matrix.py:297–304`][providers] starts with its provider, appends only
unseen dependencies, and visits the growing list. In a finite valid catalog,
each component is appended at most once; the algorithm terminates and includes
every reachable dependency. Base-supplied capabilities have an empty closure
and require separate base-service evidence.

For a non-legacy effective lock, [`capability_selection.py:108–156`][selection]
establishes the following loop invariant:

```text
After processing mandatory prefix Q of (R followed by L):
    keep contains the union of P(c) for every c in Q;
    each such provider has supported component metadata;
    each base-only capability in Q is supplied by a recognized base.
```

The empty prefix satisfies it. `supply` checks the complete closure before
`keep.update`; a failed mandatory check raises instead of returning a weakened
lock. Induction gives `union(P(c), c in R ∪ L) ⊆ keep`. SDK checks then succeed
or abort. The optional loop only adds to `keep`: skipping an omitted or
unsupported capability cannot subtract a mandatory dependency. Filtering the
source components by `keep` therefore preserves the mandatory closure. The
interactive selector survives only when its component survives. Reconstructed
provider evidence comes from this reader's catalog, not the contributor's claims.

This is a structural supply argument. Artifact format, integrity metadata,
authorizations and realization still have their own checks. Deep copies at
entry and projection preserve the caller's documents. The narrowly guarded
legacy fast path returns a copy without re-resolving old locks; it does not
claim the new closure proof for arbitrary legacy documents.

### 2.3 Shared requirements and personal choices remain separate

[`capability_commands.py:109–191`][writer] accepts exactly one edit scope.
Shared edits reject newly introduced IDE/agent choices, while grandfathering
existing shared choices until explicit migration. Local edits replace the local
capability record and write only its checkout file. They preserve other checkout
fields, and copy retained personal providers' exact metadata before composing
the candidate. Pending local activation blocks a competing edit.

[`capability_selection.py:68–105`][compose] overlays pinned local providers on
an owned copy. A conflicting legacy shared IDE is rejected rather than silently
replaced. [`storage.py:292–310`][load] additionally rejects a local version set
for another platform and requires an IDE before producing an executable
selection. A project declaration itself can validly have no IDE.

Version-set admission reuses the policy projection
([`version_sets.py:399–418`][versions]); following project recommendations
removes the explicit version set while composing personal choices again
([`version_sets.py:574–585`][follow]). Inactive consent for known acquisition
nodes remains stored without making those tools active
([`authorization.py:519–528`][consent]). This is not a grant of new host access.

**Qualification:** retained-pin preservation is established for the tested
reselection case, not all command sequences. Section 4 gives a counterexample
when omissions are applied to an explicit version set.

### 2.4 SDK-major constraints are hard admission checks

[`capability_selection.py:58–65`][generate] requires equality between every
requested and established major; an unknown major also fails. The catalog
lookup in [`resolution_matrix.py:312–322`][providers] recognizes base references
for base SDKs and the locked .NET component version for .NET. This establishes
agreement with metadata, not independent verification of artifact contents.

Local composition and version-set selection both invoke the policy projection.
A local base image identity is refused when SDK constraints exist
([`model.py:49–53`][model]); an execution-time differing base override is also
refused before image lookup ([`environment_realization.py:56–70`][override]).
These close those override paths rather than treating an unknown base as evidence
that a major constraint is satisfied.

### 2.5 Conservative writers and read-only validation

[`generate_lock`, lines 28–55][generate] authors known capabilities. For an
unknown optional capability already present, it preserves explicitly recorded
provider metadata only if it exists and does not conflict with generated
metadata; otherwise it refuses. This is preservation of that opaque provider
payload, not a promise that every unknown field anywhere in a lock survives a
regeneration. Unknown required capabilities cannot be authored as supported.

[`check_documents` and `check`, lines 71–106][check] validate schema, the usable
projection, executable artifact metadata and declarations without registration,
acquisition or persistence. Unsupported optional data is excluded from the
executable projection. Malformed metadata of an otherwise admitted artifact is
not excused merely because its capability is optional.

The writer validates the starting pair and proposed pair before promotion.
Preview follows the same candidate construction and validation, then bypasses
the write. Successful offline checking establishes neither downloadable URLs nor
launch permission. Initial creation validates and serializes the local candidate
before promoting shared files ([`initialize`, lines 194–234][init]).

### 2.6 Shared-file recovery has an explicit commit boundary

[`promote` and `recover`, lines 23–68][journal] record both endpoint texts
in a journal, replace the lock, replace the manifest, then delete the journal.
[`storage.py:218–245`][atomic] uses a temporary file in the destination directory
and rename for each replacement; cooperating entry points refuse a pending
journal. A process interruption between writes is therefore detectable.

For distinct before/after manifest texts, recovery follows this state table:

| Observed manifest | Observed lock | Recovery outcome |
| --- | --- | --- |
| Before | Before or after | Restore before lock; remove journal |
| After | Before or after | Complete after lock; remove journal |
| Neither endpoint | Any | Refuse; preserve evidence |
| Either endpoint | Neither endpoint | Refuse; preserve independent edit |

The manifest selects an endpoint; recovery never needs to infer progress from a
partially parsed lock. Snapshot reads are text reads, so this is not a promise
of preserving arbitrary input newline encodings byte-for-byte. Missing original files use empty strings, allowing initial
creation rollback. Repeated recovery after journal removal is a no-op. If the
before and after manifest texts are identical, the after branch wins: recovery
can roll forward even before the manifest replacement. The defensible claim is
one consistent endpoint, not unconditional rollback of every pre-commit failure.

Limits matter: individual renames do not provide an atomic multi-file read to
noncooperating/concurrent readers; there is no `fsync` or writer lock. The journal
uses the current platform's lock path, so cross-platform recovery is not proved.
If recovery itself encounters I/O failure, successful immediate repair is not
guaranteed. Finally, initial local-checkout persistence follows shared promotion
at lines 230–231: failure there can leave a valid shared project with incomplete
local setup. The three documents are not one atomic transaction.

### 2.7 Optional-only freshness does not waive changed local decisions

[`fingerprints.py:10–41`][fingerprints] records full source digests plus a
mandatory baseline: required policy, SDK constraints, local providers and their
metadata, base/platform/image/materialization, and other configuration-relevant
manifest content. It excludes optional-only policy/provider content and rejects
missing required provider evidence. Evidence is reconstructed by the selector
before the pure model consumes it.

[`ExecutionConfiguration.load`, lines 36–62][execution] reconciles a stale
resolution only when stale inputs are limited to manifest/platform lock, review
is ready, and a nonempty old baseline equals the candidate's baseline. Thus a
changed checkout digest prevents this exception; a changed mandatory baseline
cannot pass its equality condition. Normal acceptance still runs afterward.
This is conditional reconciliation, not automatic acceptance of every optional
change: new consent requirements, for example, can make review unready. The
existing explicit `force` behavior is a separate policy and is not covered by
this no-waiver claim.

### 2.8 Download degradation is bounded and preserves integrity

[`materialization.py:188–238`][acquire] gives URL acquisition failures a distinct
`ArtifactUnavailable` type. Downloaded-byte digest mismatch raises the ordinary
`CliError`, outside that type. [`environment_realization.py:228–261`][degrade]
maps a failed URL back to components, refuses any intersection with mandatory
closure, and omits every optional capability whose closure needs those components.
It returns a reviewed/resolved copy and performs no configuration writes.

On a successful reduction, at least one failed nonmandatory component loses all
of its selected optional providers and leaves the effective component set.
That finite set strictly shrinks, so [`project.py:1185–1205`][retry] cannot
retry forever through repeated successful reductions. A failure with no eligible
reduction propagates. Mandatory/local downloads, integrity mismatches and general
build failures are not silently waived. After a reduced successful run,
[`project.py:1322–1334`][certify] suppresses recording the original full stored
configuration as known-good.

## 3. Separate argument for the tests

### 3.1 What makes these tests meaningful

A test has its own correctness obligation: construct an admitted starting state,
exercise the intended boundary, and compare an observable result with an oracle
derived from the requirement. Passing a test whose expected value merely repeats
the production algorithm is weak evidence.

The shared [fixture, lines 24–45][fixture] creates a real legacy project under
`tmp_path` and redirects `XDG_CONFIG_HOME`. This isolates project and checkout
writes; it does not claim to isolate every environment variable. Real catalog
resolution supplies structurally valid pins. Assertions then use literal expected
component sets, byte snapshots, explicit error classes/messages, or sentinel
values, rather than reimplementing the selection algorithm. Catalog reuse still
creates a common-mode risk: these tests do not independently audit vendor pins.

Synthetic file edits are test fixtures representing incoming configurations or
interrupted writes; they do not authorize hand-editing a real project's config.
Monkeypatches are limited to external effects or targeted failure injection and
are restored by pytest. The important oracles and their limits follow.

| Test location (all in `devcapsule-src/tests/`) | Oracle and defect it would expose |
| --- | --- |
| [`test_capability_policy.py:48–79`][parse-tests] | Explicit invalid-input classes must raise. A literal normalized dictionary checks deduplication and unknown optional preservation; the round trip is supplemental, not the sole oracle. |
| [`:82–148`][closure-tests] | Literal component/provider sets, unchanged deep-copied inputs, warning contents and required/optional paired failures. Rider still needs `dotnet-sdk` when optional `dotnet` is omitted; deleting that dependency must fail. |
| [`:151–192`][writer-tests] | Legacy copy identity, byte-for-byte shared-file preservation under local edits/rejected edits, and absence of a checkout record after preview/check. These would expose ownership leaks and writes on these paths. |
| [`:195–226`][recovery-tests] | Both synthetic interruption endpoints compare exact before/after bytes, journal removal and idempotence. An injected manifest-write `OSError` must restore the initial byte snapshot. |
| [`:239–279`][freshness-tests] | A hypothetical newer optional contribution preserves effective components/runtime and shared bytes. A changed SDK major fails; changed local authorization remains stale. |
| [`:282–310`][init-tests] | Literal shared policy and component sets exclude implicit personal tools; malformed creation leaves both project and local config absent. This checks validation failure, not late disk failure. |
| [`:313–332`][pin-tests] | Distinct sentinel Playwright/Codex versions survive an IDE replacement, the old IDE disappears, and shared bytes remain equal. Sentinels detect accidental repinning. |
| [`:335–361`][conflict-tests] | Malformed journals and independent manifest/lock edits must leave every shared byte intact; an interrupted initial creation removes its candidate files. |
| [`:364–421`][boundary-tests] | Missing/malformed pins, conflicting IDEs, wrong platform, unknown SDK knowledge, pending activation and a local base override fail at their intended boundaries. |
| [`:424–464`][download-tests] | Derived omission leaves the original selection unchanged and a fresh disk load still contains Playwright. Real local-file wrong bytes raise a digest error of a different type from an injected URL failure. |
| [`:467–510`][run-tests] | Recorded realization calls show retry, a launch counter proves one launch, and a forbidden known-good recorder fails immediately if invoked. Mandatory/unmatched acquisition failure returns nonzero. |
| [`:513–561`][cli-tests] | CLI flag incompatibilities, explicit no-IDE diagnosis, retained legacy surface, wrong-platform version sets and incomplete provider evidence are exercised. |
| [`:564–593`][override-tests] | A differing base override fails; an identical reference reaches the injected image-lookup boundary. Actual required-artifact URLs and unowned artifacts cannot be omitted. |
| [`:596–614`][consent-test] | Removing a licensed local agent still permits resolution while the entire saved authorization table remains equal. |
| [`:616–644`][artifact-tests] | Each malformed artifact field has a matching rejection; checking a corrupt optional candidate rejects it without changing shared bytes. |

The tests are finite examples, not exhaustive enumeration or a machine-checked
proof. Several rejection tests accept any `ProjectConfigurationError`, so they
prove refusal but may not identify the exact rejecting condition. Snapshot
helpers cover shared files; they do not detect every possible write elsewhere.
The orchestration tests mock image realization and IDE launch: their conclusions
concern control flow, not Docker behavior or a graphical developer experience.
The interruption tests do not kill a process during `rename`, simulate power
loss, or run competing writers. No mutation-testing claim is made.

### 3.2 Architecture and packaged execution provide different evidence

[`configuration/test_architecture.py:8–72`][architecture] constructs an AST import
graph, including function-local imports. DFS checks reject cycles; transitive
reachability rejects dependencies from the designated pure core to named adapters.
These are structural oracles independent of the policy's output computation.
They cover recognized static imports, not arbitrary dynamic import machinery,
and the declared core/adapter sets remain a reviewed architectural input.

[`integration/test_pex_runtime.py:317–339`][pex] runs the built executable in a
subprocess from an isolated project, creates shared policy, selects personal
tools, checks the contract, and rejects Python major 4. It compares shared bytes
after both local selection and rejection. This adds packaging/CLI/process-boundary
evidence beyond in-process calls; it still does not launch a container or test
an older released reader.

### 3.3 Coverage measures reach, not the validity of the oracle

The [implementation checkpoint's recorded evidence][evidence] reports 1,245
passing unit cases (87 in the new policy module), ten packaged integration
cases, and the full build gate. One pre-existing xfail and one non-strict xpass
remain. These are observations of that run, not a theorem about future runs.

The saved local Coverage.py/diff calculation reports **574/574 changed executable
lines (100%) and 199/204 outgoing branch arcs (97.55%)**, relative to merge
`710fd04`. Both exceed the requested 90%. The denominator is changed production
code, not the entire repository or test code. The five uncovered arcs are:

| File under `devcapsule-src/devcapsule/` | Arc and unexercised alternative |
| --- | --- |
| [`configuration/capability_commands.py`][check] | `84 → 92`: formation validation without a base |
| [`configuration/capability_commands.py`][writer] | `171 → 169`: retained provider has no old metadata |
| [`configuration/capability_commands.py`][writer] | `180 → 183`: local version set has no removable old surface |
| [`configuration/capability_selection.py`][compose] | `93 → 101`: overlaid local pins have no surface selector |
| [`configuration/execution.py`][execution] | `57 → 60`: optional-only reconciliation candidate fails baseline equality |

The last gap limits dynamic evidence for freshness refusal. Source inspection
supports that guard, but the SDK mismatch test fails earlier and does not cover
this arc. Likewise, executing all lines does not test every sequence of commands.

To reproduce the main evidence in a disposable checkout of the pinned commit,
with its documented virtual environment and dependencies:

```sh
cd devcapsule-src
PYTEST_ADDOPTS='--basetemp=/opt/devcapsule-gate/pytest' .venv/bin/python -m nox -s build
PYTEST_ADDOPTS='--basetemp=/opt/devcapsule-gate/pytest' .venv/bin/python -m nox -s tests
.venv/bin/python -m coverage json -o /opt/devcapsule-gate/capability-coverage.json
```

Branch collection and default suite selection are declared in
[`pyproject.toml:74–102`][coverage-config]. For the changed-code calculation,
intersect executable line numbers from the JSON with added-side ranges from
`git diff --unified=0 710fd04 99ff26a -- devcapsule-src/devcapsule`; count branch
arcs whose source line lies in those ranges. Local original artifacts are
`.git/config-policy-coverage.json`, `.git/config-policy-diff-coverage.json` and
`.git/measure-config-coverage.py`; they are not shipped evidence. The commands
above do not require those local artifacts. Run the unit suite last so its
coverage data is not replaced by another pytest session.

## 4. Counterexample: omission destroys a retained version-set pin

The guide promises that empty [`--without` restores enhancements, lines 100–119][promise].
For an existing explicit local version set containing Playwright:

1. `config capabilities --without browser-automation` projects Playwright out.
2. [`capability_commands.py:175–186`][writer] stores that *effective* reduced
   lock back into the persistent version-set record, losing its Playwright pin.
3. `config capabilities --without` clears the omission but takes that reduced
   record as its source again. It neither restores the old pin nor fills the
   missing optional provider from the shared recommendation.
4. The reader warns about missing Playwright; the optional tool stays absent,
   although its shared declaration and provider are still available.

This was reproduced with the pinned source CLI in an isolated temporary project
on Linux AMD64, without network, Docker or changes to the working repository's
configuration. See the [bug record](../../bugs/devcapsule/2026-10-06-optional-omission-loses-local-version-pin.md)
for the exact fixture and observed output.

The pin-retention test exercises an IDE replacement while retaining all optional
providers; the ordinary omission/restoration test has no explicit local version
set. Both are correct for their own inputs, but their conjunction does not cover
this interaction. A regression test must combine an explicit sentinel optional
pin with omission and restoration, assert the pin survives in persistent intent,
and assert the provider returns without changing shared bytes or host decisions.
The implementation should distinguish persistent selected software from the
run's filtered projection. A future fix needs its own commit and argument update;
this document intentionally retains the original snapshot and failed obligation.

[requirement]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/engineering-docs/requirements/product/r-config-001-conservative-writers-tolerant-readers.md#L17-L79
[policy]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/capabilities.py#L15-L75
[providers]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/resolution_matrix.py#L297-L322
[selection]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/capability_selection.py#L108-L156
[compose]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/capability_selection.py#L68-L105
[generate]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/capability_selection.py#L28-L65
[writer]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/capability_commands.py#L109-L191
[check]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/capability_commands.py#L71-L106
[journal]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/capability_commands.py#L23-L68
[init]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/capability_commands.py#L194-L234
[atomic]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/storage.py#L218-L245
[load]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/storage.py#L292-L310
[fingerprints]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/fingerprints.py#L10-L41
[execution]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/execution.py#L36-L62
[model]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/model.py#L40-L54
[override]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/environment_realization.py#L56-L70
[degrade]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/environment_realization.py#L228-L261
[acquire]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/materialization.py#L188-L238
[retry]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/commands/project.py#L1185-L1205
[certify]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/commands/project.py#L1322-L1334
[versions]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/version_sets.py#L399-L418
[follow]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/version_sets.py#L574-L585
[consent]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/devcapsule/configuration/authorization.py#L519-L528
[fixture]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L24-L45
[parse-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L48-L79
[closure-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L82-L148
[writer-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L151-L192
[recovery-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L195-L226
[freshness-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L239-L279
[init-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L282-L310
[pin-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L313-L332
[conflict-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L335-L361
[boundary-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L364-L421
[download-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L424-L464
[run-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L467-L510
[cli-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L513-L561
[override-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L564-L593
[consent-test]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L596-L614
[artifact-tests]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/test_capability_policy.py#L616-L644
[architecture]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/configuration/test_architecture.py#L8-L72
[pex]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/tests/integration/test_pex_runtime.py#L317-L339
[coverage-config]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/devcapsule-src/pyproject.toml#L74-L102
[evidence]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/engineering-docs/wip/2026-08-30-component-catalog/CURRENT-STATUS.md#L143-L165
[promise]: https://github.com/ccozianu/devcapsule/blob/99ff26ac564368427f77773ac0a4c2beaa257eea/docs/configuration/capabilities.md#L100-L119
