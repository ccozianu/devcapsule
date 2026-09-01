# DevCapsule Release And Validation Process

Recorded 2026-09-01 at the product owner's direction, from the v0.2.8
release preparation. This is the process as the tooling actually enforces
it; where a step is convention rather than enforcement, that is said
explicitly.

## Version Identity

The distribution version is authored in exactly one place: the `[project]`
table of `devcapsule-src/pyproject.toml`. Everything else derives it:

- `python -m nox -s bump -- patch|minor|major|X.Y.Z` rewrites that single
  line and refuses malformed, equal, or decreasing versions.
- Runtime code reads the authored file in a source checkout and installed
  metadata elsewhere (`build_info.current_build_info`); built artifacts
  carry the record `scripts/build-pex.sh` stamps.
- The official release tag is exactly `v<version>` — `build-pex.sh`
  refuses a `--release-mnemonic` that differs from the checked-in version
  or is not an exact tag for checkout `HEAD`, so tag and version cannot
  disagree in a published artifact.
- A source checkout has no build record at all; its absence is what
  defines a source-form run, reported as `v<version>-local`. Contributor
  binaries report `v<version>-local-<platform>`.

## Validation

Two halves, by who can run them:

**The mechanical gate** is `python -m nox -s build`, one command running
in order: locked dependency install, version-form check, Python and shell
syntax checks, mypy, the unit suite, the source-tree CLI smoke, a local
PEX build, the same smoke against that artifact, and the packaging
integration tests. The public `dist/devcapsule.pex` is built only when
the repository is clean and the revision is published; otherwise the
session finishes with the local validation artifact and says so. Any
agent or CI run can execute this gate.

**The product-owner smoke** is manual and deliberate: for component work
it is the workstream's validation bar (unit tests pass plus a smoke test
performed by hand by the product owner) and it bounds integration pace.
Plan sessions to end at smoke-testable points.

## Release Steps, In Order

1. **Land the content on `main`** through ordinary pull requests. Release
   artifacts are cut from published revisions only; `build-pex.sh`
   verifies the exact commit is advertised by the public GitHub
   repository.
2. **Bump the version** — one edited line via `nox -s bump` — and land it
   by pull request so the release revision's CI is green *before* the tag
   exists. This ordering is convention, not enforcement: the tag is
   immutable identity, so nothing should be tagged that CI has not
   already accepted.
3. **If the release must repin the base image**, do it before tagging
   (see *Base Image Releases* below): the released PEX embeds the
   resolution matrix, so a repin that misses the tag ships a client
   pinning the previous base.
4. **Tag the release revision** `v<version>` and push the tag.
5. **The `release-pex.yml` workflow** fires on the tag: it rebuilds from
   the tagged revision, runs tests and type checks, builds the scie PEX,
   asserts the embedded mnemonic equals the tag, runs the packaging
   integration tests, proves the artifact on a clean machine without
   Python or networking, publishes `devcapsule.pex` and its checksum to
   GitHub Releases, then downloads the published assets and proves them
   again. Re-running via `workflow_dispatch` against an existing tag
   verifies the published assets byte-for-byte instead of republishing.
6. **Verify as an adopter would**: download the release asset, check the
   checksum, run `devcapsule.pex version --json`, and confirm the
   mnemonic, version, and source URL name the tagged revision.

## Base Image Releases

The base image is a separate, less frequent artifact; most releases ship
only the PEX. When a release changes what containers must understand —
new runtime-plan adapters, entrypoint behavior — the base must be rebuilt
and repinned, and the ordering is forced by a dependency cycle: the
matrix pin needs the pushed image's digest, and the released PEX needs
the matrix pin.

1. Build the base from a published revision:
   `devcapsule images build --recipe ubuntu-24.04 --pex dist/devcapsule.pex
   --source-revision <sha> --tag docker.io/mycodespaceai/devcapsule-base:<label>`.
   The build refuses a PEX without a verified public revision and stamps
   the PEX digest and source identity into the image labels.
2. Push the image and record the registry digest.
3. Land the repin: the new digest and build mnemonic in `_BASE_TABLE`
   and an advanced `MATRIX_VERSION` in `resolution_matrix.py`.
4. Only then tag the distribution release, so the published client's
   embedded matrix pins the new base.

The base's own embedded runtime PEX is one commit behind the release it
serves (it predates the repin commit); this is harmless because the
runtime never consults the resolution matrix, and the image labels record
the true source revision. Building and pushing the base is manual as of
this writing; automating it as a `workflow_dispatch` job with a Docker
Hub credential was assessed and deferred.

## Compatibility Bounds

- The matrix version is informational (`R-COMPAT-001`): a newer client's
  matrix changes what is *generated next time*, never the validity of a
  lock that stands.
- A newer client runs against an older base as long as the base's
  embedded runtime PEX understands the runtime plans the client's locks
  produce — validated 2026-09-01: the 0.2.8 client operates correctly
  against the v026 (0.2.7-era) base for the surfaces that base already
  knew. The failing direction is a lock naming an adapter the base
  predates (the codium surface against v026), which the container rejects
  at plan time; until a repinned base ships, such launches need the
  runtime-PEX override volume
  (`-- --volume <host-pex>:/opt/devcapsule/bin/devcapsule.pex:ro`, host
  path, since raw passthrough options are not bind-translated).

## Known Gaps

- The bump-by-PR-before-tag rule and the base-release ordering are
  convention; only the tag↔version weld and the published-revision checks
  are enforced. A future `release-base.yml` and any pin-advance policy
  belong with the component update mechanism work already recorded in the
  component-catalog workstream.
