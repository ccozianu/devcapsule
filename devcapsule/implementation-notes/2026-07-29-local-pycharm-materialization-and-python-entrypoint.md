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

The package should use focused modules with clear contracts, for example:

```text
devcapsule_runtime/
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

`devcapsule/devcapsule/assets/pycharm/bootstrap-project.sh` is project
scaffolding, not runtime initialization or a PyCharm component. Do not migrate
it into the runtime package. Retain, retire, or move its still-supported
behavior to the client-side `devcapsule init`/template path separately.

## Done Criteria

This task is complete when all of the following are true:

1. A new DevCapsule base image can be built and inspection proves it contains
   the generic Python runtime entrypoint but no PyCharm/JetBrains binaries,
   archives, installation tree, or PyCharm-specific default command.
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
7. `cd devcapsule && python -m nox -s build` passes, including source and PEX
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

