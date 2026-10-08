# Capability configuration: persistent selection versus execution projection

Review date: 2026-10-08. Branch: `ws-component-catalog/intellij-idea-correctness`,
proposed into `ws-component-catalog/intellij-idea`. Implementation and tests
reviewed at commit `236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98`; the failing showcase tests are
the previous commit `3bc9eb6a89deb9661f9d6bd23ede3b752c8344f7`. Every source link below fixes
both the commit and its original line numbers. Paths are relative to the
repository root. This note extends the
[2026-10-06 argument](2026-10-06-configuration-correctness.md), which keeps its
own snapshot and its counterexample; the obligation that failed there is
discharged here, together with three smaller defects the same review found.

**Conclusion:** with one representation invariant added, the omission argument
closes. The persisted selection of a checkout never depends on which optional
capabilities are currently omitted, so clearing an omission restores exactly the
pinned provider. The claim remains conditional on the preconditions of the
earlier argument (schema-admitted documents, validating entry points, a finite
consistent catalog) and on the limits recorded in section 4.

## 1. The invariant the original implementation lacked

Let `S` be a checkout's **persistent selection**: the explicit local version
set when one exists, otherwise the shared lock with the checkout's personal
pins laid over it. Let `E(S, W)` be the **execution projection**: `S` filtered
by the project policy and the local omissions `W`, as defined by
`usable_lock`. The original code computed `E` and stored it back as `S`
whenever a local edit touched an explicit version set, and whenever a version
set was selected while an omission was active. Storing the projection destroyed
the information the projection had hidden, which is the
[reproduced counterexample](../../bugs/devcapsule/2026-10-06-optional-omission-loses-local-version-pin.md).

The fix names the two values and keeps them apart:

- [`compose_lock`, lines 107–152][compose] computes `S` and applies no
  omission. It returns the version set when present; otherwise it copies the
  shared lock and lays over it exactly the providers of each locally selected
  capability, plus the IDE selector and materialization when a selected
  capability supplies the IDE. It rejects an IDE that conflicts with a legacy
  shared IDE, missing or malformed pins, and omissions outside the project's
  optional list.
- [`usable_lock`, lines 181–243][usable] computes `E`. Its closure argument
  from the earlier note is unchanged; only a message now distinguishes a
  required from a locally selected capability.
- [`effective_lock` and `selected_lock`, lines 155–178][effective] are
  `E ∘ compose` with warning output, so every existing reader keeps its
  behavior while new writers can reach `S` alone.

**Invariant P1:** every writer of a version-set record writes a value of `S`,
never a value of `E`. The two writers are checked below.

## 2. Writers persist the selection

### 2.1 Local capability edits

[`configure_local`, lines 211–253][local] loads the record, validates the new
selection through the same reader as external data (so `L ∩ W = ∅` and name
rules hold before anything is resolved), parses the previous pins through
`local_pins` (so a corrupt document is a configuration error before any
write), and takes `source` as the version set when present, else the shared
lock. It then:

1. [`release_deselected`, lines 288–310][release] removes from an explicit
   version set the providers of capabilities that were selected and no longer
   are, unless a required, known optional or still-selected capability needs
   them. A removed IDE also clears the selector and materialization. This is the
   only subtraction, and it is driven by the selection delta, not by `W`.
2. [`pin_selection`, lines 256–285][pins] builds the personal pins document,
   holding exactly the providers of the selected capabilities. Each provider's
   metadata comes from the first document that has it: `source`, then the
   previous pins for a capability that stays selected, then a fresh catalog
   resolution of the required and selected capabilities. The IDE selector and
   materialization follow the IDE component's document.
3. `compose_lock` over `source` and the new pins yields `S'`, which is written
   into the version-set record when one exists. `E(S', W')` is computed only to
   validate formation, and is discarded.

Because `W` enters neither step 1 nor step 2, `S'` is a function of
`(S, L, L')` alone, which is P1. Two consequences follow directly from the
pin rule and are tested: a locally selected project-optional tool follows the
shared pin instead of being re-pinned from the catalog, and a retained
selection keeps its previous pin with or without a version set.

### 2.2 Version-set selection

[`Workspace.load`, lines 52–58][workspace] now carries both values, using
[`selection_for`, lines 292–337][storage], which returns the composition and
its projection from one load. [`preview`, lines 316–368][preview] builds the
candidate from the composition and changes one component, and all structural and
validation checks run on `_projection` of the candidate: what would execute.
`_selection` persists the candidate unchanged and admits its projection, as it
did before. The record written by `select` is therefore `S` with one
component replaced, which is P1.

`follow_project` removes the version set rather than writing one, and realizes
the projection, unchanged. `rollback` is discussed in section 4.

## 3. Separate argument for the tests

The showcase commit adds six tests that fail on the previous implementation,
one per defect, and the fix commit adds two that pin the deselection rule.
Oracles are sentinel versions written into locks before the command runs, byte
snapshots of the shared directory, the saved authorization table, and explicit
error classes and messages; none re-implements the composition.

| Test (all in `devcapsule-src/tests/`) | Oracle and defect it would expose |
| --- | --- |
| [`test_capability_policy.py:647–668`][t-omit] | Sentinel Playwright pin in an explicit version set survives omit and restore; the effective lock omits it in between and carries the sentinel afterward; shared bytes and the authorization table are unchanged. The original defect. |
| [`:671–679`][t-shared] | A sentinel shared Playwright pin is what the effective lock carries after `--local browser-automation`. Re-pinning from the catalog would show the catalog version. |
| [`:682–692`][t-corrupt] | A corrupt pins document yields `ProjectConfigurationError` mentioning pins and leaves the record byte-identical. A traceback or a rewritten record fails it. |
| [`:695–705`][t-init] | `init --local codex-agent` succeeds, the effective lock then asks for an IDE, and selecting one yields the literal component set. |
| [`:708–712`][t-named] | An unavailable local selection is reported as *Selected*, not *Required*. |
| [`:729–738`][t-keep] | Deselecting a project-optional tool keeps its sentinel pin in the version set and in the effective lock, because the project still wants it. Exercises the *needed* guard of `release_deselected`. |
| [`:741–752`][t-drop] | Deselecting an agent removes only its component; the IDE's sentinel pin and selector stay. Exercises removal of a non-IDE provider. |
| [`test_version_sets.py:987–1012`][t-versions] | Through the CLI: with `--without browser-automation` active, `versions preview` and `select` record a version set that still holds the sentinel shared Playwright pin, and clearing the omission brings it back beside the upgraded component; host decisions other than renewed base trust are unchanged. |

The two deselection tests pass on the previous implementation as well; they are
regression guards for the stated rule, not evidence of a defect. The version-set
test is limited to the codex journey because the widget fixture's capability is
unknown to the catalog and cannot be a required capability.

Full unit suite on the review branch: 1,253 passing cases (the earlier 1,245
plus the eight above) and two xfails; the previously non-strict xpass
(the clock-dependent workflow claim test, a recorded flake) xfailed in that run. The build gate
(`nox -s build`: distribution version, syntax, mypy, unit tests, source and
PEX smokes, ten packaged integration cases, documentation contract) passed;
log `.git/correctness-review-build.log`, not shipped. Branch coverage of the
changed modules under the policy, version-set, upgrade-recovery and project
command suites: `capability_selection.py` 99%, `capability_commands.py` 97%,
the two uncovered arcs being the deliberately unreachable
*catalog did not pin its provider* refusal and the guard for a previously
selected capability this launcher no longer knows.

## 4. Limits and open threads

- **Rollback re-persists an execution snapshot.** Known-good records store the
  lock that ran, which is a projection. `rollback` writes that lock as the
  version set, so a rollback to a run that omitted an optional capability bakes
  the omission in; clearing the omission afterwards will not restore the
  provider. P1 does not hold for that writer. Fixing it needs the composition
  to be recorded beside the known-good lock, a record-format decision left to
  the owner.
- **Unknown previously selected capabilities are left alone.** If a launcher
  downgrade makes a previously selected capability unknown, its providers stay
  in the version set when it is deselected. The projection still filters them.
- **Corrupt pins have no command-only recovery.** The refusal is conservative
  and leaves the record intact; the developer currently has to repair or remove
  the record by hand, which the project's command-only rule discourages. A
  product decision is needed on whether a local edit may discard unreadable
  pins when it replaces the selection anyway.
- **`proposal` exports the projection.** It diffs the effective lock against
  the shared lock, so a proposal from a checkout with a personal IDE or an
  omission describes personal state as a project change. Pre-existing and
  outside this review's diff.
- The argument covers the composition and persistence boundary. Artifact
  integrity, authorization, realization and the legacy fast path keep the
  arguments and limits of the earlier note.

[compose]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/devcapsule/configuration/capability_selection.py#L107-L152
[usable]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/devcapsule/configuration/capability_selection.py#L181-L243
[effective]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/devcapsule/configuration/capability_selection.py#L155-L178
[local]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/devcapsule/configuration/capability_commands.py#L211-L253
[release]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/devcapsule/configuration/capability_commands.py#L288-L310
[pins]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/devcapsule/configuration/capability_commands.py#L256-L285
[workspace]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/devcapsule/version_sets.py#L52-L58
[storage]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/devcapsule/configuration/storage.py#L292-L337
[preview]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/devcapsule/version_sets.py#L316-L368
[t-omit]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/tests/test_capability_policy.py#L647-L668
[t-shared]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/tests/test_capability_policy.py#L671-L679
[t-corrupt]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/tests/test_capability_policy.py#L682-L692
[t-init]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/tests/test_capability_policy.py#L695-L705
[t-named]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/tests/test_capability_policy.py#L708-L712
[t-keep]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/tests/test_capability_policy.py#L729-L738
[t-drop]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/tests/test_capability_policy.py#L741-L752
[t-versions]: https://github.com/ccozianu/devcapsule/blob/236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98/devcapsule-src/tests/test_version_sets.py#L987-L1012
