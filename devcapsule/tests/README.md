# DevCapsule Test Suites

DevCapsule separates tests by both directory and pytest marker. Directories
make scope and dependencies discoverable to humans; markers make selection
explicit for pytest, Nox, and CI.

## Test levels

### Fast tests

The existing `tests/test_*.py` modules exercise Python units and closely
coupled module behavior without requiring a built PEX or Docker daemon.

```text
python -m nox -s tests
```

### Integration tests

`tests/integration/` contains tests marked `integration`. They cross process or
packaging boundaries but do not require Docker. The tests execute the freshly
built `devcapsule.pex`, prove that `runtime --help` reaches the
container-runtime command, and verify that `version --json` exposes
self-contained build/source identity without consulting the checkout.

```text
python -m nox -s integration
python -m pytest --no-cov -m integration tests/integration
```

The Nox session builds `dist/devcapsule-local.pex` before running the tests.
That explicit local-only filename carries an unknown revision and prevents the
development gate from overwriting or masquerading as the strict public artifact
at `dist/devcapsule.pex`. Direct pytest uses the local test path and fails with
an actionable message when it has not been built.

### End-to-end tests

`tests/e2e/` contains tests marked `e2e`. They exercise real Docker image
build, inspection, and container execution. They require an explicit command:

```text
python -m nox -s e2e
python -m pytest --no-cov -m e2e tests/e2e
```

The first E2E test uses the production default-base image specification to
build a disposable image containing the freshly built PEX, configures the
generic OCI entrypoint, and runs
`devcapsule.pex runtime --help` inside the container. It defaults to the
locally validated dogfood image `mycodespace.ai/pycharm:debug-v018`, which
already provides Python 3.12 and `tini`. Override the cached base when needed:

```text
DEVCAPSULE_E2E_BASE_IMAGE=python:3.12-slim python -m nox -s e2e
```

The selected base must already exist locally. E2E tests do not pull images
implicitly, keeping network access and external image changes explicit.

The same E2E test then creates a small deterministic JetBrains-shaped archive,
acquires it through the production SHA-256 cache, materializes a second local
image, verifies the unpacked launcher and formation metadata, and confirms that
only the generic component template—not a checkout-specific runtime plan—is
baked into the shared image. It removes the original fixture and invokes
orchestration again to prove the already-materialized image avoids both
download and rebuild after strict descriptor verification. The real vendor archive is intentionally excluded
from this default E2E because the current Linux download is approximately
1.28 GB; a separately explicit vendor test will cover that path.

The contributor-bootstrap E2E launches a disposable managed base and performs
a clean local clone, isolated Python 3.12 venv creation, locked dependency
installation, editable package installation, and import-path verification. It
runs in two contexts: directly on a contributor host, where the owned workspace
is a direct bind source, or inside a recursive-ready DevCapsule, where the same
path is translated through inspected current-container mounts before use with
the host daemon. The test never mounts the Docker socket into the disposable
contributor container. Override the host-mode locked base with
`DEVCAPSULE_CONTRIBUTOR_E2E_IMAGE`; the selected managed base must already be
present locally. Each run creates an ownership-labeled user-defined bridge so
Docker's embedded DNS can reach the public package index without granting host
networking; both the container and network receive deterministic cleanup.

## Selection and gate policy

- `nox -s tests` runs only fast tests.
- Plain `python -m pytest tests` selects `not integration and not e2e` through
  the project pytest configuration. Explicit `-m integration` or `-m e2e`
  replaces that default selection.
- `nox -s integration` builds the PEX and runs integration tests.
- `nox -s build` includes fast tests, source smoke tests, PEX construction,
  PEX smoke tests, and integration tests.
- `nox -s e2e` is explicit and is not part of the default build gate yet.
- An explicit E2E run fails when Docker or its selected local base is missing;
  it does not silently pass through a skip.

GUI operation, licensing, credential reuse, and host capability validation
remain manual dogfood checks. Automated E2E tests must not use host networking,
privileged mode, Docker socket mounts, credentials, or unrelated host paths.
Every Docker resource must have a unique name/label and deterministic cleanup.

### Manual user-journey evidence

The former laptop-specific
`tests/manual/v1-second-checkout-dogfood.sh` acceptance script was retired on
2026-08-05 after the product owner manually accepted sustained use from the
second checkout. Its fixed personal paths, credential-bearing shared state,
GUI interaction, and broad host authorizations made further maintenance poor
value relative to the confidence gained.

The accepted evidence and the later V1 replacement task are recorded in
`implementation-notes/2026-08-03-next-functional-dogfood-stage-plan.md`. The
replacement will be an explicitly invoked, disposable multi-project E2E that
uses isolated temporary checkouts and XDG roots, exercises normal
configuration and materialization paths, inspects running containers, and
cleans only test-owned resources. GUI usability, third-party license prompts,
and real credential login remain manual checks.

## Adding tests

Use a fast test unless behavior genuinely crosses a packaging, process, or
Docker boundary. Decorate each applicable test with `@pytest.mark.integration`
or `@pytest.mark.e2e`. Keep integration tests independent of Docker. Keep E2E
images minimal, reuse production paths when they exist, and assert observable
behavior rather than implementation mocks.
