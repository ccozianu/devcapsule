# Base images: how one is chosen, what its name is, and how a user could move to a newer one

Design note for a decision the product owner asked to make together on
2026-09-26, after 0.2.14 shipped with its base labelled `v0.2.12-rc5`.
Written by `maintenance` as a memory prop: the mechanics below are read
from the 0.2.14 source, not remembered. Status: proposed; the owner decides.

## 1. The three places a base image lives

**The matrix, inside the tool.** `devcapsule/resolution_matrix.py` is a
hand-maintained table shipped in every DevCapsule executable, currently
`embedded-20`. It holds base pins, component pins, and "verified edges",
records that a component version was validated on a base family. A base
pin has four parts:

| Part | Value for the 0.2.12 base | Role |
|---|---|---|
| `mnemonic` | `v0.2.12-rc5` | the pin's name in matrix diagnostics |
| `base_family` | `ubuntu-24.04` | which validations it inherits |
| `satisfies` | python, docker-cli, node, java, maven | capabilities the base provides |
| `lock_table` | `reference = docker.io/mycodespaceai/devcapsule-base@sha256:8837edd3…`, `build-mnemonic = v0.2.12-rc5` | copied verbatim into locks |

Three pins exist: v0.2.8, v0.2.10, v0.2.12-rc5, all one family. The newest
pin whose family has verified edges for every needed component is selected.
Every project that lets the tool recommend a base gets this pin. The table
is not about the ccozianu/devcapsule repository; that repository is only
the project that regenerates its lock most often.

**The lock, inside each project.** `project init` and `init --regenerate`
write `.devcapsule/devcapsule.<platform>.lock`, committed with the project.
Its `[base]` table is the pin's `lock_table`, byte for byte. The lock is the
project's recommendation; it changes only when someone regenerates it, and
that change travels to every checkout by git.

**The consent, inside each checkout.** `config authorize base-image default`
accepts the lock's recommendation and records, in the checkout's own file,
the `reference` and a `lock-digest`, the digest of the entire lock. Any
later change to any table of the lock, a component version, a mnemonic,
anything, makes the consent "authorized against a different lock", and the
checkout is asked again. A local image can be authorized instead by tag or
ID; then the consent also records the image ID and `run` requires it.

## 2. Where the name you see comes from

This is the fact that reshapes the options. The visible label is not the
matrix pin's `mnemonic`. `config show` and the launch messages read the
lock's `build-mnemonic`: "Execute DevCapsule v0.2.12-rc5 at the exact
registry digest selected by the platform lock", and "recommended:
v0.2.12-rc5 — docker.io/…". The matrix `mnemonic` appears only in matrix
diagnostics such as "X on base v0.2.12-rc5".

So "change only the display name" cannot be done by editing one word in
the table: the display reads the lock, and the lock is a copy of the table
made at regeneration time.

Why the label is what it is: the base was built by the v0.2.12-rc5
executable on 2026-09-14 and pushed; Docker Hub later got a second tag,
`v0.2.12`, on the same image. `build-mnemonic` records who built it, which
is provenance, and the messages use it as if it were the base's release
name, which it is not.

## 3. The options for the name

**A. Derive the display name from the matrix by reference; keep the lock.**
The matrix already looks up a pin by its `reference` (it does so to find the
base family). The display code can do the same: when the lock's reference
matches a pin, show the pin's `mnemonic`, renamed to `v0.2.12`; otherwise
fall back to the lock's `build-mnemonic`. The lock is untouched, no
consent is invalidated, every project sees "v0.2.12" from the next
executable on. Cost: a small display change plus the one-word rename.
Locks keep saying `build-mnemonic = "v0.2.12-rc5"`, which is true as
provenance and read by nobody else.

**B. Rename in the lock table as well.** `build-mnemonic` becomes
`v0.2.12`. Correct on its face, but the lock fragment is part of the lock,
so at each project's next regeneration the lock changes and every
checkout's base consent is invalidated for a cosmetic reason. By the
matrix's own rule a changed generated formation also advances the matrix
version.

**C. Separate the two meanings.** Add a `release` field to the pin's
`lock_table`, `v0.2.12`, and keep `build-mnemonic` as provenance; messages
use `release`. Same re-consent cost as B, because the lock changes, but it
fixes the vocabulary permanently: every future base carries both the
release it belongs to and the executable that built it. This is B done
properly, and it should ride along with the next genuinely new base, when
regeneration and re-consent happen anyway.

**D. Bind consent to the base, not to the whole lock.** Today a component
version bump invalidates base consent although the image is unchanged. If
the consent bound to the base table's digest (reference and its fields),
B and C would not re-prompt for a mnemonic change, and component-only lock
changes would stop re-prompting base consent too. This is a change to
D-0004's consent binding and needs its own argument: the whole-lock digest
was chosen so that a consent always names the exact combination it was
given for. Worth deciding on its merits, not as a way to fix a label.

Recommendation: A now, C with the next new base, and D as a separate
question for component-upgrades.

## 4. The design question underneath: moving to a newer base

Today a user has exactly three ways to change the base a checkout runs on:

1. Regenerate the project's lock with a newer tool (`init --regenerate`),
   commit it, and re-consent. A project change; every checkout follows.
2. Authorize a daemon-local image by tag or ID. A checkout-local override
   bound to that image ID.
3. Nothing per checkout for a published base the tool recommends but the
   project's lock does not. Version sets (R-UPGRADE-001, `project versions`)
   let a checkout try newer component versions without touching the lock;
   the base is part of a set's identity but is not selectable.

The gap is number 3. Two shapes:

- **Base as a version-set member.** `versions preview base v0.2.13`,
  `select`, `rollback`, with the same evidence and consent flow the
  components have. The tool's newer pin becomes a candidate the checkout
  can adopt without a project change, and `propose` can export the lock
  patch upstream once it worked. Consistent with the existing design.
- **Keep the rule that base changes are project changes**, and make the
  tool say so clearly: "this DevCapsule recommends a newer base than your
  project's lock; regenerate to adopt it". Cheaper, and honest about who
  decides, but it leaves the per-checkout trial that version sets give
  components unavailable for the base.

Both need the same prerequisite: a published base that is newer than the
project's lock, which does not exist today, since 0.2.14 shipped no base.
The decision can wait for the first one, but the naming (section 3) should
not, because every new base inherits the vocabulary.

## 5. What is asked of the owner

1. For the name: A now, or B or C now, or nothing until the next base.
2. Whether D, consent bound to the base table rather than the whole lock,
   should be argued separately by component-upgrades.
3. Whether the base becomes a version-set member, the plain rule stays, or
   the question waits for the first newer published base.
