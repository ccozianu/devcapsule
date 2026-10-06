# Image layers, the local cache, and how the final image is composed

Status: design as built on 2026-10-06 (named build contexts, one context
root, digest-keyed unpacked trees), on the maintenance branch for 0.3.0.
The reuse of installed Docker content and the reaping of superseded
formations are not built; they are the design review recorded in the
[installed-IDE record](../../bugs/devcapsule/2026-09-24-installed-ide-docker-reuse.md).

Code: `devcapsule/images/build.py` (the plan, the renderer, the builder),
`devcapsule/materialization.py` (the recipe, the cache, the identity),
`devcapsule/environment_realization.py` (who calls what).

## What a layer is

The word "layer" is used loosely for Docker images; here it names three
different things, and the design depends on keeping them apart.

**A contribution** is the unit DevCapsule composes with. It is one
component's installation, built in its own BuildKit stage from a common
baseline and exporting named paths: the IDE under `/opt/jetbrains/pycharm`,
a browser under its own directory, an agent's npm tree, a wheel-installed
tool with its `venv/`. A contribution is declared by `ContributionComponent`
with a name, the build steps that produce it (a directory copied in, files,
`RUN` steps such as an offline `npm install`), and the paths it exports.
BuildKit keys the stage on its parent image, its commands and the content
of what it copies in, and on nothing else: not the other contributions,
not the final image's name or labels. That is what lets one contribution's
stage stay cached while the launcher, the labels, or a sibling change.

**A formation** is one complete image: a base, the interactive surface, the
ancillary components, the runtime launcher, the boot contract, and the
labels that describe all of it. Its identity is the SHA-256 of a canonical
descriptor (`formation_descriptor`): platform, base image identity, each
component's version and artifact digest, the recipe and its version, the
runtime launcher's digest and the public command name. Change any of those
and it is a different formation with a different canonical image name,
`devcapsule-local-<surface>:<identity prefix>`. The launcher's own digest is
part of it by design, so a launcher upgrade is a new formation.

**A Docker layer** is what the daemon stores: one filesystem diff per
Dockerfile instruction. DevCapsule does not reason about these directly;
they fall out of the composition below. The one thing it controls is
that each contribution's export reaches the final image as a single
`COPY --link` instruction, so a contribution is one layer of the final
image and that layer is reused verbatim across formations that share it.

## How it is cached locally

Four caches, each keyed by content, each at a different stage of the
pipeline. All of them live under the launcher's cache root,
`$XDG_CACHE_HOME/devcapsule` (`~/.cache/devcapsule`), except the last,
which is Docker's.

| Stage | Where | Key | Reused when |
|---|---|---|---|
| Verified archive | `artifacts/<sha256>` | the lock's SHA-256 of the download | the same artifact is needed by any project or formation; the digest is re-verified on every use |
| Unpacked tree | `unpacked/<sha256>/` with a completion marker | the same SHA-256 | any formation of the same IDE or component version; unpacked once (15 s for PyCharm), then found in under a millisecond |
| Local-source snapshot | BuildKit's state, keyed by the context root's path and the named context's name | the main context root `build-contexts/context` plus the context name | every build from the same launcher cache: BuildKit syncs only what changed in the tree (1.29 MB of 3.69 GB when nothing did) |
| Stage and layer cache | Docker's build cache and image store | the stage's parent, commands and copied content | any later build whose stage inputs are identical; the final image's name and labels do not enter the key |

Two points in this table are the design, not defaults.

The unpacked tree is a stable path on purpose. BuildKit's incremental
transfer of a local source diffs the directory against the snapshot it
holds for the same shared key, and it derives that key from the path of
the main context root. A fresh temporary context per build, which 0.2.15
used, meant a new key every time, a full 3.69 GB transfer every time,
and a new copy of the tree in BuildKit's local-source cache every time.
The builder therefore reuses one context root per launcher cache,
serialized by a lock beside it, and the trees it attaches as named
contexts stay where they were unpacked.

The completion marker is written last and renamed into place with the
tree. An unpack interrupted at any point leaves a directory without a
marker, which the next launch removes and redoes. Two launchers unpacking
the same digest at once both finish; the second finds the first's tree
and discards its own, identical by construction.

What is not cached: nothing is pruned. Verified archives, unpacked trees,
superseded formations and BuildKit's cache entries accumulate until the
reaping policy from the design review exists. The launcher already says
so when it builds a new formation.

## How the final image is composed

`render_build_context` turns a plan into one Dockerfile with this shape.
The example is the PyCharm surface with Codex as an ancillary component;
other surfaces differ only in the contributions.

```dockerfile
# syntax=docker/dockerfile:1
FROM <base image by digest> AS devcapsule-baseline
# apt packages the recipe needs, if any

FROM devcapsule-baseline AS pycharm
COPY --from=pycharm-copy-dir-0 / /opt/jetbrains/pycharm/
# the surface's post-install steps

FROM devcapsule-baseline AS codex
COPY codex-copy-file-0 /opt/codex/package.json
RUN npm install --offline --ignore-scripts ...

FROM devcapsule-baseline
COPY --link --from=pycharm /opt/jetbrains/pycharm /opt/jetbrains/pycharm
COPY --link --from=codex /opt/codex /opt/codex
COPY copy-file-0 /etc/devcapsule/component-runtime-template.json
RUN ln -s /home/devcapsule/xtras /opt/xtras ...
COPY copy-file-1 /opt/devcapsule/bin/devcapsule.pex
RUN ln -sfn /opt/devcapsule/bin/devcapsule.pex /usr/local/bin/devcapsule
ENV PATH=/opt/xtras/bin:${PATH}
LABEL devcapsule.materialization.descriptor=...
LABEL devcapsule.materialization.identity=...
ENTRYPOINT ["/usr/bin/tini", "--", ...]
```

Read it top down.

1. **The baseline** is the project's base image, selected by digest from
   the platform lock and validated as a DevCapsule base before anything
   is built. Every stage starts from it, so every contribution is built
   against the exact userland it will run in.
2. **One stage per contribution.** The surface's installation tree arrives
   as a named context, `--build-context pycharm-copy-dir-0=<unpacked tree>`,
   read in place; small inputs such as a generated `package.json` or a
   verified tarball travel in the ordinary context. Steps that need to run
   (`npm install`, wheel installs, native package installs) run inside the
   stage, offline, with scripts refused, so a stage's result is a function
   of verified inputs only.
3. **The final stage** starts again from the baseline and copies each
   contribution's exports with `COPY --link --from=<stage>`. `--link`
   makes the copied layer independent of the layers before it, so the
   same contribution layer is shared, not rebuilt, by every formation
   that includes it. Then come the pieces that are per formation rather
   than per contribution: the component runtime template, the `/opt/xtras`
   alias into the persistent home, the launcher executable itself and its
   public command name, the `PATH` and component environment, the labels
   carrying the canonical descriptor and identity, and the boot contract
   (`tini` and the entrypoint).
4. **Verification after the build.** The built image is inspected and its
   labels compared with the descriptor; a mismatch is an error, never a
   silent acceptance. An existing image whose content is right but whose
   boot configuration predates the contract is repaired by a
   configuration-only rebuild from its own tag, not rebuilt from scratch.

What a launcher upgrade costs after this design: a new formation identity,
a new final stage (a few small `COPY` and `RUN` steps and labels), every
contribution stage reported `CACHED`, and 1.29 MB of context transfer for
the IDE tree instead of 3.69 GB. Measured in the installed-IDE record.

## What the design review still owes

- **Reuse of installed Docker content before acquisition.** A compatible
  installation already in a contribution layer should satisfy a new
  formation without the archive cache, without unpacking, and without a
  download, including on a machine where the launcher's filesystem cache
  is empty. The stage cache gives most of this when the cache is warm; it
  gives nothing on a fresh cache root or after a prune.
- **Reaping.** A policy for superseded formations, their BuildKit cache
  entries, unpacked trees and archives: keep the newest per surface and
  anything a container uses; say what is promised about retention and
  what ordinary `docker system prune` may remove.
- **Whether the contract is general or PyCharm-first**, and what enters a
  contribution's identity beyond its artifact digest: the recipe version,
  the base contract, the platform.
