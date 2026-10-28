---
description: Build a DevCapsule base image on your computer and select it for one checkout, when the published base lacks something the capsule needs, such as the web console.
weight: 6
updated: 2026-10-25
---
# Build and select a local base

Every capsule image starts from a base: the operating system, the toolchains,
the contained display and, since base recipe 11, the web console. The project
lock pins a published base, and that is what you get unless you choose
otherwise. A base built on your computer is the way to run a checkout on a
newer recipe than the published one; a checkout whose lock still pins an
older base can show this message:

```text
Web console: none on this base (ubuntu-24.04@9; the console needs base recipe 11 or later); the capsule runs without it.
  To build a base that has it:  devcapsule images build --type base --recipe ubuntu-24.04 --source-revision <revision>
  Then select it for this checkout; the steps: https://devcapsule.mycodespace.ai/docs/current/configuration/local-base/
```

The capsule still runs. Nothing below is required for everyday work; it is
how you get the newer base before the project pins one.

## Build the base

The launcher builds the base from the recipe it carries, and records its own
source revision in the image as provenance. Take the revision from
`devcapsule version`, or copy the command the launcher printed, which already
has it:

```bash
~/.local/bin/devcapsule version
~/.local/bin/devcapsule images build --type base --recipe ubuntu-24.04 \
  --tag devcapsule-base-local:recipe-11 \
  --source-revision 0123456789abcdef0123456789abcdef01234567
```

`--tag` is the local name you will select; choose one that says what it is.
The build installs the operating system packages and the toolchains and takes
a while the first time. If your Docker daemon's build network cannot resolve
names, add `--network host`. A launcher built from source rather than
downloaded has no public revision; it builds with `--allow-local-source`
instead of `--source-revision`.

When it is done, the base is in your local Docker store with its labels:

```bash
~/.local/bin/devcapsule images list
```

The listing shows the recipe, `ubuntu-24.04@11`, and the revision it was
built from. The published base and your local one are told apart by that
recipe and by where they live, not by a release number.

## Select it for a checkout

Run these from the project checkout, on your computer:

```bash
~/.local/bin/devcapsule project config authorize base-image devcapsule-base-local:recipe-11
~/.local/bin/devcapsule project run
```

The first command inspects the image, checks that it is a DevCapsule base
for your platform, and records its image ID in this checkout's own
configuration. It prints the ID it bound to and says that this
developer-owned selection overrides the published base recommendation for
this checkout. The second launches on it. On a recipe-11 base, the launcher
prints the web console link.

What the selection is, and is not:

- It is yours and stays on your computer, like every personal choice in
  [project versus personal](project-versus-personal.md). The project's lock
  still recommends the published base; collaborators are unaffected.
- It binds to the exact image ID. If you rebuild the base under the same
  tag, select it again.
- It is a qualification, not validation: a run on a local base proves that
  run, not the base, and a lock proposal from such a checkout says so.
- It cannot satisfy a mandatory guarantee the project declares, such as an
  capability minimum; see [capabilities](capabilities.md).

`devcapsule project config show` shows the override among this checkout's
answers.

## Back to the published base

```bash
~/.local/bin/devcapsule project config authorize base-image default
```

`default` accepts the lock's current pin and nothing more. The local image
stays in your Docker store until you remove it.
