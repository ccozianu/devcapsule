# Local PyCharm Materialization And Python Entrypoint

Date: 2026-07-29

Status: active next task

## Objective

Replace the current dogfood image bridge with a reproducible image-formation
path that does not require MyCodeSpace.ai to distribute JetBrains binaries.
DevCapsule will publish a redistributable base, download a pinned current
PyCharm release directly from JetBrains on the user's workstation, verify it,
and materialize the complete runnable image locally.

At the same time, replace the monolithic PyCharm Bash entrypoint with a tested
Python runtime package. Separate generic capsule initialization from a
parameterized JetBrains/PyCharm component adapter.

"Current PyCharm" means the version selected by the curated resolution catalog
when the platform lock is generated. The resulting lock must pin an exact
version, upstream URL, checksum, and recipe version; runs must not silently
float to a newer release.

## Delivery Model

DevCapsule components have two delivery policies:

1. `redistributable`: the component may be installed into a base or complete
   image published by MyCodeSpace.ai.
2. `local-materialization`: the DevCapsule client acquires the component from
   its upstream vendor and adds it only to a workstation-local image.

The policy describes distribution, while a deterministic materialization
recipe describes installation. PyCharm uses `local-materialization`:

- download the pinned archive directly from JetBrains's public URL;
- verify its pinned digest before using it;
- do not proxy, mirror, or embed it in a MyCodeSpace.ai-published image;
- leave JetBrains EULA acceptance, account login, and licensing to the user;
- show a clear notice before acquisition or first launch that PyCharm is a
  JetBrains product, is downloaded from JetBrains, and is governed by
  JetBrains's terms. Acknowledging this notice does not accept the vendor EULA
  on the user's behalf.

The committed platform lock describes immutable materialization inputs. The
resulting local image ID and materialization cache are workstation state.

Materialization is a host-side image-formation step that completes before the
project container starts. When the required completed image is absent, the
DevCapsule client downloads and verifies the locked PyCharm archive, then uses
the locked redistributable base to build a new workstation-local image that
contains both `/opt/jetbrains/pycharm` and a reusable component runtime
template. It then runs that completed image with a checkout-specific runtime
plan supplied from outside the image. The client does not run the bare base
and ask its container entrypoint to download or install PyCharm just in time.
The runtime entrypoint performs no component acquisition; it only initializes
the capsule from the supplied plan and executes the already-installed
foreground IDE.

### Local image identity and discovery

A completed PyCharm image uses this local repository and tag pattern:

```text
devcapsule-local-pycharm:<materialization-identity>
```

`<materialization-identity>` is the first 20 hexadecimal characters of a
SHA-256 identity derived from the immutable base identity, the locked PyCharm
version and artifact digest, and the materialization recipe version. For
example:

```text
devcapsule-local-pycharm:5d4f9c0e7a31b8926f10
```

The stable `devcapsule-local-pycharm` prefix makes these images recognizable
in the ordinary local image list, while the content-derived tag makes reuse
deterministic and prevents different materialization inputs from sharing a
tag. Materialized images also carry machine-readable labels including:

- `devcapsule.image.kind=materialized`;
- `devcapsule.materialization.recipe-version=<version>`;
- `devcapsule.component.jetbrains.version=<version>`;
- `devcapsule.component.jetbrains.sha256=<digest>`.

The labels support reliable inspection and filtering independently of the
human-readable repository name. DevCapsule checks for the deterministic image
name before downloading the archive or rebuilding, and reuses the local image
when it already exists.

### Intended clean-clone user experience

The acceptance scenario begins with the DevCapsule client already installed
and Docker plus the host GUI prerequisites available. The project repository
already contains `.devcapsule/devcapsule.toml` and the matching committed
platform lock, so an ordinary user does not run `devcapsule init`, generate a
lock, build the base, supply a PyCharm archive, or invoke an IDE-specific build
command.

The intended operator-level script is:

```bash
set -euo pipefail

git clone "$PROJECT_GIT_URL" "$CHECKOUT"
cd "$CHECKOUT"

test -f .devcapsule/devcapsule.toml
test -f .devcapsule/devcapsule.linux-amd64.lock

devcapsule config resolve
devcapsule run
```

For V1, configuration before those final two commands is an iterative CLI
process, with direct editing of the developer-owned checkout TOML also
available. DevCapsule distinguishes required choices from optional choices
with defaults. `config resolve` is the user's explicit signal that the choices
are complete; it validates them and writes the generated plan, or reports the
remaining decisions without materializing or launching. V2 is intended to
make `devcapsule run` the primary interaction and subsume this resolution step
through a graphical configuration flow, initially envisioned as an embedded
local web application opened in the browser. That V2 flow removes the separate
command from ordinary interaction but retains the logical review boundary
before acquisition, image formation, host exposure, and launch.

On a new checkout, `config resolve` must be able to establish the
developer-owned checkout record and safe convention-based state roots without
requiring the user to adopt legacy directories. It validates the manifest and
matching platform lock, records no host authorization merely because the
project recommends it, and writes the generated local resolution. Adopting or
sharing existing state remains a separate explicit action.

On the first `run`, DevCapsule must:

1. discover and validate the project, checkout, generated resolution, and
   current-platform lock;
2. derive the deterministic completed-image name and reuse it if it is already
   present;
3. otherwise ensure the exact locked redistributable base is local, display
   the JetBrains vendor notice, download the locked PyCharm archive directly
   from JetBrains on the host, and verify its SHA-256 digest;
4. stop before building or launching if verification fails;
5. build the `devcapsule-local-pycharm:<materialization-identity>` image on the
   host and record its materialization labels;
6. start that completed image with the project, managed persistent home, and
   component state mounted, using bridge networking and no ambient Docker
   socket, sudo, credentials, devices, or other host permissions; and
7. keep PyCharm foreground-attached so closing the IDE ends the container.

The acquisition notice is not JetBrains EULA acceptance. Product licensing,
login, and EULA interaction remain between the user and JetBrains inside the
launched IDE.

For this repository, controlling the host Docker daemon is recommended only
for work that needs the full test suite. The user authorizes that relaxation
separately, for example as a run-once choice:

```bash
devcapsule run --docker-daemon host-socket
```

The committed recommendation must never turn into access implicitly. A second
ordinary `devcapsule run` with unchanged locked inputs must reuse the local
artifact cache and completed image without downloading or rebuilding. IDE and
tool state from the first session must remain available through the persistent
state mounts.

Useful acceptance inspection after the IDE exits includes:

```bash
docker image ls devcapsule-local-pycharm
docker image ls --filter label=devcapsule.image.kind=materialized
```

The committed dogfood lock now pins the local v019 base identity, PyCharm
2026.2.0.1 artifact and digest, variant, delivery policy, and materialization
recipe. `config resolve` bootstraps a clean default checkout record, and
`images build --type environment` creates or strictly reuses the canonical
materialized image. The remaining integration gap is `project run`: it does
not yet invoke materialization automatically or deliver a checkout-specific
runtime plan from outside the shared image.

## Redistributable Default Base Image

The first redistributable base is a complete, curated Linux development base,
not a minimal Python image and not an IDE image. It uses Ubuntu 24.04 as its
root filesystem and contains the common development and runtime utilities that
are presently installed by the Python-owned PyCharm image builder. This
includes the compiler/debugger toolchain, Git and SSH clients, network and
process diagnostics, Docker client and optional daemon tooling, X11 and Mesa
runtime libraries, `tini`, `gosu`, and the public-default Node.js/npm
tooling baseline. The exact package and tool versions remain deterministic
image-formation inputs and must be represented by the base recipe/version and
immutable base-image identity in the platform lock.

The base contains Python **3.12**. “Python 12” is not a Python release name;
for this implementation it means the Python 3.12 interpreter supplied for the
PEX. Ubuntu 24.04 is the initial platform because its supported distribution
Python is 3.12. The image must expose `python3.12`, and the PEX shebang and
automated inspection must select that interpreter rather than an unpinned
ambient Python version.

The normal DevCapsule distribution artifact is reused inside the image:

```text
/opt/devcapsule/bin/devcapsule.pex
```

The base-image build copies the already-built `devcapsule.pex` into that
location with executable mode. It does not separately copy
`devcapsule-src/devcapsule/container_runtime`, install a second DevCapsule
wheel, or maintain
a container-only dependency set. The PEX already contains the host CLI,
`devcapsule.container_runtime`, their shared contract/object model, and pinned
Python dependencies. Consequently the exact same PEX digest can be inspected
and compared outside and inside the image.

The generic OCI process configuration is:

```dockerfile
ENTRYPOINT ["/usr/bin/tini", "--", "/opt/devcapsule/bin/devcapsule.pex", "runtime"]
CMD ["/etc/devcapsule/runtime-plan.json"]
```

Splitting `ENTRYPOINT` and `CMD` this way makes the executable role immutable
while leaving the plan path visible and overrideable for inspection and
testing. The base does not contain a PyCharm plan. Running the bare base either
with its default missing plan or with an invalid plan must fail clearly before
starting an application. Local materialization adds the component installation
and reusable component template; launch supplies the deterministic plan at
`/etc/devcapsule/runtime-plan.json`.

PEX extraction and interpreter caches must not depend on a writable image
root. The PEX is built with `/tmp/devcapsule-pex-root` as its runtime root;
`/tmp` remains the per-container writable location under the normal read-only
root profile. Persistent application configuration and state belong only in
the declared home and state slots, never in the PEX cache.

The base image carries at least these labels:

- `devcapsule.image.kind=base`;
- `devcapsule.base.recipe-version=<version>`;
- `devcapsule.pex.sha256=<digest>`;
- the immutable source revision used to build the PEX and image.

Names and final registry coordinates remain publication configuration rather
than runtime behavior. The build must accept a local output tag so the base can
be built and inspected before any registry publication.

The default-base build is a separate Python-owned image specification. It may
reuse composable apt, tooling, file-copy, label, and entrypoint components from
`devcapsule.image_build`, but it must not call the PyCharm builder or source
assets from `devcapsule.assets.pycharm`. The subsequent workstation-local
materialization uses the immutable base identity and adds only the verified
JetBrains installation plus its generic component template. Project
scaffolding is not part of either image layer.

### Base-image verification

Automated plan and rendered-context tests must prove that:

- Ubuntu 24.04 is the default root image and Python 3.12, `tini`, and `gosu`
  are installed;
- the selected development-utility and public-tooling baseline is present;
- the PEX is copied once to `/opt/devcapsule/bin/devcapsule.pex`, its digest
  label matches the input artifact, and its mode is executable;
- OCI `ENTRYPOINT` and `CMD` have exactly the generic values above;
- no PyCharm asset package, JetBrains URL/archive, `/opt/pycharm` tree,
  JetBrains runtime plan, or PyCharm-specific environment/default command is
  included;
- `devcapsule.pex runtime` is covered by both source and PEX smoke tests.

Host-level inspection of a built base must additionally record:

- the base image ID and recipe/source labels;
- `python3.12 --version` and successful PEX startup through that interpreter;
- the SHA-256 digest of the in-image PEX compared with the host input;
- the configured entrypoint and command;
- a filesystem/package search demonstrating the absence of JetBrains content.

The PEX is DevCapsule's Apache-2.0 distribution, but its bundled dependencies
and all base packages/tools retain their own licenses. Publication therefore
also requires retaining applicable license and notice material and recording a
machine-reviewable component inventory. This does not change PyCharm's
`local-materialization` policy or grant redistribution rights for JetBrains
artifacts.

## Runtime Architecture

The distributable base contains a versioned, tested Python runtime entrypoint,
not a PyCharm-specific entrypoint. Its responsibilities are generic:

- parse and validate a structured runtime plan;
- establish the container user identity and privilege-drop boundary;
- prepare persistent home, XDG roots, runtime directories, and declared state
  slots;
- configure only explicitly authorized Git, SSH, Docker, sudo, graphics, and
  related runtime facilities;
- select a component adapter and `exec` its foreground command so application
  exit continues to own the container lifecycle.

The JetBrains adapter is parameterized rather than PyCharm-hard-coded. Its
configuration declares the installation path, launcher, properties environment
variable, state-slot mapping, and other JetBrains-product details. The adapter
generates the IDE properties file and foreground command. Other IDE adapters
reuse generic initialization without copying it.

Persistence belongs to the component interface rather than shared runtime
options. The component template declares persistent-home/XDG use and any
exceptional component-local slots, including lifecycle, sensitivity, scope,
storage, concurrency, ownership, deletion, and reconstruction semantics.
Generic host planning namespaces and binds those declarations; the adapter may
map its own configuration keys to local slot names. A component that uses only
standard `HOME` or XDG locations declares no slots and requires no named field
in shared runtime code.

The package should use focused modules with clear contracts, for example:

```text
devcapsule/
  container_runtime/
    entrypoint.py
    contract.py
    identity.py
    filesystem.py
    git.py
    docker.py
    graphics.py
    components/jetbrains.py
```

Python orchestrates existing system tools such as `gosu` and `dockerd`; it
does not reimplement their security-sensitive behavior.

`devcapsule-src/devcapsule/assets/pycharm/bootstrap-project.sh` is project
scaffolding, not runtime initialization or a PyCharm component. Do not migrate
it into the runtime package. Retain, retire, or move its still-supported
behavior to the client-side `devcapsule init`/template path separately.

## Done Criteria

This task is complete when all of the following are true:

1. A new Ubuntu 24.04 DevCapsule base image can be built and inspection proves
   it contains Python 3.12, the base development-tooling baseline, and the
   normal `devcapsule.pex` wired to its generic runtime command, but no
   PyCharm/JetBrains binaries, archives, installation tree, runtime plan, or
   PyCharm-specific default command.
2. The platform lock no longer points only at the prebuilt local
   `mycodespace.ai/pycharm:debug-v018` image. It pins the immutable
   redistributable base, exact PyCharm component artifact and digest, component
   delivery policy, and materialization recipe version.
3. On a workstation without the final local image, DevCapsule displays the
   vendor notice, downloads the pinned PyCharm archive directly from
   JetBrains, verifies its digest, and deterministically materializes a local
   image. Digest failure stops without building or launching.
4. Neither the PyCharm archive nor the locally completed PyCharm image is
   pushed to or required from a MyCodeSpace.ai/Docker Hub registry.
5. The completed local image uses the generic Python entrypoint and the
   parameterized JetBrains adapter; generic runtime setup is not duplicated in
   a PyCharm Bash entrypoint.
6. Automated tests cover the runtime-plan contract, generic setup planning,
   JetBrains configuration/property generation, component delivery-policy
   enforcement, notice behavior, download/digest failures, materialization
   planning, and final foreground command. Coverage remains part of the normal
   pytest/Nox gate.
7. `cd devcapsule-src && python -m nox -s build` passes, including source and PEX
   smoke coverage for the new path.
8. A newly materialized dogfood image launches this checkout through
   `devcapsule run` and works at least as well as `debug-v018`: existing
   persistent home and PyCharm state are reused, the established project path
   is preserved, GUI and IDE operation work, licensing remains a user/vendor
   interaction, explicitly requested Docker and sudo access work, and PyCharm
   remains foreground-attached to the container lifecycle.
9. Host inspection records the base and local-image identities, absence of
   JetBrains content from the base, verified upstream artifact digest, mounts,
   user identity, requested host capabilities, network mode, and foreground
   process tree without exposing credentials.

The existing network and Docker-option parity work follows this task. The new
runtime contract must leave those facilities generic and explicit, but this
task must not grow into implementing every outstanding runtime option before
the new image can dogfood successfully.

## Requirements

- Root: R-PRODUCT-001, R-PRODUCT-002, R-DOCS-002
- DevCapsule: R-IMAGE-BUILD-001, R-FRAMEWORK-001, R-PYTHON-MVP-002,
  R-PYTHON-MVP-003, R-SCOPE-001, R-DOCKER-001
- Architecture: D-0001 capability-first CLI model, especially curated
  resolution, locked materialization inputs, and workstation-local image state
