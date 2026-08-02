# Docker Hub Namespace And Publication Plan

Date: 2026-07-15

Status: namespace and initial push path validated; official V1 artifacts remain blocking

## Why This Note Exists

DevCapsule needs a documented path for publishing prebuilt Docker images for
users. This note records the current Docker Hub naming constraints, account
limits, and the concrete follow-up work needed before V1 image publication.

## Namespace Findings

- Docker Hub image names live under a Docker Hub namespace, which is either a
  user namespace or an organization namespace.
- The practical Docker Hub naming shape is:

```text
<docker-namespace>/<repository>:<tag>
```

- A domain-style namespace such as `mycodespace.ai/devcapsule` is not the
  expected Docker Hub repository naming model.
- The realistic namespace candidates to claim are more like:

```text
mycodespaceai/devcapsule
mycodespace/devcapsule
```

- Docker domain verification is useful for proving organizational control over
  `mycodespace.ai`, but it does not turn the Docker Hub namespace into a
  domain-style image path.

## Current Docker Hub Limit Findings

At the time of research, the Docker documentation indicates:

- authenticated Personal accounts get 200 pulls per 6 hours;
- Personal accounts get unlimited public repositories;
- Personal accounts get up to 1 private repository;
- Pro, Team, and Business accounts get unlimited pull rate and unlimited
  public/private repositories;
- Docker documents storage and transfer under fair-use language rather than a
  simple fixed free upload/storage quota on the main usage page.

Treat these limits as documentation-backed guidance that should be rechecked
immediately before public release.

## Recommended Publication Direction

For V1, prefer an organization-owned Docker Hub namespace rather than a
personal namespace.

Adopted organization namespace:

```text
mycodespaceai
```

The reusable development base uses a dedicated repository:

```text
mycodespaceai/devcapsule-base:<recipe-and-release>
```

Environment-image publication remains a separate later decision because the
current PyCharm environment is materialized locally from the published base
and checksum-pinned vendor artifact.

## Initial Push Validation

On 2026-08-02, the user confirmed a successful host-authenticated push of:

```text
docker.io/mycodespaceai/devcapsule-base:ubuntu-24.04-v019
```

Docker Hub assigned repository digest:

```text
sha256:637f646a9de962cb399025c2bf3817b08e242d2a4416b49a202cf06763852feb
```

The digest resolves locally to image ID
`sha256:7e81e49d7b9c3a82faae8af4de4e3eed927f13261d8f0040af0aa23f64963dee`,
the same content used to form the validated v019 dogfood environment. The
committed Linux dogfood lock now uses the globally resolvable digest reference,
not the mutable discovery tag or workstation-local image ID.

This validates the namespace and push path only. The image records source
revision `unknown`, a local canonical-name label, and the superseded ambient
Gemini CLI baseline, so it is not an official V1 release artifact. The next
candidate must use agent-neutral base recipe version 2 or later.

A subsequent digest pull succeeded from the credential-isolated dogfood
capsule, confirming that the repository is public and the reference resolves
without the user's Docker Hub credentials. Because the layers were already
present in the shared Docker store, the required clean-store pull validation
remains open.

## V1 Release Versioning

Internal checkpoint tags such as `v019` are dogfood identifiers and must not
be presented as polished V1 versions. Release candidates and general
availability artifacts use semantic product versions:

```text
mycodespaceai/devcapsule-base:ubuntu-24.04-1.0.0-rc.1
mycodespaceai/devcapsule-base:ubuntu-24.04-1.0.0
devcapsule-1.0.0-rc.1.pex
devcapsule-1.0.0.pex
```

Floating convenience tags may be considered only after the immutable release
is validated. Committed locks always use the registry digest, never a version
tag. Official artifacts must record the actual source revision and version,
publish checksums/digests and a basic security-scan result, and pass clean
pull/download checks. These are V1 trust inputs for a human authorizing one
exact digest; they are not verifiable build provenance. Signed SBOMs,
attestations, automated provenance/publisher verification, and policy
enforcement are deferred to the explicit V2 supply-chain task.

Before V1 publication, source disclosure must be consistent across artifact
boundaries. Base images should carry `org.opencontainers.image.source` and
`org.opencontainers.image.revision` in addition to the existing
`devcapsule.source.revision`; the source value must identify the public GitHub
repository and the revision must be a full public commit. The PEX must embed
the same commit and canonical GitHub commit URL at packaging time and expose
them through a read-only command such as `devcapsule version --json`, even when
the PEX is copied away from its source checkout. Release validation compares
the image and PEX values, verifies that the URL resolves publicly, and rejects
`unknown`, a dirty-tree pseudo-revision, abbreviated hashes, or unrelated
commits. This improves inspectability but does not claim that the artifacts are
reproducible or cryptographically proven to derive from the disclosed commit.

## Required V1 Follow-Up Work

1. Keep the `mycodespaceai` Docker Hub organization and repository ownership
   documented.
2. Verify whether `mycodespace.ai` should also be added as a verified domain
   for the Docker organization/company account.
3. Retain `mycodespaceai/devcapsule-base` for reusable bases and decide later
   whether any pre-materialized environment family warrants another repository.
4. Decide which Docker subscription tier is acceptable for projected pull
   volume and private/public needs.
5. Build release-ready images from the active `devcapsule` implementation.
6. Embed and expose one full public GitHub revision in the PEX, record the same
   revision and public source URL in OCI metadata, and add release checks that
   prove the two disclosures agree and resolve publicly.
7. Perform a clean pull validation using the published digest; the initial push
   path is already validated.
8. Document the end-user pull commands in current user docs.

## Minimal Push Flow To Reuse Later

```bash
docker login
docker tag devcapsule-base:release-candidate \
  mycodespaceai/devcapsule-base:ubuntu-24.04-1.0.0-rc.1
docker push mycodespaceai/devcapsule-base:ubuntu-24.04-1.0.0-rc.1
```

Adjust the repository and tag names once the final publication layout is
chosen.

## Open Questions

- Should V1 publish only the default Ubuntu base, or also promote the CUDA
  recipe after its specialized validation closes?
- Which release host should publish the PEX and checksum manifest?
- Is a Personal account sufficient for early testing, or should V1 start on an
  organization-backed paid plan immediately?
