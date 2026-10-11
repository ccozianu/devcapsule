---
status: confirmed
severity: minor
target: 0.3.0
owner: maintenance
opened: 2026-09-24
requirements: [R-IMAGE-BUILD-001]
---

# Installed IDE cannot be reused before archive acquisition on a new formation

Owner direction, 2026-09-24: file the bug first and **review the design with
the owner before implementation**. No implementation approach or release target
is approved. This is not a new 0.2.14 blocker. Severity is minor because the
observed consequence is repeated download/preparation cost, with a working
launch; reconsider if evidence establishes a more serious impact.

## Expected behavior

After a user downloads and materializes a pinned PyCharm installation, that
installation should remain reusable from the local Docker daemon for future
compatible environments. Another project, a changed DevCapsule executable, or
a fresh capsule without the archive cache should not require downloading and
unpacking the same IDE again while the reusable Docker content is retained.
The current installation prefix is `/opt/jetbrains/pycharm`.

## Evidence and current limits

The real recursive launch at `9cc0868`, run
`29fb2abc530735da1ebd625acd991622`, downloaded the pinned PyCharm
2026.2.0.1 archive (SHA-256
`4a37cb2d15703553c61e814d8e014bfa47308508470de5f968c4e9645b771675`).
Measured archive size: 1,217 MiB compressed; file contents total 3,517 MiB.
The owner accepted the running session, then requested stronger Docker reuse.
This run alone does not prove that an identical reusable installation was
already present in Docker before the download.

Code inspection establishes the gap:

- `ensure_materialized_surface` in `devcapsule/materialization.py` reuses an
  exact complete formation immediately. On a formation miss it calls
  `acquire_artifact`, then unpacks the IDE before calling the Docker builder.
- `acquire_artifact` can reuse a verified file in the launcher's filesystem
  cache. It does not consult installed Docker content.
- `ContributionComponent` and `COPY --link --from` in `devcapsule/image_build.py`
  provide independent BuildKit stages. That cache is reached after acquisition,
  extraction and build-context preparation; it cannot prevent those earlier costs.
- `test_installation_is_reused_across_images_and_invalidated_by_recipe` covers
  BuildKit execution reuse using a small generated component. It does not cover
  the materializer with an empty archive cache and an existing installed IDE.

## Owner evidence from v0.2.14-rc3, 2026-09-24

The owner ran `project run` with the downloaded rc3 launcher in a checkout
last launched by rc2. The formation differed only in `runtime.pex-sha256`,
so the launcher materialized a new canonical image
`devcapsule-local-pycharm:71ccc3500d04b532a6c8` from `828151182df668fafb66`.
Every component stage was `CACHED`, including the PyCharm copy stage and the
codex `npm install`; the archive cache was warm, so no download or unpack
happened. The cost was elsewhere:

| Phase | Measured |
|---|---|
| `load build context` | 4.28 GB transferred in 10.9 s, with the PyCharm tree re-rendered into the context although its stage was cached |
| `exporting layers` | 16.9 s |
| whole build | 31.5 s, 38 steps |
| retained images | 39 prior `devcapsule-local-pycharm` formations, 266.0 GB, with the launcher's own note that superseded canonical images are not reaped |

Root cause of the rebuild itself: the runtime PEX digest is part of the
formation identity by design (D-0009, `materialization.py`, `pex-sha256` in
the descriptor and the `devcapsule.pex.sha256` label), so every launcher
change is a new formation. Root cause of the cost: `image_build.py` renders
the extracted IDE tree into the build context on every build (`copy-dir`
entries), so BuildKit's stage cache saves the `COPY` but not the transfer;
and nothing reaps superseded canonical images. The owner rates this "very
bad": a launcher upgrade should not cost minutes of I/O and gigabytes of disk
per checkout. This extends the scenario list below: reuse must hold across a
launcher change with a warm archive cache, and the context must not carry
what the cache already holds.

## Proposed acceptance scenarios for design review

1. Materialize a pinned IDE once. Keep its reusable Docker content, use an
   empty launcher artifact cache, change the launcher or consuming project,
   and disable artifact downloads. A compatible environment must still build
   with the expected IDE files and the new launcher bytes.
2. Verify the reuse path does not unpack or resend the IDE archive/tree.
3. Change the pinned IDE artifact or installation recipe. The previous
   installation must not be mistaken for the new one.
4. Remove the reusable Docker content. A subsequent launch must acquire and
   verify missing inputs normally, or report their absence clearly when offline.

## Design questions to review together

Decide how installed content is named, found and verified in Docker; what
platform/base/recipe compatibility enters its identity; and what retention,
pruning, concurrent creation and interrupted-build behavior is promised.
Decide whether the first implementation covers PyCharm alone or a general
component contract. A retained component image is one possible approach, not
an approved design. Ordinary user pruning may remove reusable content; do not
promise persistence independent of Docker lifecycle choices.

Coordinate with the already-deferred
[image-composition contract redesign](2026-07-16-pycharm-build-multiline-exec-rendering.md),
without treating this report as approval to start that redesign or enlarge
the current release. Review design, implementation ownership and release
placement with the owner before coding.

## Decision, 2026-10-05: in the next release, which is 0.3.0

Owner ruling during the triage of the next release's bugs: the design
review happens now, and the optimized way of building Docker images is
part of the next release. That release is named **0.3.0**, not 0.2.16, a
marketing decision reflecting the jump forward from 0.2.15. Both halves of
this record are in scope: reuse of installed IDE content across
formations, launcher changes and projects (acceptance scenarios 1 to 4
above), and reaping of superseded canonical formations and their cache
entries. The named-build-context fix for the context transfer stays the
first step. The design questions above are reviewed with the owner before
code, as directed on 2026-09-24; the agent prepares the design proposal
when the plate reaches this item.

## First step built, 2026-10-06: named build contexts, measured

On `ws-maintenance/post-0.2.15`, commits `images: directory inputs are
named build contexts ...` and its follow-up. Three parts, each needed; the
first experiment showed why.

1. **Directory inputs are named build contexts.** `render_build_context`
   renders every `DirectoryCopy` as `COPY --from=NAME / DEST/` and returns
   the `NAME=PATH` map (`RenderedBuildContext`); the builder passes it as
   `--build-context`. Nothing is copied into the context root any more.
2. **One context root per launcher cache.** BuildKit keys its incremental
   transfer of local sources on the path of the main context root; a fresh
   temporary root per build, which 0.2.15 uses, re-sends every tree in
   full. Experiment on a 157 MB tree: 157 MB with root A, 157 MB again with
   a fresh root B and the same named context, 4 KB with root A again.
   `BuildxImageBuilder(context_root=<cache>/build-contexts/context)`
   reuses one directory, serialized by a lock beside it.
3. **Archives unpack once, by digest.** `unpacked_tree` keeps the surface
   archive and directory artifacts under `<cache>/unpacked/<sha256>` with
   a completion marker written last; every formation reads the same path.

Measured 2026-10-06 in this repository's capsule on the real PyCharm
2026.2.0.1 tree, 3.69 GB unpacked, a new label per build standing in for
the launcher-digest change that makes every upgrade a new formation:

| Rebuild after a launcher change | Context transfer | Wall |
|---|---|---|
| 0.2.15 way: copy the tree into a fresh context, plain `COPY` | 3.69 GB, plus a 9 s copy of the tree first | 21 s per rebuild, every time |
| New way, first build of this tree | 3.69 GB | 23.5 s, once per IDE version |
| New way, every later rebuild | 1.29 MB | 1.1 s |

The unpack itself took 15 s once; the second call returned the tree in
under a millisecond. The 4.28 GB transfer in the rc3 measurement above is
therefore gone from every launcher upgrade, and so is the per-build copy
of the tree in BuildKit's local-source cache, since the shared key no
longer changes.

Not done here, for the design review: the unpacked trees under
`<cache>/unpacked` are never pruned (one per IDE version, 3.7 GB each for
PyCharm; the archive cache already keeps the 1.2 GB tarball beside it),
superseded formations are still not reaped, and installed Docker content
is still not consulted before acquisition. Note for the proof: this
capsule's `PEX`/`SCIE` environment makes the runtime digest that of the
capsule's own launcher, so the recursive end-to-end test always reuses
the formation here and cannot exercise a rebuild; the measurement ran the
materializer's own pieces directly.

## Disposition, 2026-09-25

Owner ruling: reuse of installed IDE and other component layers across
formations is substantial work and is presumed outside the 0.2.14 release
cycle; keep it in attention with the rc3 measurements above as the case.

## Addendum, 2026-09-25: the other half is reaping

The host cleanup after 0.2.14 found 39 superseded PyCharm formations and
15 Codium formations retained at up to 7 GB each, and a BuildKit cache of
645.9 GB in 2561 entries, one copy of the IDE tree per formation build.
The named-build-context fix stops the transfer; a reaping policy for
superseded canonical formations and their cache entries, keeping the
newest per surface and anything a container uses, is the other half, and
the launcher already prints that it does not reap. Both belong to this
record's design review.
