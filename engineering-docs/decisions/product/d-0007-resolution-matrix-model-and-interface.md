---
id: D-0007
title: Resolution Matrix As Accumulated Verified Combinations
status: accepted
date-proposed: 2026-09-01
date-decided: 2026-09-01
decided-by: Costin Cozianu
requirements:
  - R-COMPAT-001
supersedes:
superseded-by:
---

# D-0007: Resolution Matrix As Accumulated Verified Combinations

Runtime-delivery update, 2026-09-11: [D-0009](d-0009-launcher-delivers-identical-runtime.md)
establishes launcher-delivered identical runtime as the default. Embedded-runtime
examples in the historical amendments below describe the earlier architecture;
the accepted resolution model remains in force.

## Context

`resolution_matrix.py` answers the product's central derivation: the user
expresses capability needs, and the module looks up component versions
that satisfy those needs on a platform, constrained by what has been
tested. Its current form cannot express that constraint's most basic
property: **verification is a fact about a combination, and facts do not
expire.** PyCharm against the v0.2.7 base does not cease to be verified
because v0.2.8 exists — yet today the module pins exactly one "proven
current formation," and advancing `MATRIX_VERSION` *replaces* it,
un-expressing combinations that remain perfectly verified. They survive
only in committed locks and git history.

Structural symptoms of the same gap:

- `_BASE_TABLE` can hold only one base version, while the codium surface
  already needs a newer base than the one PyCharm was proven on, and the
  NVIDIA CUDA recipe exists with no matrix slot at all.
- Every pin is a `dict[str, Any]` TOML fragment; a typo in a hand-edited
  pin surfaces at materialization time, not type-check time — and the
  release process prescribes exactly such hand edits.
- "The base satisfies capability X" is said two structurally different
  ways: `BASE_SATISFIED_CAPABILITIES` (a frozenset, invisible in the
  generated lock) versus the postgresql-client component with
  `delivery-policy: "base-image"` (visible in the lock).
- Component coupling hides in flat dicts: the codex pin carries
  `integration: "jetbrains-ai-assistant"`, a surface-coupled fact whose
  meaning under a codium lock the structure cannot even question.
- The module has no deliberate public interface; it exports its internals
  (`BASE_SATISFIED_CAPABILITIES`, `INTERACTIVE_SURFACE_CAPABILITIES`,
  `MATRIX_VERSION`, `SUPPORTED_PLATFORMS`).

That multiple versions must be supported almost everywhere is a given;
even if the result is sparse, it is a matrix.

## Options Considered

### Option A: Keep the single-formation model, add typing

`TypedDict`s over the current tables. Cost: closes only the typo class.
The matrix remains one overwritten point; accumulated verification stays
inexpressible, and the codium/PyCharm base split has no representation.

### Option B: Rows are whole tested formations

Each row: (platform, base version, all component versions) plus evidence,
append-only. Cost: combinatorial re-verification — every new agent
version demands re-smoking every surface it might sit beside — so the
matrix stays so sparse that reasonable user combinations routinely have
no row.

### Option C: Verified edges, declared couplings, default orthogonality

Verification is recorded per edge (component@version × base@version ×
platform). Components that interact through an explicit integration point
declare a **coupling**, which requires its own jointly verified version
pairs. Components without a declared coupling compose freely on a shared
verified base. Cost: default orthogonality is an assumption — it is where
a composed formation could claim verification nobody performed.

## Decision

Option C, as the information model:

1. **Verified edges**, append-only: (component@version, base@version,
   platform) with a reference to the evidence that verified it (which
   test, when). Removal is explicit **retirement** (security withdrawal,
   dead artifact URL), never an implicit effect of adding newer versions.
2. **Declared couplings** for component pairs with an integration surface
   (today: agent↔IDE via ACP / `jetbrains-ai-assistant`), carrying their
   own jointly verified version pairs.
3. **Default orthogonality** otherwise — IDE ⊥ agent absent a coupling;
   SDK questions are inside the base edge because SDKs are base contents.
4. A full-formation smoke is recorded as **provenance verifying all its
   constituent edges and couplings jointly**, so evidence stays cheap to
   produce; interference discovered later is by definition a missing
   coupling declaration, and the fix is declaring it.
5. **Resolution** selects component versions such that every required
   edge and every triggered coupling is verified, preferring the newest
   verified combination. Same need, same matrix ⇒ identical lock bytes,
   offline (R-COMPAT-001: a matrix advance changes only what is generated
   next time, never the validity of a standing lock).

And the public interface, sized by what a client must know (Parnas):

```python
MATRICES: Mapping[Platform, ResolutionMatrix]   # total over Platform members

class ResolutionMatrix:
    def capabilities(self) -> tuple[str, ...]      # the askable vocabulary
    def normalize(self, need) -> tuple[str, ...]   # canonical, vocabulary-checked
    def resolve(self, need) -> Formation           # raises ResolutionError

class Formation:
    capabilities: tuple[str, ...]
    provenance: str                   # displayable identity of the selection
    def render_lock(self) -> str      # the exact bytes to commit

class ResolutionError(...)            # message complete and displayable
```

`Platform` comes from D-0006; a client obtains one only via
`Platform.current()` or `Platform.parse()`, and the map's totality over
the enum makes "supported" a single, type-checked fact. Everything else
becomes private: the capability taxonomy (the exactly-one-surface rule
survives only as a `ResolutionError` explanation), the pin tables, the
selection policy, the evidence representation, `MATRIX_VERSION`, and the
TOML shape. Base satisfaction is unified as one concept — every
capability's satisfaction has a source (base or materialized component) —
with one policy for whether base-satisfied capabilities appear in the
lock.

## Rationale

The model follows from taking "what has been tested" seriously as the
module's subject: tested facts accumulate, so the structure must be
append-only and versioned on every axis. Edges-plus-couplings is chosen
over whole formations because interference between components is not
ambient — it travels either through the base (the codium/v026 failure was
precisely a component×base edge) or through an integration point the
system already half-declares (the codex pin). Making couplings
first-class turns yesterday's hidden field into the model's exception
mechanism. The interface hides the entire model behind `resolve()` so the
matrix can move from today's single point to the sparse verified matrix
— and later grow the update mechanism's evidence queries as new methods —
without any client noticing. Lock rendering stays behind `Formation`
because nothing else authors locks; the client's need is "bytes to
commit."

## Consequences

- The generated lock format (v1) is unchanged; the new model must project
  onto it byte-identically for current inputs, pinned by the existing
  rendered-lock tests.
- The base repin for codium becomes an *addition* of newly verified edges
  rather than a replacement of the only formation; PyCharm's v026
  verification remains expressed.
- The future component-update mechanism gains its foundation: per-edge
  provenance says what re-verification a version advance demands.
- Accepted risk: default orthogonality can compose combinations never
  tested as wholes. Mitigation: couplings are first-class, and any
  discovered interference converts into a declaration.
- Migration touches every current importer (`project_operations`, tests)
  and demotes today's exported constants to private.

## Reopen If

A second author of locks appears (the rendering seam behind `Formation`
was chosen on there being exactly one), or undeclared-interference bugs
recur across component families — evidence that orthogonality is the
wrong default and formation-level verification (Option B) is the honest
unit after all.

## Amendment 2026-09-02: Edges Key On The Base Substrate

Decided by the product owner after the v0.2.9 base rebuild hit the
model's granularity: decision point 1 keyed edges on
(component@version, **base@version**, platform), which made every
release of *our own derived base* a fresh verification target with zero
edges — a full re-smoke of every component per release, even when the
release changed nothing but the embedded runtime PEX, whose correctness
the test suite and the release E2E ladder already own.

What a smoke actually establishes is component-on-**substrate**: the
component runs on this OS/toolchain surface. Base pins therefore declare
a substrate (a compatibility generation, e.g. `ubuntu-24.04-gen2`), and
edges verify against the substrate, not the pin. Base releases sharing a
substrate share edges; resolution still prefers the newest pin. Bumping
the substrate string is the deliberate act reserved for substantial base
changes — a new OS release, a toolchain overhaul, or a runtime-plan
vocabulary the older generation cannot execute (the gen1→gen2 boundary:
gen2 bases embed a runtime that executes vscode-adapter plans, which
v026 predates).

Accepted risk, stated at the ruling: derived bases carry the capability
toolchain (node, python, docker-cli, …), so a rebuild that bumps a
toolchain package could break a component without touching the substrate
string. The release E2E ladder covers that class; if it recurs in
practice, the substrate granularity is the thing to revisit. Evidence
strings on edges keep naming the concrete base that was smoked.

## Amendment 2026-09-06: A Missing Validation Is Disclosed, Not Refused

Decided by the product owner after a refusal met while regenerating the
trading-research sample's lock (PyCharm validated only on gen1,
Antigravity only on gen2) surfaced two things: the model's vocabulary
(*verified edge*, *substrate*) had leaked into every adopter-facing
surface, and a gap in the matrix's knowledge was being delivered in the
voice of a refusal on grounds.

**Grounds for refusal.** Resolution refuses outright in exactly one case:
no base ships a toolchain the need requires. That is a fact about the
world and `--unverified` cannot help; the message says so. Every other
gap — a component version or a coupling the matrix has not validated on
the selected base — is a fact about the matrix's knowledge. It is
disclosed, not refused: the message names the exact elements the
experiment would run (component, version, base) and offers to run it as
an experiment with `--unverified`. The lever is accepted wherever
resolution happens (`init`, `config need`).

**The lock discloses the same.** A lock generated as an experiment says
so in its header and in `unverified-combinations`, in the same words, so
the owner or contributor who publishes it and the collaborator who
clones it read the same fact. For now both are warned identically; the
tool cannot yet tell a private checkout lock from one about to be
committed, and gating belongs where the matrix is updated (below).

**The vocabulary boundary.** *Verified edges*, *couplings*,
*provenance*, and *substrates* are this record's words and the code's.
Adopter-facing text — refusals, warnings, lock headers, README — says
*validated* / *not yet validated*, names components, versions, and
bases, and never names the grouping.

**Handed to `project-management` (intake 2026-09-06):** designing how
the matrix learns from user experience — an adopter's successful
experiment becoming a validated combination — and, later, gating a
matrix change on mainline on the existence of a claim that every added
combination has run successfully. Until then, matrix entries advance at
the owner's direction with their evidence string, provisional entries
included.

## Amendment 2026-09-06 (second): One Base Family, Named Plainly

Decided by the product owner while retiring the 0.2.9 release. Two
facts drove it: the older generation was still active in exactly one
place — `postgresql-client` had a validation only against it, so every
need naming that capability resolved to v026 — and the field carrying
the generation, `substrate`, was the one identifier in the model that
did not explain itself.

- **Vocabulary.** The compatibility unit of the 2026-09-02 amendment is
  now called the **base family**: the family of base releases a
  validation holds for. `_BasePin.base_family` and
  `_VerifiedEdge.base_family` carry it, documented in place. The
  `ubuntu-24.04-gen1` / `-gen2` names are gone; the one family in use is
  `ubuntu-24.04`. A new family is opened, and named, only for a
  substantial base change (new OS release, toolchain overhaul, a
  runtime-plan vocabulary older releases cannot execute).
- **Retirement.** The v026 pin
  (`docker.io/mycodespaceai/devcapsule-base@sha256:695f9eb6…`) and every
  validation recorded only against its family are retired, per decision
  point 1 (retirement is explicit, never an implicit effect of adding
  newer entries). Nothing selected v026 once `postgresql-client` gained
  its entry.
- **`postgresql-client`.** A base-shipped component's validation is that
  the base carries the package its pin describes; checked in the v0.2.9
  image on 2026-09-06 (`psql 16.14`, the same Ubuntu build v026 shipped)
  and recorded as its entry's evidence.
- **Internal naming.** Commit subjects and records name what changed for
  whom — component, version, base, evidence status — not the model's
  words; the house style is with `project-management` (intake
  2026-09-06).

## Amendment 2026-09-06 (third): The v0.2.9 Pin Retired With Its Release

Decided by the product owner: the 0.2.9 release — the PEX on GitHub
Releases and the `v0.2.9` base tag on Docker Hub — was withdrawn on
2026-09-06, after v0.2.10 had been pushed, run on the trading-research
sample and the dogfood project, and tagged. 0.2.9 shipped codex as a
single plucked binary; the fix landed the same day, after the tag.

- **Retirement.** The v0.2.9 base pin
  (`docker.io/mycodespaceai/devcapsule-base@sha256:ca9f7961…734232`) is
  retired from the matrix, explicitly, per decision point 1. Retiring a
  base release in a family removes no validation: the family's edges
  stand, and evidence strings that name the v0.2.9 image keep naming it,
  since they record where a smoke ran, not what is selectable.
- **No matrix-version advance.** Nothing selected v0.2.9 once v0.2.10
  was pinned, so no generated formation changes; `embedded-18` stands.
- **Standing locks.** A lock that pins the v0.2.9 digest remains valid
  per `R-COMPAT-001`. The manifest is still served by digest after the
  tag's removal, but that is registry retention, not a guarantee; such
  a checkout should regenerate.
