# Current Status

This is the handoff for the next developer or agent. Git history and the linked
implementation notes hold completed-session detail; this file records only the
current state, evidence, and next step.

## Project

DevCapsule is a Python CLI for building and running reproducible, isolated
developer environments. The V1 target is described in [README.md](README.md),
[REQUIREMENTS.md](REQUIREMENTS.md), and
[devcapsule/REQUIREMENTS.md](devcapsule/REQUIREMENTS.md).

The canonical public repository is
`https://github.com/ccozianu/devcapsule`. The active branch is
`milestone/recursive-dogfood-e2e`, created from clean `main` revision
`237d4939f8d1dcfcfbe2061209f16f8692542c08`.

## Active Milestone

The current milestone is **Recursive Dogfood E2E — Build And Launch A
Successor From Inside DevCapsule**. Its execution plan is
[2026-08-06-recursive-dogfood-e2e-milestone-plan.md](devcapsule/implementation-notes/2026-08-06-recursive-dogfood-e2e-milestone-plan.md).

- Stages 0 through 3 are complete.
- Stage 3 closed with passing local-clone and contributor-bootstrap E2Es in
  both recursive and contributor-laptop contexts.
- Stage 4 is in progress. Its first checkpoint publishes the accepted v024
  base and selects its immutable registry digest in the project lock.
- Stages 5 and 6 have not started.
- No successor image has been built or launched yet.

The milestone is one part of the broader
[V1 gap plan](devcapsule/implementation-notes/2026-08-06-v1-gap-review.md).
PyCharm functional closure, the self-service configuration catalog, and V1
publication and acceptance follow it.

## Verified v024 Bootstrap

Development is running inside the accepted v024 PyCharm environment:

- source revision: `e2dae20abcd2b60fde8f4f7901e6b88b40f097df`;
- embedded PEX SHA-256:
  `fb278f145a583faba12df9c4a663b41cb60b0b508a769b050cfa4e088f13febc`;
- base: `devcapsule-local-base:v024`, image
  `sha256:56bbd10c54eb2b35044eb49f4f81c49602c73c9edd8b738a969d9340492f75df`;
- published recommendation:
  `docker.io/mycodespaceai/devcapsule-base@sha256:0c9ebc0c9744a525c160bba1a0f75dacd27cd16cb5dfee769f69bc2c3165fb81`
  (discovery tag `ubuntu-24.04-v024`);
- environment: `devcapsule-local-pycharm:9cdac50e4c802fff5077`, image
  `sha256:85a560c3f1fc55ded2991e555ed63fc3687d9905213622f0fa33f50e5db8c31b`;
- running container: `pycharm-isolated-costin-1786072465`.

Embedded-PEX preflight reports `READY`. It confirms the container and image
lineage, host Docker access, host networking, development sudo, display,
required mounts, and writable workspace.

The lock change deliberately leaves this checkout's prior base authorization
and generated resolution stale. Reauthorizing the new digest is a separate
developer-owned decision; no committed recommendation grants it automatically.

The checkout is expected to advance beyond the immutable v024 revision. Tests
must keep the v024 bootstrap identity separate from the selected source commit
and the artifacts generated from that commit.

The full Stage 2 handoff is in
[2026-08-06-recursive-dogfood-stage-2-execution-checklist.md](devcapsule/implementation-notes/2026-08-06-recursive-dogfood-stage-2-execution-checklist.md).

## Stage 3 Evidence

The executable acceptance specifications are:

- [test_recursive_local_clone.py](devcapsule/tests/e2e/test_recursive_local_clone.py):
  validates the recursive environment and makes an exact, independent,
  credential-free local clone;
- [test_contributor_bootstrap.py](devcapsule/tests/e2e/test_contributor_bootstrap.py):
  bootstraps a clean contributor environment from both supported launch
  contexts.

Observed results on 2026-08-07:

- inside v024, `python -m nox -s recursive_dogfood_e2e`: `2 passed`,
  `1 deselected`;
- directly on the laptop,
  `pytest --no-cov tests/e2e/ -m contributor_e2e`: `1 passed`, `2 deselected`
  in 28.39 seconds;
- ordinary repository gate: 223 fast tests and clean mypy over 85 files;
- cleanup inspection: no owned test container, network, or run workspace
  remained.

The contributor container uses host networking in both contexts because the
dogfood host blocks public package downloads from Docker bridge containers.
When invoked recursively, the test first proves through Docker inspection that
the current container is itself host-networked.

The filesystem-local clone does not depend on the developer's configured
`origin` URL. Stage 4 verifies canonical public artifact metadata separately.

## Next Step

Begin Stage 4. Compose the accepted Stage 3 clone and bootstrap protocols into
one retained, ownership-marked milestone run. From the clean clone, run the
full clean Nox gate, build and verify the revision-bearing PEX, then use that
PEX to build and inspect the successor base through the authorized host Docker
daemon.

Additional workspace, retry, corruption, redaction, and isolation hardening is
tracked in the
[V1 test backlog](devcapsule/implementation-notes/2026-08-07-v1-test-backlog.md).
It does not block the completed Stage 3 boundary.

## Known Follow-ups

- The bare v024 base contains the expected Node archive but does not add
  `/opt/node/current/bin` to `PATH`. This is a tooling usability issue, not a
  recursive-E2E blocker.
- DevCapsule will not support Gemini CLI. Active work must not install,
  configure, mount state for, or advertise it; absence checks are allowed as
  regression guards.
- V2 candidates include safe image/cache lifecycle commands and verifiable
  software-supply-chain provenance. They are not V1 blockers.

Keep isolation relaxations explicit and documented. In particular, changes to
host access, credentials, networking, devices, or mounts must preserve
`R-SCOPE-001`, `R-DOCKER-001`, and root `R-PRODUCT-002`.

## Validation

From `devcapsule/`:

```text
python -m nox -s tests
python -m nox -s build
python -m nox --no-reuse-existing-virtualenvs -s build
python -m nox -s recursive_dogfood_e2e
```

Use the clean-slate form when proving a milestone boundary. The recursive E2E
is on-demand because it uses the host Docker daemon and host networking.
