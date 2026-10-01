# Source Layout

[Development](README.md) · [Developer environment](developer-environment.md) · [Unit tests](unit-tests.md) · [Integration tests](integration-tests.md) · [End-to-end tests](e2e-tests.md)

## The repository

- `devcapsule-src/` — the Python distribution project: packaging, tests,
  runtime assets, and the `devcapsule/` import package. The `-src` suffix is
  deliberate: in a clone named `devcapsule` the three layers are
  `devcapsule/devcapsule-src/devcapsule`, checkout, distribution project,
  import package, instead of three identically named directories.
- `devcapsule-src/devcapsule/assets/project_workflow/` — the reusable
  workflow definition and the project-instance templates embedded in the
  executable; the root `WORKFLOW.md` is their source.
- `docs/` — the product documentation, versioned per release by the
  [content–website contract](../specifications/product/content-website-contract.md).
- `website/` — the presentation project, a Git submodule; content stays here.
- `engineering-docs/` — requirements, specifications, decisions, design
  notes, implementation notes, releases, bugs, workstream records, and this
  directory; placement rules in [its README](../README.md).
- `docker4pycharm/` — the frozen shell-based MVP the project started from;
  reference only. Its maintained descendant is
  `devcapsule-src/devcapsule/assets/docker4pycharm/`, extracted by installed
  builds for the remaining legacy-compatible operations; the two have
  diverged, and `devcapsule.compat.script_path()` still prefers the frozen
  root copy for delegated scripts, so source checkouts and installed builds
  can run different revisions. See [its README](../../docker4pycharm/README.md).
- `.devcapsule/` — this project's own capability declaration and platform lock.
- `component-status/` — the generated compatibility feed's operations.

## The package

The command trees are noun-oriented, `devcapsule project …` for a checkout's
lifecycle and `devcapsule images …` for workstation images, and the model is
capability-first: a project declares what it needs, the platform lock selects
exact components, and developer-owned configuration authorizes host access.
The package follows the responsibilities of the launcher and the runtime:

```text
devcapsule/
  commands/                 CLI grammar, dispatch and presentation
  configuration/            Project declarations, local decisions and plans
    model.py                Configuration value API
    values.py               Ordinary values, types and omissions
    bindings.py             Directory and secret-source bindings
    authorization.py        Host/acquisition consent and base trust
    nodes.py                Canonical node names and registry
    review.py               Complete assessment and effective host decisions
    resolution.py           Derived plan values and serialization
    manifest.py             Project declaration validation and projection
    fingerprints.py         Source fingerprints
    freshness.py            Current and predecessor checkpoint freshness
    documents.py            Versioned document admission and codecs
    storage.py              File discovery, ownership and atomic writes
    execution.py            Admission of a stored checkout for execution
    operations.py           Initialization and persistent edit orchestration
    history.py              Successful-run snapshots
  components/               Trusted component declarations and contributions
  launch/                   Host-side launch adapters
    pycharm/                Shared host launcher and PyCharm image utilities
  container_runtime/        In-container plan interpretation and supervision
```

Use `devcapsule.configuration` for the value API: `Configuration`,
`Resolution`, `ConfigurationReview`, `HostAccess` and
`ProjectConfigurationError`. File and lifecycle adapters use the named
`storage`, `execution`, `operations` and `history` modules. The configuration
core depends on domains and codecs only; it does not depend on those
adapters, on CLI commands, on image realization or on launch, and its
internal imports are acyclic, imports inside functions included. The
architecture tests under `tests/configuration/` enforce these boundaries
beside the configuration laws and representation tests; see
[Unit tests](unit-tests.md).

`launch/pycharm` holds the shared host launcher that `project run` uses and
the retained PyCharm image utilities; the legacy `pycharm run` command is
retired and `commands/_pycharm.py` keeps the build and check-runtime grammar
with the retirement diagnostic. The remaining top-level modules keep their
historical responsibilities: `host_daemon` and the `recursive_*` modules for
launching from inside a capsule, `resolution_matrix` and `base_contract` for
the embedded component matrix and the base-image contract, `materialization`
and `image_build` for environment images, `display_client` for the host
side of the contained desktop, `project_information` for the read-only
`project info`, and `workflow_*` for the coordination commands.
