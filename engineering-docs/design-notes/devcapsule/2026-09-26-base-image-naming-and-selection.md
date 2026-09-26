# Base images as a contract

Design note, 2026-09-26, `maintenance`, for a decision with the product
owner after 0.2.14 shipped with its base labelled `v0.2.12-rc5`. Status:
proposed. The first version of this note presented four options for
renaming; the owner redirected it to the question underneath, and the
options collapsed. The mechanics quoted here are read from the 0.2.14
source.

## 1. What a base image is

A base image is a prebuilt OCI image that every capsule image names in its
`FROM` line. It is built once, by `devcapsule images build --type base`,
from a recipe in `devcapsule/base_image.py`, and it contains no DevCapsule
runtime: the launcher copies its own executable into the capsule image at
launch (D-0009). The consumer of a base is a formation, the capsule image
built on top of it, and the components validated to run there.

The consumer does not care who built the base or with which executable. It
cares what it can rely on: which operating system line and libraries, which
toolchains are installed and where, whether a contained display is present,
and what the runtime expects of the image. That set of promises is the
base's contract, and the recipe is the contract's text.

## 2. The contract, and when it changes

The recipe already knows its contract; it labels it into every image it
builds:

| Label | Value today | What it promises |
|---|---|---|
| `devcapsule.base.recipe` | `ubuntu-24.04` | the OS line and library ABI |
| `devcapsule.base.recipe-version` | `9` | which edition of the recipe |
| `devcapsule.base.display` | `contained` | Xvnc, window manager, noVNC present |
| `devcapsule.base.runtime` | `launcher-supplied` | no runtime inside; the launcher brings its own |
| `devcapsule.component.*` | temurin 25.0.4+7, maven 3.9.16, postgresql client | toolchains and their homes |

The matrix has the other half of the vocabulary: a **base family**
(`ubuntu-24.04`), the line along which validations are inherited. D-0007's
amendment of 2026-09-06 says when a new family opens: "a new OS release, a
toolchain overhaul, or a runtime-plan vocabulary older releases cannot
execute". That sentence is the definition of an incompatible change, and it
is already the boundary the matrix uses: a component version is verified
against a family, and every base in the family inherits the verification.

So the contract has two versions, and both already exist:

- **Family** is the incompatible-change line. A consumer validated on
  `ubuntu-24.04` may not run on `ubuntu-26.04`.
- **Recipe version** is compatible evolution within the family. Recipe 9
  added the contained display to recipe 8; a formation validated on recipe 8
  still runs on recipe 9.
- A **build** is one execution of a recipe: fresher packages, a new digest,
  the same promises.

## 3. Naming by contract

A base's name is its contract: `<family>@<recipe>`, today `ubuntu-24.04@9`.
A concrete image is that name at an immutable digest. The release of the
tool that built it belongs in provenance labels, where the recipe already
puts it (`devcapsule.source.revision`, `org.opencontainers.image.version`),
and nowhere in the name.

This dissolves the problem that started the note. `v0.2.12-rc5` was never
the base's name; it was its builder. The matrix pin copied the builder's
mnemonic into the lock as `build-mnemonic`, and the messages read it as if
it named the base. Renaming it to `v0.2.12` would have replaced one wrong
kind of name with a slightly less wrong one. The right name was in the
labels all along.

## 4. The model

Three small, frozen types; the recipe module owns the first two, the matrix
and the lock carry the third.

```python
@dataclass(frozen=True)
class BaseContract:
    """What a base promises. Changes only when the recipe changes."""
    family: str                 # "ubuntu-24.04": the incompatible-change line
    recipe: int                 # 9: compatible evolution within the family
    services: frozenset[str]    # capabilities satisfied: python, docker-cli, node, java, maven
    display: str                # "contained" or "host-x11-only"
    runtime: str                # "launcher-supplied"

    @property
    def identity(self) -> str:
        return f"{self.family}@{self.recipe}"

    def accepts(self, validated_on: "BaseContract") -> bool:
        """May a consumer validated on `validated_on` run on this base?"""
        return self.family == validated_on.family and self.recipe >= validated_on.recipe


@dataclass(frozen=True)
class Provenance:
    """Who built the image. Informational; never an identity."""
    source_revision: str
    builder: str                # "v0.2.12-rc5"
    built_on: date


@dataclass(frozen=True)
class BaseImage:
    """One built artifact under a contract."""
    contract: BaseContract
    reference: str              # registry reference at an immutable digest, or a local image ID
    built: Provenance

    @classmethod
    def from_labels(cls, reference: str, labels: Mapping[str, str]) -> "BaseImage": ...
```

`from_labels` exists because the labels are complete: any image the daemon
holds, published or locally built, reconstructs its `BaseImage` without a
matrix lookup. That is what makes a local twin (`devcapsule-base:0.2.14-rc2-local`)
and the published `v0.2.12` provably the same contract: both are
`ubuntu-24.04@9`.

The matrix's base pins become `BaseImage` records; its verified edges stay
keyed by `contract.family`, which they already are. The lock's `[base]`
table gains `contract = "ubuntu-24.04@9"` and renames `build-mnemonic` to
`built-by`, read under both names for old locks. Messages become:

```text
Base ubuntu-24.04@9 at sha256:8837edd3…, built 2026-09-14 by v0.2.12-rc5.
```

## 5. What the abstraction buys

**Consent binds to the base.** Today the base-image consent is bound to a
digest of the whole lock, so a component version bump re-asks consent for
an unchanged image. Consent is about executing an image; it should bind to
the `BaseImage`, its reference and contract identity. Component changes stop
re-prompting; a different image, or the same image under a different
contract claim, still does.

**Moving to a newer base has a rule instead of a procedure.** `accepts` is
the rule. A newer base in the same family is compatible by construction and
inherits every validation, so a checkout may adopt it the way it adopts a
newer component version: as a version-set member, `versions preview base
ubuntu-24.04@10`, `select`, `rollback`, `propose`. A base in a new family
is a project decision: regenerate the lock, validate the components on the
new family, commit. The tool can say which case it is, because the contract
says so.

**Rebuilds are ordinary.** A rebuild of recipe 9 with fresher packages is
`ubuntu-24.04@9` at a new digest: compatible, adoptable per checkout, and
its provenance says when it was built. Security refreshes of the base stop
needing a release of the tool.

**Registry tags follow.** A published build is tagged by contract and date,
`devcapsule-base:ubuntu-24.04-r9-20260914`, with the digest as the pin.
Tags named after tool releases, `v0.2.12`, `v0.2.12-rc5`, stop being minted.

## 6. Migration

- Add `BaseContract` and `BaseImage` to `base_image.py`; the recipe
  constants already define the contract. `from_labels` reads the labels the
  build already writes.
- Give the three matrix pins their contracts: v0.2.8 is `ubuntu-24.04@5`,
  v0.2.10 is `ubuntu-24.04@6`, the 0.2.12 base is `ubuntu-24.04@9`, from
  the recipe versions recorded in their comments. Verified edges are
  unchanged.
- Lock: write `contract` and `built-by`; read `build-mnemonic` as `built-by`
  for existing locks. This is a lock change, so each project's next
  regeneration re-asks base consent once. With consent rebound to the
  `BaseImage`, it is the last cosmetic re-consent there will be.
- Display and diagnostics read the contract identity; provenance is shown
  after it, never instead of it.
- Version sets admit the base as a member in a later slice; nothing above
  depends on it.

The four options of the earlier draft map onto this: A is the interim if
the contract work waits (derive the display name from the matrix by
reference); B is subsumed; C is this note done properly; D is section 5's
first paragraph.

## 7. Asked of the owner

1. Adopt the contract naming, `<family>@<recipe>`, as the base's identity,
   with provenance kept out of the name.
2. Approve rebinding base consent to the `BaseImage`.
3. Decide whether the version-set membership of the base comes with the
   contract work or waits for the first newer published build.
