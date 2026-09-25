---
status: confirmed
severity: minor
target: none
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

## Disposition, 2026-09-25

Owner ruling: reuse of installed IDE and other component layers across
formations is substantial work and is presumed outside the 0.2.14 release
cycle; keep it in attention with the rc3 measurements above as the case.
