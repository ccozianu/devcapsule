# Unit Tests

[Development](README.md) · [Developer environment](developer-environment.md) · [Source layout](source-layout.md) · [Integration tests](integration-tests.md) · [End-to-end tests](e2e-tests.md)

## Running them

```text
cd devcapsule-src
.venv/bin/python -m nox -s tests          # the suite, with coverage
.venv/bin/python -m pytest tests/test_project_init.py -k regenerate   # one module, one pattern
```

Pytest's configuration is in `pyproject.toml`: `testpaths = ["tests"]`, the
project root on `pythonpath`, branch coverage of the `devcapsule` package
with a terminal report of missing lines, and the default selection
`-m "not integration and not e2e"`. So a bare `pytest` under `tests/` is the
unit suite; the heavier suites are chosen by marker, never by accident. The
`flaky` marker runs a test for visibility with a temporarily non-blocking
result; the other markers belong to the heavier suites.

The hosted runner runs exactly this: the GitHub Actions workflow
`tests.yml` installs the locked environment, runs `pytest tests/` with
coverage, publishes the summary and the badge. It runs no Docker, by the
owner's standing rule, so everything the unit suite proves it proves with
fakes and files.

## What is in the suite

Sixty modules at the time of writing, about one per module or contract of
the package, in two places:

- `tests/test_*.py`, fifty-three modules, one per subsystem of the package:
  the command framework and CLI grammar, `project init` and the project
  commands, the resolution matrix and the base contract, materialization and
  image build, the components (Codium, PyCharm, Codex, Claude Code,
  Antigravity, PostgreSQL client), the contained display and its host-side
  client, the supervisor and the runtime entrypoint, the recursive-launch
  modules, release manifest, protocol and compatibility, version sets and
  upgrade recovery, workflow bootstrap and coordination, and the noxfile
  itself (`test_noxfile.py` checks the gate's own session wiring).
- `tests/configuration/`, seven modules that are the configuration
  boundary's proof: `test_architecture.py` asserts the domain/adapter
  dependency rule by inspecting imports; `test_adt.py` and `test_contract.py`
  state the laws of admission and resolution and the lifecycle's proof
  obligations independently of branch coverage; `test_invariants.py` holds
  the cross-boundary invariants partitioned by contract condition;
  `test_nodes.py` and `test_history.py` cover the node registry and the
  known-good history.

Tests are written from the contract: the module docstring names the
behaviour's ownership and invariants, and a test asserts a postcondition an
adopter can observe, not an implementation detail. Where the real path is
cheap it is exercised; where it needs Docker or a GUI it is controlled, and
the controlled parts are named in the docstring. The owner's standing
caution applies when adding tests beside new end-user functionality: a
fresh test can encode the same unvalidated assumption as the code it checks,
so prefer the existing laws and an acceptance step for what the user sees.

## Fixtures

`tests/conftest.py` holds two fixtures and nothing else:

- `host_launch_by_default`, autouse: makes launcher tests behave as if they
  run on the host, since the launcher translates bind sources when it finds
  itself inside a capsule and the suite is often run from one.
- `built_pex`: the executable under test, `DEVCAPSULE_PEX_UNDER_TEST` when
  set, otherwise `dist/devcapsule-local.pex`; it fails with the Nox session
  to run when the file is missing. The integration and end-to-end suites use
  it; the unit suite does not need an artifact.

Everything else is local to its module: fakes for Docker and vendor
services, temporary XDG roots, and the `tmp_path` pytest provides.

## Resources

`tests/resources/` holds versioned inputs:

- `golden_locks/`: platform locks the matrix must keep producing for the
  named need sets, one per combination (`pycharm-minimal`, `pycharm-full`,
  `codium-node`, `codium-agents`, `codium-antigravity`, `dogfood`). A matrix
  change that alters one is a deliberate, reviewed change.
- `compat/`: artifacts produced by earlier released clients, never
  regenerated, proving R-COMPAT-001: a newer client needs no user action
  for a project, checkout or lock an older one created. [Its README](../../devcapsule-src/tests/resources/compat/README.md)
  names each client and what was templated.
- `sample_projects/`: three sample projects as submodules, fixtures for the
  project model; they have their own suites and are excluded from this one
  by `norecursedirs`.
- `supervisor_driver.py`: a driver that runs the supervisor over a JSON
  child-set specification, used by the supervisor and runtime tests.

## Type checking

`nox -s typecheck`, also inside the gate, runs mypy over the package, the
tests, the noxfile and the release scripts with the settings in
`pyproject.toml`. Tests are typed like source; an optional dependency a
test imports, Playwright for instance, carries an explicit ignore with its
reason rather than a loosened configuration.
