# Capability configuration: persistent selection versus execution projection

Review date: 2026-10-08. Branch: `ws-component-catalog/intellij-idea-correctness`,
proposed into `ws-component-catalog/intellij-idea` as PR #171. Implementation and
tests reviewed at commit `e9be77a9234015790892da857a5834ace80b1c36`. The showcase tests for the
original defects are commit `3bc9eb6a89deb9661f9d6bd23ede3b752c8344f7`; the
first fix is `236fa3cc4eac0f2c05c3e72c2616da5a92b3fd98`; the reproducers from
the Codex review of #171 are `babbb96` and their fix is the reviewed commit.
Every source link below fixes both the commit and its original line numbers.
Paths are relative to the repository root. This note extends the
[2026-10-06 argument](2026-10-06-configuration-correctness.md), which keeps its
own snapshot and its counterexample; the obligation that failed there is
discharged here, together with three smaller defects the same review found and
three regressions the Codex review found at the selection boundary.

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

**Invariant P1:** each command writer of a version-set record, the local
capability edit and `versions preview`/`select`, writes a value of `S`, never a
value of `E`. `versions rollback` is a third writer and is excluded; section 4
records why. The two command writers are checked below.

**Invariant P2 (its converse):** every consumer that acts on a version-set
candidate, by asking consent, downloading, pinning or realizing, acts on
`E(candidate, W)`, never on the candidate itself. Entries that `E` hides are
carried unchanged. The Codex review of #171 found three consumers that broke P2
once the candidate became `S`; section 2.3 covers them.

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

### 2.3 Selection consumes the projection

[`select`, lines 494–516][select] receives a candidate that is now `S`. At the
first fix it still treated the candidate as `E` in three places, each reproduced
by the Codex review and now a test:

1. **Consent.** Acquisition declarations and the accepted answers replayed into
   the final admission were collected from the unfiltered candidate, so a
   component hidden by an omission either raised `KeyError` for an answer never
   required, or had its retained inactive consent replayed as an acquisition.
   Declarations are now read from `prepared.lock`, the lock `_selection` admitted,
   which is the projection. A hidden tool neither needs nor replays consent.
2. **Pinning and download.** `_pin_artifacts` recursed over the whole candidate,
   downloading hidden providers and interpreting opaque metadata this reader does
   not understand. [`_pin_active_artifacts`, lines 408–418][pin-active] pins the
   projection and writes only its component entries back into the candidate.
   Hidden and unsupported entries are byte-for-byte what the composition held.
3. **Freshness.** A preview recorded only the execution identity, which hashes
   the projection, so a hidden shared pin could change between preview and
   select and the old value would be persisted as an explicit pin. The proposal
   now also records a canonical digest of the composition, and `select` refuses
   when either differs. Execution identities (`set_id`) are unchanged, so running
   and known-good identities keep their meaning. A preview written before this
   change lacks the field and is refused as stale.

With these, `select` reads `S` only to persist it, and everything with an
effect reads `E`. That is P2 for this writer.

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
| [`:1030–1039`][t-consent-absent] | With shared optional `antigravity-agent` omitted locally, `preview`/`select` succeed, infer no `antigravity-download` consent, and keep the hidden provider in the version set. Failed with `KeyError` before the select fix. |
| [`:1042–1052`][t-consent-kept] | Consent given while the tool was active is left exactly as recorded after it is omitted and a selection runs; the executed lock excludes the tool. Replaying it as an acquisition fails this. |
| [`:1055–1069`][t-stale] | Change a shared pin that the current omission hides after previewing: the composition differs, the execution identity does not, and `select` exits 2 with *preview again* without writing a version set. |
| [`:1072–1094`][t-opaque] | An opaque optional provider with `url`/`integrity` and no SHA-256: selection must not request its URL, and the version set carries its metadata unchanged beside the upgraded component. |

The two deselection tests pass on the previous implementation as well; they are
regression guards for the stated rule, not evidence of a defect. The version-set
test is limited to the codex journey because the widget fixture's capability is
unknown to the catalog and cannot be a required capability.

Full unit suite on the review branch: 1,257 passing cases (the earlier 1,245
plus the twelve above) and the two expected-failure outcomes recorded before
(one xfail; the clock-dependent workflow claim test is a recorded flake that
xpasses or xfails by run). The build gate (`nox -s build`: distribution
version, syntax, mypy, unit tests, source and PEX smokes, ten packaged
integration cases, documentation contract) passed;
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
  provider. P1 is stated for the two command writers and does not hold for
  this third one. Fixing it needs the composition to be recorded beside the
  known-good lock, a record-format decision left to the owner for the #170
  review.
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

[compose]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/devcapsule/configuration/capability_selection.py#L107-L152
[usable]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/devcapsule/configuration/capability_selection.py#L181-L243
[effective]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/devcapsule/configuration/capability_selection.py#L155-L178
[local]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/devcapsule/configuration/capability_commands.py#L211-L253
[release]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/devcapsule/configuration/capability_commands.py#L288-L310
[pins]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/devcapsule/configuration/capability_commands.py#L256-L285
[workspace]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/devcapsule/version_sets.py#L52-L58
[storage]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/devcapsule/configuration/storage.py#L292-L337
[preview]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/devcapsule/version_sets.py#L316-L370
[t-omit]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/tests/test_capability_policy.py#L647-L668
[t-shared]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/tests/test_capability_policy.py#L671-L679
[t-corrupt]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/tests/test_capability_policy.py#L682-L692
[t-init]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/tests/test_capability_policy.py#L695-L705
[t-named]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/tests/test_capability_policy.py#L708-L712
[t-keep]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/tests/test_capability_policy.py#L729-L738
[t-drop]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/tests/test_capability_policy.py#L741-L752
[t-versions]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/tests/test_version_sets.py#L987-L1012
[select]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/devcapsule/version_sets.py#L494-L516
[pin-active]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/devcapsule/version_sets.py#L408-L418
[t-consent-absent]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/tests/test_version_sets.py#L1030-L1039
[t-consent-kept]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/tests/test_version_sets.py#L1042-L1052
[t-stale]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/tests/test_version_sets.py#L1055-L1069
[t-opaque]: https://github.com/ccozianu/devcapsule/blob/e9be77a9234015790892da857a5834ace80b1c36/devcapsule-src/tests/test_version_sets.py#L1072-L1094
