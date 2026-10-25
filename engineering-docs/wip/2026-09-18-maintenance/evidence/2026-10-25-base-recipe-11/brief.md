# Implementation brief for the Codex + gpt-6-astra pair: pin the published recipe-11 base

You implement; Claude Fable 5.1 reviews, with the owner, Costin Cozianu, who merges. This is an ordinary catalog change in the sense of the runbook's *Release Fixes And Main*: a new base pin in the embedded resolution matrix, the locks that follow it, the tests that name it, and two documentation sentences. The release records, the changelog and the status files are the release driver's and are not yours.

## Your checkout

You are in the git worktree at /home/devcapsule/worktrees/maintenance-impl-3, on the branch `ws-maintenance/base-recipe-11-pin`, branched from `release-0.3.0` at `b19d654`, the rc6 publication record. Work only there. Do not touch the main checkout at /workspace/301e4208ef81-ChatGPT_Codex nor any other `/home/devcapsule/worktrees/*` worktree.

Read first: `AGENTS.md`; `WORKFLOW-LOCAL.md` (*Review Partners In This Checkout*, *GitHub Integration*, *Validation Commands*); `devcapsule/resolution_matrix.py`, the header comment, `_BasePin`, the three base pins and the comments above them, `_LINUX_AMD64_MATRIX`; `devcapsule/images/contract.py` and `images/base.py` (`BASE_RECIPE_VERSION`, `BASE_SERVICES`); `devcapsule/images/tooling.py` (`NODE_VERSION`, `TEMURIN_VERSION`, `MAVEN_VERSION`); `tests/test_base_contract.py`, `tests/test_resolution_matrix.py`, `tests/test_project_init.py`; and the commit `3debc28`, the previous base repin, which is the model for this one in shape and in the style of its matrix comment and commit message.

## GitHub CLI

In every shell you run, first execute:

    . /opt/xtras/miniconda3/etc/profile.d/conda.sh && conda activate gh

Then `gh` is logged in to github.com as the owner's account against ccozianu/devcapsule. Do not edit `.bashrc` or any shell profile.

## Validation environment

Your worktree's `devcapsule-src/.venv` exists with the source installed editable from this worktree. Run every pytest and nox invocation from `devcapsule-src` with `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex-impl-3"`. The gate is the full one: `.venv/bin/python -m nox -s build`. Do not build images and do not start capsules. Docker is available for `docker buildx imagetools inspect`, which reads the registry without pulling; use it to verify the image, nothing more.

## The image

The owner built the base from the published rc6 executable and pushed it on 2026-10-25:

    docker.io/mycodespaceai/devcapsule-base:v0.3.0.rc6
    digest sha256:8c97d308b4ac8172ce91ef4f96406063bfcd85a55efb09d4a23e795b10a834a3

Re-inspect the registry copy by digest before you write anything and record what you read in the PR body. The reviewer read: linux/amd64; `devcapsule.base.recipe=ubuntu-24.04`, `recipe-version=11`, `display=contained`, `runtime=launcher-supplied`, `services=docker-cli,java,maven,node,postgresql-client,python`, `webconsole=/opt/devcapsule-webconsole`; `devcapsule.source.revision=2ed8ecf536b0d653056ac35792cae413a6d6732a`, the rc6 tag revision; `org.opencontainers.image.version=v0.3.0-rc6`; Temurin `25.0.4+7`, Maven `3.9.16`. Your pin states what the registry copy states.

## The task

1. **One new base pin**, appended after the recipe-9 pin, newest last as the matrix requires: mnemonic `v0.3.0-rc6`, family `ubuntu-24.04`, recipe 11, display contained, runtime launcher-supplied, `satisfies` the six services of the label with the versions the base pins (Python `3.12`, Node from `NODE_VERSION`, Java from `TEMURIN_VERSION`, Maven from `MAVEN_VERSION`, `docker-cli` and `postgresql-client` unversioned), lock table `reference` at the digest above, `build-mnemonic` `v0.3.0-rc6`, `contract` `ubuntu-24.04@11`. The comment above it says, in the style of the recipe-9 comment: what recipe 11 adds over recipe 9 (the web console under `/opt/devcapsule-webconsole` with its process and resource monitor; recipe 10 added the console, 11 the monitor), that it is the same family and inherits every validation, who built it with which executable from which revision, when it was pushed and under which tag, that the digest was read from the registry and the copy re-inspected, and the evidence: the owner's test of 2026-10-25 on the locally built twin of this recipe, the console's configuration page working after the rc5 regression was repaired in PR #281.
2. **The recipe-9 pin stays.** Retirement is an explicit act of the owner under D-0007 and is not asked for. Locks that still reference it, adopters' and the sample projects', keep resolving as before. Resolution prefers the newest base, so a regenerated lock moves to recipe 11 by itself.
3. **The matrix version advances** to `embedded-28`.
4. **The locks that follow the matrix are regenerated**, not hand-edited: every golden lock under `tests/resources/golden_locks/` and this repository's own `.devcapsule/devcapsule.linux-amd64.lock`, with the executable built from your tree, through `project init --regenerate` or the test helper the golden locks are generated with, whichever the tests already use. The diff of each lock must be the generator comment's matrix version, `resolution-matrix-version`, and the `[base]` table, and nothing else; show one such diff in the PR body. Do not touch `website/.devcapsule/` or anything under `tests/resources/sample_projects/`: those are submodules.
5. **The tests that name the base** change to the new pin: `test_base_contract.py` (the pinned digest and contract in `test_recipe_declares_the_current_contract`; the consent description in `test_consent_names_the_contract_and_the_recipe_source` now reads `built by v0.3.0-rc6` and links `blob/v0.3.0-rc6/` with the current recipe source path, since this image carries the recipe-source label; keep a case that an image built before the move still points at the legacy path), the `v0.2.12-rc5` mnemonic strings in `test_resolution_matrix.py` and `test_project_init.py` where they assert the newest base, and any other test the gate shows. Add one test that a lock pinned to the recipe-9 digest still resolves as a known base of the family, so item 2 is proven and not assumed.
6. **Two documentation sentences.** `docs/getting-started/first-session.md`: the example contract `ubuntu-24.04@9` becomes `ubuntu-24.04@11`, and the page's `updated` date is today. `docs/configuration/local-base.md`: the opening paragraph still presents a local base as the way to a newer recipe than the published one; with recipe 11 published, make its example honest without rewriting the page, for instance by saying the message appears on a checkout whose lock still pins an older base, and date the page. Nothing else under `docs/` changes.

## Acceptance

- Full gate green from `devcapsule-src`: `PYTEST_ADDOPTS="--basetemp=/opt/devcapsule-gate/pytest-codex-impl-3" .venv/bin/python -m nox -s build`, both sessions.
- `grep -rn 8837edd devcapsule-src/devcapsule devcapsule-src/tests .devcapsule docs` returns the retained recipe-9 pin in the matrix and the one test of item 5 that proves it still resolves, nothing else.
- With the executable built by the gate, in a scratch copy of the `pycharm-minimal` golden fixture, `project init --regenerate` writes the recipe-11 base and `project config show` names `ubuntu-24.04@11` in its base line, no container started. Quote the base line in the PR body.
- `git diff --check` clean. One commit, or two if you separate the regenerated locks from the code; the message names the base, its recipe, its digest's first eight characters, who built and pushed it and when, and what the evidence is, as `3debc28` does. Never the words substrate, edge, gen1 or gen2.
- The PR targets `release-0.3.0`, title `Pin the published recipe-11 base, v0.3.0-rc6`, body with the registry inspection, the lock diff, the regeneration evidence and the gate counts, ending with the line `🤖 Generated with Codex`.

## What you must not do

- Do not retire a pin, change a component pin, add a validation edge or touch any other matrix row.
- Do not edit `engineering-docs/releases/`, any `CURRENT-STATUS.md`, `intake-dispositions.md`, this `evidence/` directory, or run `devcapsule workflow publish`.
- Do not pull the image, build an image or start a capsule.
