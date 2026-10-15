---
description: "A conversation between DevCapsule's product owner and the agent developing it about when a tool should refuse, and how the refusal experience took its shape."
---
# When should a tool refuse? Taking stock of DevCapsule's refusal UX

*2026-09-06. A conversation between Costin Cozianu, DevCapsule's product
owner, and Claude, the agent developing it alongside. The exchange is
reproduced with light edits for readability.*

## Some context first

DevCapsule gives a software project a portable development capsule: an IDE
and a chosen set of agent CLIs, materialized into a local container image
and launched against a checkout, with the project's declaration committed
in Git. A project owner writes a small manifest naming *capabilities* the
project needs, such as `python-ide`, `node`, or `codex-agent`. From that
declaration, the DevCapsule client derives a *platform lock*: the exact
base image, component versions, download URLs and checksums that every
collaborator will get. The lock is committed; collaborators consume it and
never derive anything themselves.

The derivation runs against an *embedded resolution matrix*: a table,
shipped inside the client, of which component versions have actually been
validated on which base images. The matrix is deliberately sparse. A
combination enters it when someone has run it and recorded the evidence,
and resolution prefers the newest combination the matrix vouches for. When
no base image satisfies every requested capability with validated
components, the client refuses to generate a lock and says why. An escape
hatch, `--unverified`, lets the owner generate the lock anyway with a
warning, and the lock then records which combinations were unvalidated.

DevCapsule is developed by a human product owner and an AI agent working
in the same repository, under a written workflow. The owner rules on
design; the agent implements, investigates, and keeps the engineering
records. This means the developers are also the heaviest users of their
own tool, and they are permanently running ahead of the very matrix they
maintain. That is how the conversation below started.

The day before, while regenerating the lock of a sample project that asks
for PyCharm together with three agent CLIs, the owner had been refused
with this:

```
v0.2.9: no verified pycharm version against base v0.2.9 (substrate ubuntu-24.04-gen2)
v0.2.8: no verified pycharm version against base v0.2.8 (substrate ubuntu-24.04-gen2)
v026: no verified antigravity-cli version against base v026 (substrate ubuntu-24.04-gen1)
Pass --unverified to resolve past missing verification with a gentle warning; ...
```

The immediate cause was quickly established: PyCharm had been validated
only on the older generation of base images, the Antigravity CLI only on
the newer one, so no single base satisfied both. The fix was a data
change, since the owner had in fact been running PyCharm on the newer
base all day. But the message itself, with its "verified", "edge", and
"substrate", was clearly written by the matrix for the matrix, not for
the person reading it. When the agent asked how to rename those terms,
the owner declined to answer a vocabulary question in isolation and
stepped back:

## The question

> First of all let's revisit what we, and you especially, both understand
> of the UX, and maybe also clean up our engineering docs on this topic.
> When do we refuse a configuration asked by a user (and should we
> distinguish different users here?), what grounds do we have, and what
> message do we give them?

## The answer

Here is my understanding of the refusal UX as it stands, what the design
notes commit us to, and where the two disagree.

### Who is on the other side of a refusal

The [V1 user-experience design note](https://github.com/ccozianu/devcapsule/blob/cb4616b4a9ede8ac92881c50a5100b719c96cac4/engineering-docs/design-notes/devcapsule/v1-user-experience.md)
names three owners of artifacts, and the code distinguishes them only by
which command they run:

- **The project owner** runs `init` and authors the manifest and the lock.
  Resolution against the matrix happens only here. Every "no verified
  combination" refusal is therefore owner-facing by construction.
- **A collaborator** clones a lock and runs `config`, `resolve`, and
  `run`. They never resolve against the matrix. Their refusals are consent
  and drift: authorize this base, accept these vendor terms, this lock
  predates the recipe the client understands.
- **Us, the matrix maintainers**, who decide what counts as validated. We
  are also the heaviest owners, permanently running ahead of our own
  matrix, which is why we keep meeting the owner-facing refusal.

So the answer to "should we distinguish users" is that the code already
does, by phase. What it does not do is speak to each in their own terms.

### The grounds we refuse on today

| Ground | Who hits it | Bypass | Nature |
|---|---|---|---|
| Vocabulary and shape: unknown capability, zero or two surfaces, malformed files | owner | none | a fact about the request |
| A base does not ship a required toolchain | owner | none | a fact about the world |
| No validated component-on-base combination | owner | `--unverified` on `init` only | a fact about **our knowledge** |
| Consent declined: base image, vendor acquisition | anyone, per checkout | authorize later | the user's decision |
| A published base other than the pinned digest | anyone | select a local image instead | reproducibility rule |
| Drift: old recipe version, already initialized, authored content never rewritten | anyone | `--regenerate`, `config` | protocol |

The third row is the one that keeps biting, and it is different in kind
from every other row. Every other refusal states something true about the
request or the world. This one states something about the matrix's
ignorance, then phrases it as if PyCharm on v0.2.9 were known to fail. It
is not a refusal on grounds. It is an honest "we have not checked",
delivered in the voice of "you may not".

### Where the design notes and the code disagree

- **The lock is a record, not a mandate** and **inspection never gates**
  are settled principles of the design note. But a lock generated past the
  matrix carries a header warning and an `unverified-combinations` field,
  and nothing reads that field back. A collaborator who clones it is never
  told. The owner's informed choice becomes the collaborator's silent one.
- **Every refusal names the sanctioned lever** is the house rule, ruled
  again the day before this conversation when a
  [refusal that named only the oldest base's problem](https://github.com/ccozianu/devcapsule/blob/cb4616b4a9ede8ac92881c50a5100b719c96cac4/engineering-docs/bugs/devcapsule/2026-09-03-resolution-refusal-names-only-the-last-base-and-no-remedy.md)
  was fixed. Yet `config need`, the command that adds a capability to an
  existing project, prints the `--unverified` remedy and cannot accept the
  flag, and the owner's `--authorize base-image` selection cannot
  influence resolution because `init` resolves before it reads the base
  answer. Two levers on screen, neither reachable from where the user
  stands.
- **Derive, report, ask** says the tool decides facts and asks intent.
  Whether to run ahead of validation is intent, and the owner ruled
  strict-first three days earlier: try the fully validated resolution, and
  only fall past the matrix on request. That ruling stands, but the
  question is asked as an error, not as a question.
- **Vocabulary.** The matrix's decision record,
  [D-0007](https://github.com/ccozianu/devcapsule/blob/cb4616b4a9ede8ac92881c50a5100b719c96cac4/engineering-docs/decisions/product/d-0007-resolution-matrix-model-and-interface.md),
  speaks of verified edges, couplings, provenance, and since a later
  amendment, substrates: the compatibility generation a family of base
  images shares. Those are the right words for the model. They leak
  verbatim into the refusal, the lock, the README, and a sample project's
  committed files. Adopters read "edge" and "substrate" and learn nothing
  about what to do.

### What I would put to you

1. **Reframe the third row from refusal to disclosure.** For the owner:
   state exactly what has and has not been validated, in base and
   component terms only, and ask the intent question with a named lever
   that works everywhere resolution happens, including `config need`. For
   the collaborator: `resolve` and `run` say once, plainly, "this lock runs
   PyCharm 2026.2.0.1 on base v0.2.9, which the project owner accepted
   unvalidated", and `config list` shows it always.
2. **Keep the model's words inside the model.** Edges, couplings,
   substrates, provenance stay in D-0007 and the code. Adopter-facing text
   says validated and not validated, names bases, and never names the
   grouping unless you want it taught.
3. **Say what validation means.** Today a matrix entry is anything from a
   full end-to-end run to "the owner ran it all day". Adopters deserve one
   sentence on the gate, and our own provisional entries deserve to be
   visible as provisional in the lock, not only in a code comment.
4. **Clean the record.** D-0007 gets the refusal-grounds table and the
   vocabulary boundary. The user-experience note gets a section on when
   DevCapsule refuses and when it only discloses. The sample project's
   committed lock and README lose the substrate wording on the next
   regeneration.

The one thing I cannot settle for you is the default in row three.
Strict-first makes an owner opt in to unvalidated combinations, which
protects collaborators. Newest-first-with-disclosure makes the tool more
useful to owners running ahead, which is us most days. Your earlier ruling
chose strict-first, and everything above works under either.

## Where this goes next

The decisions this answer asks for, the default in row three, the word
for "validated", and whether the base grouping is ever shown to adopters,
were still open when this entry was written. The engineering records
will carry the rulings; a later entry may carry what they taught.
