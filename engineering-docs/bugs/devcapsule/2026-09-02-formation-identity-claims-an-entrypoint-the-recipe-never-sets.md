# Bug: The Formation Identity Claims An Entrypoint The Recipe Never Sets

Date opened: 2026-09-02

Status: open; entrypoint half **ruled 2026-09-05** (see *Ruling* below),
implementation pending. Reported by the product owner during v0.2.8
dogfood validation, running `devcapsule-local.pex project run` against
the DevCapsule checkout itself

Requirements: R-PRODUCT-001, root R-PRODUCT-002 (the host-side image
accumulation), R-SCOPE-001

Related: `2026-08-15-detached-successors-not-cleaned-up.md` — same
family for the accumulation half: DevCapsule creates host objects it
neither surfaces nor reaps.

## Symptom

`project run` against the unchanged dogfood project re-ran the full
materialization: the PyCharm archive was re-unpacked, 4.31 GB of build
context was transferred to the daemon (11.2 s of the 11.5 s build), and
the log then reported a *new* canonical environment:

```
 => [internal] load build context                                    11.2s
 => => transferring context: 4.31GB                                  10.6s
 => CACHED [ 2/11] COPY copy-dir-0/ /opt/jetbrains/pycharm/           0.0s
    ... every one of the 11 recipe steps CACHED ...
Materialized canonical environment: devcapsule-local-pycharm:6341e61801ce8d2471b1
```

Every layer was CACHED — Docker already held this exact content — yet
the run produced another ~7.2 GB image tag instead of reusing the
existing formation.

## Environment

- Client: v0.2.8 pex (`devcapsule.pex.sha256 b7959c52…`, source revision
  `91d50b1d`)
- Base: `docker.io/mycodespaceai/devcapsule-base:ubuntu-24.04-v026`
  (the dogfood formation combines agents with the surface, so the
  `embedded-3` matrix still resolves it to v026)
- Project: this repository's own `.devcapsule` (needs
  `claude-code-agent`, `codex-agent`, `docker-cli`, `python`,
  `python-ide`)

## Mechanism (from code reading and image inspection, both confirmed)

`formation_descriptor` bakes `ENTRYPOINT_CONTRACT` into the identity
hash as `runtime.entrypoint`. Commit `500909d` (2026-08-30, the
supervisor-takes-PID-1 work, part of the v0.2.8 client) removed
`"/usr/bin/tini", "--"` from that constant. That single constant change
invalidated the identity of **every previously materialized formation**,
so the first v0.2.8 run of any project rebuilds its environment from
scratch even though no component, base, template, or recipe step
changed.

The rebuild is provably content-free. The superseded sibling
`devcapsule-local-pycharm:5dfa686ce5dc74688955` and the new
`6341e61801ce8d2471b1` differ *only* in the descriptor label — same
base identity, same three component digests, and Docker gave both the
same image `Created` timestamp (2026-08-18T00:13:38) because every
layer came from cache. Gigabytes of unpacking and context transfer
bought a label edit.

Worse, the label edit is false. The materialization recipe emits only
COPY/chmod/label steps — it never writes an `ENTRYPOINT` instruction —
so the image inherits its entrypoint from the base. The v026 base still
wraps in tini. The freshly "Materialized" image therefore records
`runtime.entrypoint = ["/opt/devcapsule/bin/devcapsule.pex", "runtime"]`
in its own descriptor label while its actual `Config.Entrypoint` is
`["/usr/bin/tini", "--", "/opt/devcapsule/bin/devcapsule.pex",
"runtime"]`. Confirmed live: inside the capsule this run launched,
PID 1 is tini, not the supervisor — the premise of `500909d` (the
supervisor takes over PID 1) does not hold on any v026-based formation.
`verify_materialized_image` cannot catch this: it compares labels to
labels, never a claim to the image's actual configuration.

## Consequences

1. A release that touches any descriptor-participating constant silently
   re-materializes every formation on every developer host — minutes of
   unpack plus a multi-gigabyte context transfer per project — and the
   output line says only "Materialized", never *why*, so the developer
   cannot distinguish expected first-run work from churn.
2. The formation record lies about the runtime contract, which is
   exactly the kind of record D-0008 and the inspection surfaces exist
   to make trustworthy.
3. Superseded canonical images are never retired. The development host
   currently carries 15 `devcapsule-local-pycharm` formations
   (5.57–7.2 GB each) plus 2 codium ones; `docker system df` reports
   138.3 GB of images with 131.9 GB reclaimable and 223.2 GB of build
   cache. Nothing in the product surfaces or reaps them — the
   2026-08-15 container bug, replayed for images.

## Expected

A formation identity that changes only when the materialized artifact
actually changes; descriptor fields that are enforced by the recipe (or
verified against the image) rather than merely recorded; and a lifecycle
for superseded canonical images consistent with the product's
leave-nothing-behind promise.

## Ruling (2026-09-05, product owner — the entrypoint half)

The owner's framing: the tension is both of our own making and the
technology's. A different entrypoint *is* logically a different
fingerprint — an image with a different entrypoint cannot be used in
place of the original — yet an entrypoint is just metadata, so changing
it should never trigger gigabytes of rebuilding; rebuilding an image
with the same contents and a different entrypoint should be almost a
no-op.

The ruling:

1. **The base image should not have a real entrypoint.** (Today v0.2.9
   bakes the supervisor and v026 bakes tini; removing it is a change
   for the next base release.)
2. **The launcher sets the entrypoint in the derived image** — the
   materialization emits it, making the descriptor claim true by
   construction. Because a derived image's `ENTRYPOINT` overrides the
   base's, this holds on *every* existing base (v026's tini and
   v0.2.9's baked supervisor both get overridden), so the fix does not
   wait for the entrypoint-less base.
3. **If a derived image does not need rebuilding for content, one may
   be built anyway just to set the entrypoint.** Implementation shape:
   when the only descriptor difference from the nearest existing
   formation is entrypoint/command, build a thin derivative — `FROM
   <existing canonical image>` plus the `ENTRYPOINT` — with an empty
   build context, instead of re-running the full recipe (whose 4.31 GB
   context transfer is the dominant cost even when every layer caches).
   The identity keeps entrypoint in the fingerprint (the owner's
   logical point stands); only the *cost* of an entrypoint-only
   identity change collapses.

Consequence for PID 1: with the recipe enforcing the supervisor as
entrypoint, the supervisor genuinely takes PID 1 on all formations,
including v026-based ones — realizing `500909d`'s premise. Its PID-1
duties (signal forwarding, zombie reaping, or composing docker's
`--init` where an init shim is still wanted) are the supervisor
contract `contained-display` owns; the standing coordination item
covers this.

Recorded for future iterations, same session (not part of this fix):
optimize materialization so component contributions are cached in
per-component layers — an `npm install` or `curl … | sh` should run
once per adopter machine, not once per formation rebuild.

## Fix Scope (owner rulings needed on direction)

1. Decide what `runtime.entrypoint`/`runtime.command` mean in the
   descriptor. Either the recipe *enforces* them (emit `ENTRYPOINT`/
   `CMD` in the materialization Dockerfile, making the claim true on
   every base) or they leave the identity hash and become a verified
   property of the base edge instead. Enforcing in the recipe also makes
   the supervisor's PID-1 takeover real on v026 formations —
   coordinate with `contained-display`, which owns that contract.
2. Make `verify_materialized_image` compare at least the entrypoint
   claim against the image's actual `Config.Entrypoint`, so a
   descriptor/config contradiction fails loudly instead of persisting.
3. When materialization does run, say why: which descriptor fields
   differ from the nearest existing formation (or "first
   materialization"), so churn is visible the day it ships.
4. Superseded-image lifecycle: on successful materialization, the tool
   knows the prior canonical tags for the same project/surface; decide
   between reaping them, offering a `devcapsule` cleanup verb, or at
   minimum reporting them in inspection output. Sequence with the
   2026-08-15 container-cleanup fix; the accounting machinery should be
   shared.

## Reproducibility

The rebuild churn: once per formation per descriptor-touching release
(the next run reuses the new tag). The false entrypoint claim: always,
on every formation whose base still carries the tini entrypoint —
inspect any v026-based canonical image and compare
`devcapsule.materialization.descriptor`'s `runtime.entrypoint` with
`Config.Entrypoint`.

## Verification Target

- Automated test: materialize against a base whose entrypoint differs
  from `ENTRYPOINT_CONTRACT`; assert either the built image's actual
  entrypoint equals the contract (if enforced) or verification fails
  loudly (if checked). A second test: two materializations differing
  only in a non-artifact descriptor field must not produce two images
  with identical layers and contradictory labels.
- Manual validation: after the fix, a client upgrade with unchanged
  components reports "Reused canonical environment" (or explains
  precisely what changed) on the dogfood project.
