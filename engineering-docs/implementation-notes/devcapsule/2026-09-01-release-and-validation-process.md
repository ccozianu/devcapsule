# Releasing A New DevCapsule Version

This is the canonical operator guide for releasing DevCapsule. On 2026-09-11,
the product owner adopted the successful v0.2.11 process as the process for
new versions. Project management owns this release-process decision and its
documentation; completing it does not depend on delegation to another
workstream. The guide was originally recorded on 2026-09-01.

The normal sequence is **prepare → publish an RC → validate the downloaded RC
→ record acceptance → integrate → tag the accepted source → verify the final
release**. An ordinary CLI release reuses its pinned base. The workflow builds
and publishes the artifacts; the operator supplies acceptance and performs
integration and tagging.

## Operator Checklist

The commands below use v0.2.11 as the worked example. For a new release,
substitute its version and candidate number; never recreate or move an existing
published tag. Run Git commands from the repository root. Python commands use
the checkout-local environment described in the [developer setup](../../../README.md#developer-setup).

1. **Prepare a committed release slice.** Select the version and scope, record
   the full preparation-baseline SHA, and run `nox -s build` from
   `devcapsule-src` through `.venv/bin/python -m nox -s build`. Keep source edits
   on the selected workstream branch. `release-X.Y.Z` is a retained ref to the
   release source, not a change of editing workstream. A maintenance patch may
   start from the previous final tag when main contains unrelated or unready
   work. Choose its integration method before promoting it.
2. **Publish the first candidate.** Create the matching release ref and an
   immutable `vX.Y.Z-rc0` tag, then push them atomically using the commands in
   *Release Identity And Trigger*. Wait for **Publish DevCapsule PEX** to pass
   and publish a non-draft GitHub prerelease with all three assets: the PEX,
   its checksum file, and `release-manifest.json`.
3. **Validate the published candidate.** Download and checksum-check its PEX;
   use that executable for smoke/E2E testing. The [published-executable smoke
   commands](../../../devcapsule-src/README.md#end-user-artifact) are documented
   in the CLI README. Use the full-base `--build-base` mode when validating
   the base recipe; ordinary CLI releases need not rebuild or publish a base.
   Record actual evidence for changed GUI, login, and provider behavior.
   Fixture tests cannot supply that acceptance. For a source fix, commit it,
   advance the release ref without dropping earlier candidates, and publish
   the next RC number. Repeat until an exact candidate is accepted.
4. **Record acceptance.** Run `prepare-promotion.py` as shown below with the
   accepted RC, preparation baseline, accepting operator, and evidence. Review
   the generated record. For v0.2.11 the accepted candidate was **RC3**, not
   RC0 or a later workstream tip. Commit the record on the integration side,
   leaving the accepted candidate's source unchanged.
5. **Integrate.** Deliver the release changes and acceptance record through
   the normal PR process, then fetch and verify them on remote `main`. Follow
   the repository's merge policy. If integration rewrites commit identities,
   use the documented `reviewed` evidence method instead of claiming ancestry.
   A scoped exception is a separately authorized alternative, not the normal
   release path. Do not rebase the tested candidate to make it match main.
6. **Publish the final tag at the accepted candidate commit.** Use the final
   tagging commands below. Wait for the final backend run to finish. It
   rebuilds version metadata, checks frozen inputs against the RC, and repeats
   the automated gates. A pushed tag alone does not mean a successful release.
7. **Verify delivery.** Confirm the GitHub release is non-draft and is a final
   release, with all three assets. Download them into a fresh directory, check
   `sha256sum --check devcapsule.pex.sha256`, make the PEX executable, and run
   `./devcapsule.pex version --json`. Check its version, build mnemonic, and
   source revision against the final tag and acceptance record. Record the
   release URL, successful Actions run, and verification result in the owning
   workstream's handoff. Retain the release branch and candidate tags.

## The Successful v0.2.11 Reference

| Fact | Accepted value |
|---|---|
| Release branch | `release-0.2.11` |
| Candidate | `v0.2.11-rc3` |
| Candidate and final source commit | `94e798f1d1a7aaab93ae3e47d9636471448a8e66` |
| Preparation baseline | `3f028eeb97d7de6bce5b9f2ac2faf0a1b940cb61` |
| Integration evidence | `ancestry` |
| Final tag | `v0.2.11` |

The [committed acceptance record](../../releases/v0.2.11.json) identifies the
candidate checksum and the exact scope of acceptance. The [candidate backend
run](https://github.com/ccozianu/devcapsule/actions/runs/34333414510) and
[final release](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.11)
are the corresponding published evidence. The record covers the release/build
change and does not claim fresh GUI/login or provider acceptance. Preserve that
distinction when using it as a template for a release with different changes.

## Release Identity And Trigger

Prepare a release on `release-MAJOR.MINOR.PATCH` and push an immutable candidate
tag such as `v0.2.11-rc1` at the prepared commit. A patch can start from the prior
release tag rather than current main. `release-*` refs are durable release
anchors, separate from workstream selection, as authorized on 2026-09-09.

```text
git branch release-0.2.11 HEAD
git tag -a v0.2.11-rc0 -m 'DevCapsule 0.2.11 candidate 0'
git push --atomic origin release-0.2.11 v0.2.11-rc0
```

Use a new commit and RC number for fixes, advance the release branch, and keep
previous tags unchanged. `.github/workflows/release-pex.yml` requires the tag's
commit to belong to the matching release branch. Candidates do not require main
integration. Main stays open; do not rebase tested release source onto it.

The tag supplies the package version. `scripts/build-pex.sh` stamps package
metadata and `_build_info.json` in a temporary directory: `v0.2.11-rc1` becomes
`0.2.11rc1`, and `v0.2.11` becomes `0.2.11`. No version-bump commit is needed.
The source version remains the local-build baseline.

## Automated Candidate Release

The tag workflow:

1. Verifies the tag/branch identity, runs syntax checks, unit tests and mypy.
2. Recovers exact existing assets, or builds the self-contained PEX.
3. Records source identity, base digests, checksum, build-input hashes, dependency
   distribution fingerprints and the embedded Python fingerprint in the manifest.
4. Runs packaging integration tests, a clean-machine proof with no Python or
   networking, Docker component-install reuse and exact launcher delivery tests
   for both surface families, and runtime-session tests on each pinned base.
   Fixture IDEs do not claim real GUI or authenticated provider smoke.
5. Retains build artifacts, creates a draft release, downloads and compares its
   bytes, and repeats the clean-machine proof against the download.
6. Publishes candidates as GitHub prereleases with Latest disabled.

An incomplete or inconsistent staged asset set fails explicitly. Recover partial
uploads from the retained Actions artifact. Reruns verify and test the existing
bytes; they never replace published candidate assets or move tags.

## Acceptance And Final Promotion

Accept an exact candidate's checksum and source commit with smoke/E2E evidence.
Generate the reviewable record on the integration side:

```text
cd devcapsule-src
.venv/bin/python scripts/prepare-promotion.py v0.2.11-rc3 \
  --baseline FULL_PREPARATION_BASE_SHA --accepted-by OPERATOR \
  --evidence 'Exact candidate smoke result and Actions run URL'
```

The helper downloads and checksum-verifies the candidate and creates
`engineering-docs/releases/v0.2.11.json`. It does not perform or invent smoke
acceptance. Commit the record and integrate the candidate through normal PR
delivery. Keep the release branch and accepted tag at their tested source commit;
main can additionally contain the acceptance record and unrelated development.

The record has schema version 1, `tag`, `candidate-tag`, `source-revision`,
`candidate-sha256`, `accepted-by`, a nonempty `evidence` list, and `integration`:

- `ancestry` (helper default): `baseline` identifies the preparation base; the
  accepted candidate must be an ancestor of main, including ordinary merge commits.
- `reviewed`: additionally supply `main-commits` (full SHAs), `reviewed-by`,
  `rationale`, and `covers-release-delta: true`. Every referenced commit must be
  reachable from main. The reviewed assertion covers the entire baseline-to-RC
  delta, including adaptations in a cherry-pick or squash; patch IDs alone do
  not establish that claim.
- `exception`: additionally supply `authorized-by`, `rationale`,
  `forward-port-owner`, and `follow-up`. This is a scoped authorization in a
  reviewed engineering record, not a boolean bypass. Baseline still applies.

After the record and integration reach main:

```text
git tag -a v0.2.11 'v0.2.11-rc3^{commit}' -m 'DevCapsule 0.2.11'
git push origin v0.2.11
```

The backend checks release-branch membership, reads the record from a captured
main revision, validates acceptance/integration, downloads the published candidate
and verifies its checksum, then builds final-version bytes from exactly the same
source SHA. It compares base, dependency and Python fingerprints with the candidate
and reruns all automated gates before final publication. The final manifest embeds
the record and its main revision. Later main commits do not invalidate retries if
the accepted record remains unchanged. Final publication uses GitHub's legacy
Latest selection, which considers semantic version; candidates explicitly disable
Latest. Tagging is the publication trigger and needs no second approval prompt.

This is source promotion with a final packaging build, not byte-for-byte PEX
promotion: version metadata changes intentionally. A new source fix requires a
new candidate. Neither a broken main nor unrelated main changes require bringing
that work into a maintenance release. The initial implementation automates each
tag's backend and promotion checks; acceptance, normal PR integration, and the
final tag remain operator/agent steps.

## Failed Candidates And Publication Retries

A failed candidate is not promoted. Source or build-input fixes receive a new
commit and RC tag. Published tags and assets remain immutable; do not delete or
replace them to make an old candidate appear successful. If a final release
needs a source fix, prepare a new patch release through the same RC process.

For an infrastructure failure with unchanged source and inputs, rerun the
failed Actions run or dispatch the workflow with its existing `release_tag`.
The backend verifies and reuses staged assets. If an upload stopped partway,
restore the missing original assets from that run's retained Actions artifact;
do not rebuild replacements or overwrite assets. Resume publication only once
the complete set passes verification. The workflow retains build artifacts for
30 days; if the originals cannot be recovered, use a new candidate (or a new
patch version if the final tag was already published).

## Runtime Delivery And Base Lifecycle

Recipe 7 produces a base containing the existing OS libraries and developer
tools, with no DevCapsule PEX or entrypoint added by the recipe. The builder's
source identity remains recorded as provenance; `--pex`, when supplied, selects
provenance metadata, not bytes to embed. Running the packaged builder uses its
own source identity by default. The public-revision checks still apply.

The launcher copies its exact executable PEX into the materialized environment
at `/opt/devcapsule/bin/devcapsule.pex`. Its SHA-256 is part of the formation
descriptor, so a launcher update creates a new local formation and cannot reuse
an image carrying an older runtime. Component installation stages are shared
between those formations. Source-form launches explicitly select a built PEX
through `DEVCAPSULE_RUNTIME_PEX`, or invoke the built artifact directly.

Ordinary CLI releases reuse the catalog's pinned base. In particular, v0.2.11
can use the published v0.2.10 base and replace its inherited runtime in the
derived image. Existing base tags and project locks are unchanged. This avoids
a mandatory Docker Hub publication, digest repin, sample migration, and owner
smoke cycle every time the CLI version advances.

Base maintenance has an independent cadence: update dependencies, build and
validate the base, publish under a fresh immutable name, then review its digest
pin as an ordinary catalog change. A base is not named after every CLI release.
This change does not introduce automatic base publication or choose a new
permanent base-naming scheme. Explicit dependency updates remain necessary for
security fixes; retaining a cached base is not a dependency-update policy.

## Independent Component Contributions

`ContributionComponent` describes installation steps and the paths they export.
The renderer emits a shared baseline stage, an independent stage for each
contribution, and a final image assembled with `COPY --link --from`.

- Base builds isolate Node, Temurin and Maven. Maven explicitly consumes the
  JDK stage for its installation-time verification; it exports only Maven.
- Environment builds isolate the IDE and each ancillary component. All of a
  component's npm packages remain one offline install, preserving the vendor's
  multi-file layout. Environment variables are composed in the final image.
- Component contexts have stable names independent of sibling ordering. A
  different IDE, agent or launcher does not invalidate another installer.
- BuildKit supplies cache identities from the parent image, platform, commands
  and file inputs. A version/recipe/parent change rebuilds the affected stage.
  Reuse lasts while that builder retains its cache; another host or cache
  pruning requires rebuilding. No component images or credentials are published.
- Only declared installation paths are exported. System-package side effects
  cannot be handled by copying an arbitrary installation directory; apt's
  shared baseline remains a complete filesystem layer.

The Docker regression test makes an installer emit a random identifier, builds
two different images with reordered/changed siblings and a changed launcher,
and verifies identical identifiers. A changed recipe must emit a new one.
This tests reuse itself rather than only the generated Dockerfile text.

## Validation And Integration

`nox -s build` remains the local gate. The explicit Docker cache/runtime check
is `python -m pytest --no-cov -m e2e tests/e2e/test_component_cache.py` after
building the local PEX and making `ubuntu:24.04` available. The release workflow
runs it against the actual release artifact. Packaging tests also build a tag
whose version differs from the source baseline and verify source remains clean.

Product-owner GUI/login acceptance for changed component behavior remains part
of development and integration. Fixture tests do not replace that evidence or
convert provisional matrix entries. Publishing an unchanged, accepted
component combination should not repeat the manual release walk.

Docker's behavior is documented in [multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
and [`COPY --link`](https://docs.docker.com/reference/dockerfile/#copy---link).
