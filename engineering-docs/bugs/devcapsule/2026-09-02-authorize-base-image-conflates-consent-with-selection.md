# Bug: `--authorize base-image` Conflates Consent With Selection And Explains Neither

Date opened: 2026-09-02

Status: ruled and fixed on the branch 2026-09-03. The owner ruled the
UX directly: init accepts the reference the user typed — DevCapsule
reads the image from the local daemon (digest, platform, base labels),
presents the metadata, and solicits informed consent that this is the
selection meant; a new `--less-pedantic` init flag records the
validated selection without the solicitation ("I am the project
maintainer and I just built v0.2.9 with my bare hands"). Noninteractive
runs without the flag batch-fail naming it as the remedy. The
unintelligible rejection is rewritten to state the flag's consent role,
the matrix's selection role, and the reference path. D-0004's trust
constraints survive intact: trust binds to the daemon-inspected image
ID, never to the mutable tag, and a *published* non-recommended digest
still requires project-reviewed metadata. Fix-scope items 1 and 2 below
are thereby delivered (item 2 exceeded: reference-shaped values are not
just explained but accepted); item 3 — the joint grammar ruling with
the denial bug — remains open. Closes on the owner's next init against
their built base.

Extended the same day by a second owner ruling: `--authorize base-image
yes` "never made sense to begin with" — authorizations are KV pairs, a
digest is a value, a tag points at one, and `yes` is neither. `yes` is
retired as a base-image value; the reserved keyword `default` accepts
the recommendation for a single key (`init --authorize base-image
default`, `config authorize NAME default` — any authorize node), with
`--all-recommended` remaining the bulk form and Enter remaining the
interactive acceptance. `no` survives as decline flow, not as a value;
whether a *recorded* denial exists is exactly the open denial-grammar
bug. Boolean consent prompts (vendor acquisitions) keep yes/no as
prompt vocabulary since their stored value is the boolean itself. Originally confirmed by the product owner 2026-09-02
("the message is only intelligible to you, not even to me as product
owner/designer, much less to an unsuspecting user").

Requirements: R-PRODUCT-001, R-PRODUCT-002

Related:
[2026-09-02-authorization-grammar-cannot-express-denial](2026-09-02-authorization-grammar-cannot-express-denial.md)
— the same grammar failing to say what it means, from the other side;
the two should be ruled on together.

## Symptom

The product owner, twice on 2026-09-02, ran:

```
devcapsule-local.pex project init --need node --need frontend-ide \
  --need antigravity-agent \
  --authorize base-image docker.io/mycodespaceai/devcapsule-base:v0.2.9 \
  --regenerate
devcapsule: Authorization 'base-image' accepts yes, no, or the exact value
'docker.io/mycodespaceai/devcapsule-base@sha256:ca9f7961…734232'
```

On the second attempt the demanded digest was the digest *of the very
tag the owner typed* — the tool refused a value naming the same image
it was asking consent for, with a message that explains nothing.

## Mechanism

Three layers, all by design rather than defect in code:

1. **Grammar**: `--authorize base-image VALUE` reads as assignment —
   every CLI convention says "use this base." It is actually *consent*:
   the value-form exists so a noninteractive run proves it consents to
   the exact reference resolution already selected
   (`_acquisition_validator` in `project_operations.py`). Base
   *selection* lives entirely in the resolution matrix; no init-level
   lever chooses a base, and nothing tells the user so.
2. **Message**: "accepts yes, no, or the exact value '…'" is the
   validator's internals leaking out. It does not say what the
   authorization is for, that the base was already chosen from
   `capabilities.need`, why the value is a digest, or what to type
   next. It even *invites* the mistake by presenting the value as
   choosable.
3. **The unrecognized near-miss**: init resolves offline, so it
   genuinely cannot verify that a tag names the same image as the
   pinned digest (tag→digest is a registry call, and tags are mutable —
   consent correctly binds to the immutable digest). But the validator
   can recognize a *reference-shaped* value and explain exactly this
   instead of reciting its accepted inputs.

## Provenance (owner asked 2026-09-02: designed or accidental?)

Split down the middle. The *semantics* are designed: D-0004 (proposed
2026-07-30) scopes authorization to "one immutable registry digest or
one inspected local image ID", "never … a registry namespace,
repository, tag, or future digest", and separates the lock's
recommendation from the developer's trust record. The *surface* is
accidental: D-0004 explicitly deferred the spelling ("remains an
implementation task"; "the command grammar may still be refined before
V1"), and the implementation (`5be7a34`, 2026-08-24) poured the consent
answer into the config family's assignment-shaped `VERB NAME VALUE`
grammar, whose validator message leaks its accepted inputs. Note:
D-0004 is still `status: proposed` — the joint ruling asked for below
is D-0004's own deferred refinement coming due and could settle its
status at the same time.

## Expected

An unsuspecting user who passes a base reference here learns, from the
error alone: the base is selected by resolution from their needs, not by
this flag; this flag consents to executing the selected base; consent
binds to the immutable digest because tags are mutable; and the way
forward is `yes` (or interactively, Enter).

## Fix Scope (proposed; wording and semantics are the owner's ruling)

1. Rewrite the rejection message to state role, selection source, and
   remedy — minimum viable fix, no grammar change.
2. Detect reference-shaped values and answer them specifically (the
   tag-vs-digest explanation above), distinct from arbitrary garbage.
3. Rule jointly with the denial-grammar bug whether the authorization
   verb family gets an explicit shape that cannot be misread as
   assignment (e.g. consent answers are only yes/no/digest-echo, and
   the flag's help text says "consents to"), since both records show
   the grammar failing to communicate its semantics.

## Reproducibility

Always: any `--authorize base-image VALUE` where VALUE is not `yes`,
`no`, or the byte-exact resolved reference.

## Verification Target

- Automated: a test asserting the rejection message for a
  reference-shaped value names the resolution matrix as the selector,
  the consent role of the flag, and the yes/no remedy.
- Manual: the owner rereads the message cold and finds it intelligible.
