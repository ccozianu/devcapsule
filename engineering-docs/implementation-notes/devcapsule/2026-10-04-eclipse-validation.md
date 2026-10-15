# Eclipse IDE for Java Developers validation

Date: 2026-10-04. Workstream: `component-catalog`. Owner-requested component
addition and noVNC/Playwright smoke with a retained movie; no release or website
publication is part of this slice.

## Delivered behavior

`eclipse-ide` selects **Eclipse IDE for Java Developers 2026-09 R**, Linux x86-64,
from the [Eclipse package page](https://www.eclipse.org/downloads/packages/release/2026-09/r/eclipse-ide-java-developers).
`java-ide` continues to select IntelliJ. The entire vendor package installs at
`/opt/eclipse`, including its Java runtime and JDT, Git, Maven and Gradle tools.
The Eclipse adapter runs the native launcher as the ordinary capsule user with
`-data /ide-workspace`; no host display or credentials are required.

The `eclipse/workspace` state slot holds workspace preferences, project references
and local history, separate from source files in the mounted checkout. Eclipse's
[shared-installation mechanism](https://help.eclipse.org/latest/topic/org.eclipse.platform.doc.isv/reference/misc/multi_user_installs.html)
creates user configuration beneath the persistent home's `.eclipse/` directory.
The installation stays read-only. Importing a repository is an IDE operation;
the launcher does not create `.project` files in existing repositories.

The vendor archive's SHA-512 matched Eclipse's published checksum. Its SHA-256,
used by ordinary DevCapsule acquisition, is:

```text
1a836dcedcc353567f164964ecb251bf0477cffb26dec1cc49bcf6ec12d82eca
```

`components/eclipse_native_pin.py` pins the Ubuntu 24.04 WebKitGTK dependency
closure against the recommended v0.2.12-rc5 base: 66 distribution packages,
including WebKitGTK 2.52.6. SHA-256 values came from signed Ubuntu APT metadata
and every downloaded package matched. These files travel the ordinary artifact
cache and lock; one grouped directory is copied into the final image and dpkg
installs it offline. No OS package is installed on the developer's host, no base
image is changed and image assembly retains `--network none`. Package maintainer
scripts run during the container build, as they would under apt.

## Smoke and evidence

[Repeatable commands](../../development/e2e-tests.md#eclipse-java-smoke):

```sh
.venv/bin/python -m nox -s ide-smoke -- --agent --surface eclipse --component-browser
```

The shared AI scenario uses Codex/GPT-6 Astra to drive Playwright mouse/keyboard
input through noVNC. It opens `smoke.txt`, saves a unique marker through the IDE,
then visually recognizes the editor. An independent filesystem assertion checks
the saved marker. The test also verifies the Java package/JDT, read-only install,
user configuration in persistent home, HTTP/window/pixel startup, exact runtime
executable checksum and cleanup. The browser runs from the child's Playwright
component; the parent browser path is deliberately nonexistent. AI authentication
stays in the parent capsule.

Acceptance executable: source `f926036fd523e3e121aef9a9ca94dd93c1a3f0ba`.
Run `20261004T090121Z-ea0a5b` passed in 240 seconds: 18 browser actions, an
independent saved-marker check and final visual recognition. The implementing
agent also reviewed the final screenshot. The IDE's update notification was
rendered normally; no extra JDK or IDE feature was installed.

Executable SHA-256:
`5922fb5c944930e1e310bda3caf9517875ca566a394228c8dc7f75209eabeab3`.
Browser: child component Chromium `153.0.8010.12`. Both the initial and corrected
runs removed their test-owned containers, workspaces and checkout records;
cleanup was independently verified after the accepted run.

[Watch the original smoke movie](assets/2026-10-04-eclipse/first-session.webm).
It is a byte-identical copy of `eclipse/agent-desktop.webm`, with no trimming,
transcoding or speed adjustment. Chromium decoded it at 1600×1000, lasting
180.04 seconds; sampled frames were reviewed. The movie is 9,484,575 bytes, SHA-256
`00e665a13b890b68b39d2113b516a1bde0ac92caccc824eb57576483392278af`.

![Eclipse after saving the marker](assets/2026-10-04-eclipse/saved-edit.png)

Raw per-run logs remain under `devcapsule-src/dist/e2e-evidence/ide-smoke/`.
They may contain ephemeral desktop URLs and are not published.

## Findings resolved during implementation

- Initial run `20261004T084835Z-aa7fc5` saved and visually confirmed the marker,
  but manual screenshot review found a broken notification panel. The log named
  missing WebKitGTK. This run is diagnostic evidence, not final acceptance.
- Native libraries must be acquired before the networkless build. A direct apt
  build failed as expected; the final implementation pins and downloads packages
  before installing them offline.
- Copying each native package through separate build steps exceeded Docker's
  layer depth. One grouped package directory fixed this without changing the base.
- Corrected startup `20261004T085937Z-10bd26` passed. Screenshot review showed the
  rendered Java Developers Welcome page, with no broken browser panel.
- The Nox IDE smoke's local-build path omitted the selected executable variable.
  That handoff is fixed and covered by a regression test.

## Validation limits

This smoke establishes startup, rendering and an editor save. It does not claim
Java compilation/debugging, Maven/Gradle project builds, Marketplace installation,
or Eclipse workspace preference persistence across a restart. The existing
JetBrains-specific relaunch/font scenario is not enabled for Eclipse.

The initial full build gate passed. A later gate exposed an unrelated packaging
check that sees the checkout's editable `devcapsule.egg-info` before the metadata
inside the release test executable. The correct release wheel is present inside
the executable; the assertion runs in the wrong directory. Reproduction and a
minimal proposed test fix were delivered to maintenance as
`2026-10-04-component-catalog-packaging-metadata-shadow.md`. The final `nox -s build` passed: 1,150 tests, one existing xfail and xpass,
mypy, executable smokes, all nine packaging checks and the documentation
contract (`.git/eclipse-final-build.log`). The full gate also passed on the
complete delivery tree (`.git/eclipse-delivery-build.log`). All nine packaging checks also passed
from an isolated working directory (`.git/eclipse-isolated-packaging.log`).
The shadowing failure depends on leftover editable metadata; the successful
full rebuild had removed it. No unrelated product change was needed.
