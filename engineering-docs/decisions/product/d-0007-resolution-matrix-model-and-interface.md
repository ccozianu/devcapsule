---
id: D-0007
title: Resolution Matrix As Accumulated Verified Combinations
status: proposed
date-proposed: 2026-09-01
date-decided:
decided-by:
requirements:
  - R-COMPAT-001
supersedes:
superseded-by:
---

# D-0007: Resolution Matrix As Accumulated Verified Combinations

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
