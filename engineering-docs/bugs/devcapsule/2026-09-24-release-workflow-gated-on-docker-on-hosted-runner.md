---
status: closed
severity: blocking
target: 0.2.14
owner: maintenance
opened: 2026-09-24
closed: 2026-09-24
requirements: [R-PRODUCT-005]
---

# The release workflow gated candidates on Docker builds on a hosted runner

`v0.2.14-rc2`, tagged at `a779295` after a passing gate with zero missing
commits, produced no assets: the backend run failed in the step "Verify
pinned base availability and runtime sessions" at
`docker build` of the disposable runtime image, 42 seconds into a step that
had passed in 74 seconds for rc1 three hours earlier with identical test
code. The candidate's delta since rc1 never reaches that test, and the same
test against the same base digest with the same PEX source passed locally
in ten minutes. The failure was the runner's, and it decided the release.

## Root cause

Two defects, one of design and one of evidence:

1. The workflow ran three Docker-dependent proofs on a GitHub-hosted runner:
   the clean-machine proof by `docker run`, component-cache reuse and
   runtime sessions on every pinned base by `docker build`. A hosted runner
   is an environment nobody controls; its network, image cache and daemon
   vary between runs. A proof that depends on it gates the candidate on the
   runner rather than on the candidate. The owner's ruling on 2026-09-24:
   a test that runs Docker in an unknown environment is broken by
   definition, and no test on free infrastructure runs Docker.
2. The e2e helpers ran commands with `capture_output=True` and `check=True`,
   so a failing `docker build` raised `CalledProcessError` with the exit
   status only. The captured stderr, which names the cause, was discarded.
   The step log needs administrator rights to read, so the failure could
   not be diagnosed from the outside at all.

## Fix

- `.github/workflows/release-pex.yml` runs no Docker: the two clean-machine
  steps, the component-cache step and the runtime-session step are removed,
  with a comment recording the ruling. The workflow keeps the source tests,
  type checks, the PEX build, the packaging integration tests, and the
  download-and-compare verification of the published assets.
- The three proofs are local acceptance steps against the downloaded
  assets, run by the driving workstream and recorded in the release
  overview; the operator guide, `DEVELOPING.md` and the source README say so.
- `tests/e2e/test_runtime_image.py` `command()` and
  `tests/e2e/test_component_cache.py` `docker()` fail with the command's
  stdout and stderr in the message.

## Verification

- The workflow YAML parses; the edited modules collect and type-check; the
  full `nox -s build` gate passed on the branch (1064 tests, mypy, PEX
  smokes, nine packaged integrations).
- The next candidate's backend run publishes assets without a Docker step,
  and the local proofs pass against its download before owner testing.
- The rc2 tag stays where it is, without assets; tags never move.

## Closure, 2026-09-24

rc3 and rc4 published under the Docker-free workflow in about four minutes
each; the local proofs passed against both downloads. Owner accepted rc4.
