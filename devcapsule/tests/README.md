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
packaging boundaries but do not require Docker. The initial test executes the
freshly built `devcapsule.pex` and proves that `runtime --help` reaches the
container-runtime command.

```text
python -m nox -s integration
python -m pytest --no-cov -m integration tests/integration
```

The Nox session builds `dist/devcapsule.pex` before running the tests. Direct
pytest uses that same conventional path and fails with an actionable message
when the artifact has not been built.

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

### Manual user-journey tests

`tests/manual/v1-second-checkout-dogfood.sh` is the executable acceptance test
for the planned D-0004 clean-clone configuration journey on the current
dogfood laptop. It intentionally targets V1 commands that are not implemented
yet. It clones the repository at a second host path, registers a distinct
checkout identity, records ordinary values, state bindings, and host
authorizations, resolves the complete plan, and launches PyCharm twice. It
requires the local `devcapsule-local-pycharm:debug-v019` checkpoint alias and
verifies that the image uses the embedded DevCapsule PEX, generic component
template, externally supplied runtime-plan boundary, and generic Python
entrypoint rather than v018's PyCharm-specific Bash entrypoint. It also verifies the V1 managed-image marker, metadata version,
materialized kind, formation/base/component identities, and canonical-name
label used by `devcapsule images list`.

The test is deliberately excluded from Nox and CI. It shares explicitly chosen
credential-bearing state, opens a GUI, enables host Docker, host networking,
and development sudo, and therefore requires an informed human running it from
the intended workstation. It is both the acceptance procedure and a concrete
debugging target for the next implementation slice.

## Adding tests

Use a fast test unless behavior genuinely crosses a packaging, process, or
Docker boundary. Decorate each applicable test with `@pytest.mark.integration`
or `@pytest.mark.e2e`. Keep integration tests independent of Docker. Keep E2E
images minimal, reuse production paths when they exist, and assert observable
behavior rather than implementation mocks.
