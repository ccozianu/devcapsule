# End-To-End Tests

[Development](README.md) · [Developer environment](developer-environment.md) · [Source layout](source-layout.md) · [Unit tests](unit-tests.md) · [Integration tests](integration-tests.md)

The end-to-end suites run real Docker: they build images, start containers,
launch capsules and look at what happens. They are opt-in, they run on a
developer's machine or inside a capsule with host Docker, and never on the
hosted runner. During a release they run against the downloaded candidate,
which is how the acceptance record gets its Docker proofs; see the
[release runbook](../implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md).

## Entry points

| Session | Runs | Needs |
|---|---|---|
| `nox -s e2e` | the `e2e` tests that are not `recursive_e2e`, `contributor_e2e` or `ide_smoke`; with `-- --build-base` also `base_build_e2e` | Docker; the executable |
| `nox -s pex_clean_machine` | the clean-machine proof: the executable on a networkless image with no host Python | Docker; the executable |
| `nox -s recursive_dogfood_e2e` | `project recursive-e2e run` on this checkout, then the `recursive_e2e` and `contributor_e2e` tests | a capsule with host Docker and host networking |
| `nox -s ide-smoke` | the `ide_smoke` tests, one per IDE surface; `-- --display` adds Playwright evidence, `-- --surface NAME` limits the run | Docker; the executable; the recommended base |

Every session selects the executable the same way: `DEVCAPSULE_PEX_UNDER_TEST`
when set, otherwise it builds `dist/devcapsule-local.pex`. When a candidate
is selected, `DEVCAPSULE_EXPECTED_RELEASE_VERSION` and
`DEVCAPSULE_EXPECTED_BUILD_MNEMONIC` assert its identity, and the session
logs the executable's checksum and source revision so the evidence names
exact bytes. `-- --build-network host` reaches the image builds that install
packages, for hosts whose bridge network has no DNS.

## The tests, and what each proves

| Test | Markers | Proves |
|---|---|---|
| `test_self_contained_pex.py` | `e2e` | The executable runs without a host Python and without network |
| `test_runtime_image.py` | `e2e` | Inside a disposable image: the runtime entrypoint, the supervisor's session end on `docker stop`, and the contained display's boundary: one token-gated bridge, no abstract X socket, no host credential, display processes as the capsule user, Openbox on DevCapsule's configuration |
| `test_component_cache.py` | `e2e` | A component installation is reused across images and invalidated by its recipe; a formation receives the exact launcher on a runtime-free base |
| `test_recursive_successor_lifecycle.py` | `e2e` | A successor capsule removed from outside is reported as failed, not lost |
| `test_built_base.py` | `e2e`, `base_build_e2e` | The full base built by the selected release's own CLI has the tools and no embedded runtime |
| `test_contributor_bootstrap.py` | `e2e`, `contributor_e2e` | A first-time contributor bootstraps in a disposable base, from a host or from inside a capsule |
| `test_recursive_local_clone.py` | `e2e`, `recursive_e2e` | The recursive E2E local-clone protocol, from a dogfood capsule |
| `test_ide_comes_alive.py` | `e2e`, `ide_smoke` | Each IDE surface comes alive in a fresh project: the desktop URL answers, an X11 window of the IDE's class exists on the capsule's display; optionally a screenshot and a recording |

## Drivers and helpers

Three modules under `tests/e2e/` are not tests; they are what the tests run:

- `contributor_bootstrap_driver.py` runs the isolated contributor bootstrap
  inside a disposable base container.
- `ide_session.py` launches a real IDE session with the executable under
  test and asks the capsule whether the IDE came alive: the table of IDE
  surfaces, the session context manager with its cleanup, the minimal X11
  client that reads top-level windows through the display socket so the
  image needs no X tools, and the optional Playwright capture. A new IDE
  surface is one row in its table.
- `tests/resources/supervisor_driver.py` runs the supervisor over a JSON
  child-set specification, shared with the unit tests.

The X11 probe in `test_runtime_image.py` and the one in `ide_session.py`
speak the core protocol over the Unix socket, enough for the setup
handshake, `InternAtom` and `GetProperty`; it is the deliberate alternative
to installing `xprop` in every image.

## Environment the tests read

| Variable | Set by | Meaning |
|---|---|---|
| `DEVCAPSULE_PEX_UNDER_TEST` | you, or the session | The executable under test |
| `DEVCAPSULE_EXPECTED_RELEASE_VERSION`, `DEVCAPSULE_EXPECTED_BUILD_MNEMONIC` | you, for a candidate | Its asserted identity |
| `DEVCAPSULE_E2E_BASE_IMAGE`, `DEVCAPSULE_E2E_BUILT_BASE`, `DEVCAPSULE_EXPECTED_BASE_SOURCE` | `-- --build-base` | The base the session built and its provenance |
| `DEVCAPSULE_EARLY_EXIT_E2E_IMAGE`, `DEVCAPSULE_CONTRIBUTOR_E2E_IMAGE`, `DEVCAPSULE_PEX_CLEAN_MACHINE_IMAGE` | the sessions | Disposable images the tests build or reuse |
| `DEVCAPSULE_E2E_BUILD_NETWORK` | `-- --build-network` | The network mode of image builds |
| `PLAYWRIGHT_BROWSERS_PATH` | you, optionally | Where `ide-smoke -- --display` finds or installs Chromium |

## Evidence

- `dist/e2e-base-build.json`: the base a `--build-base` run built, its image
  id, and the builder's identity and checksum.
- `dist/e2e-evidence/ide-smoke/<UTC time>-<id>/`: one directory per IDE
  smoke run, never overwritten, with `run.json` naming the executable and,
  per surface, the launcher and init logs, the window found, the records
  removed, and with `--display` the screenshot and the WebM recording of
  the browser session.
- The release runbook says which of these the acceptance record cites.

## Running inside a capsule

All of this runs from a capsule that has host Docker and host networking:
the launcher translates bind sources to host paths for nested launches, and
the IDE smoke puts its projects under the persistent home's E2E workspace for
that reason. `project recursive-e2e preflight --json` reports whether the
capsule is ready. The hosted runner runs none of it; that is a rule, not a
limitation to fix.

## Where the next end-to-end test goes

A new proof that needs Docker goes in `tests/e2e/` with the `e2e` marker,
plus a second marker when it needs a capsule (`recursive_e2e`), a
contributor base (`contributor_e2e`), a freshly built base
(`base_build_e2e`) or a real IDE (`ide_smoke`), so the right session picks it
up and no other does. Register a new marker in `pyproject.toml`, since
pytest warns about an unknown one at collection, and wire its session in
the noxfile; `test_noxfile.py` covers how each session selects the
executable under test, so a new session that selects one gets a case there.
