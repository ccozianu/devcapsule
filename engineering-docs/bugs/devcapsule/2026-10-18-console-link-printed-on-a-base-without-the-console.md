---
status: confirmed
severity: minor
target: 0.3.0
owner: maintenance
opened: 2026-10-18
requirements: [R-PRODUCT-001]
---

# The launcher prints a web console link on a base that has no web console

## Symptom

Found by the owner on 2026-10-18, first launch of the downloaded
`v0.3.0-rc0` on the second DevCapsule checkout. The launcher prints the
console link, then the capsule says there is no console:

```text
Web console: http://127.0.0.1:50153/?token=3d5c…
  (the capsule as a page; the link works for this run only)
devcapsule console: this base has no web console (base recipe 10 adds it at /opt/devcapsule-webconsole); the capsule runs without one
Picked up JAVA_TOOL_OPTIONS: -Dide.browser.jcef.sandbox.enable=false
```

A user who opens the link gets nothing, and the two lines contradict each
other. The third line is JVM noise from IntelliJ's launch, unrelated, and
belongs to the first-session summary work, C10.

Three minutes later, the launcher, still waiting for the console it was
told does not exist, adds:

```text
Web console did not answer on port 50153 within 180s; if the capsule is still starting, open it yourself: http://127.0.0.1:50153/?token=3d5c…
```

The user has by then read that the base has no console; the advice to open
it is wrong, and the wait was for nothing.

## Cause, from the code

The launcher allocates the console port for every run and prints the
link whenever `config.console_host_port` is set
(`devcapsule/launch/pycharm/_launcher.py`, the block after the contained
display link). Whether the base carries the console is decided only
inside the capsule, when the runtime looks for `/opt/devcapsule-webconsole`
(`devcapsule/container_runtime/console.py`), and on a base before
recipe 10 it prints the notice and runs without one. The matrix's pinned
published base is `ubuntu-24.04@9`, the v0.2.12-rc5 build, so every
project that resolves to the published base, this one included, sees
both lines. A published base of recipe 11 is a gate before the final tag
for exactly this reason; until it exists, every candidate shows the
contradiction, and after it exists older checkouts pinned to a recipe-9
base still would.

After printing the link, the launcher hands the console's port to the
readiness watcher it shares with the contained display
(`devcapsule/display_client.py`), which polls the port for 180 s and then
prints the "did not answer" line with the same link. The watcher has no
way to learn what the runtime found; the runtime's notice goes to the
capsule's output, not back to the launcher.

The launcher can know before it prints: the base's recipe version is the
image label `devcapsule.base.recipe-version`, read by
`devcapsule/images/contract.py` and shown by `images list`, and the lock
names the base.

## Expected behaviour

One true statement, before the capsule starts. On a base of recipe 10 or
later, the console link as today. On an earlier base, no link, and one
line in its place: that this base has no web console, which recipe adds
it, and how to get one, the published base when it exists or
`images build`. No port is bound, no token is minted and no readiness
watcher is started for a console that cannot answer, so the three-minute
wait and its "open it yourself" advice do not happen either. The runtime's
notice stays as the backstop for a base the launcher could not inspect,
and when that backstop fires the watcher's timeout line must not
contradict it: if the launcher cannot decide beforehand, the runtime's
finding has to reach it, or the timeout line has to say that the base may
lack the console.

## Verification target

A candidate of 0.3.0: launch a project pinned to the recipe-9 published
base and read the launcher's output; launch one on a recipe-11 base and
open the link. Both in the fresh-workspace end-to-end form the e2e rules
require.

## Close criteria

- The launcher prints the link only when the base's recipe carries the
  console, and the substitute line otherwise, with a unit test for each;
  no readiness wait and no timeout line on a base without the console.
- The owner's transcript above no longer reproduces on a downloaded
  candidate.
- The web console page in `docs/sessions/` describes the substitute line.
