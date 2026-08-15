# Bug: Detached DevCapsule Containers Exit And Are Never Cleaned Up

Date opened: 2026-08-15

Status: open

Requirements: R-SCOPE-001, R-DOCKER-001, root R-PRODUCT-002

## Symptom

DevCapsule tells developers that closing the IDE ends the environment and
leaves nothing behind. The ordinary foreground launch honours that: it runs
`docker run --rm`, so the container is removed when the IDE exits.

The detached launch path does not. Its containers exit normally and then stay
on the host indefinitely as `Exited (0)` objects. Nothing reaps them, and no
command surfaces them to the developer. A developer who has used the detached
path accumulates stopped containers that they did not ask for and are not told
about, which is not the lifecycle the product promises.

## Evidence

Observed on the development host on 2026-08-15:

```
devcapsule-e2e-482c34f24fc5c438da7b24ff172a619b-successor  Exited (0) 15 hours ago
devcapsule-e2e-b2093d85912fa34ac1324e1da26a9dcd-successor  Exited (0) 2 days ago
```

Both were launched detached through
`devcapsule project recursive-e2e launch-successor`. Both exited on their own
when their IDE closed. Neither was removed, and both still hold their image
reference, name, and writable layer.

The foreground contrast is in `build_docker_args`: `ContainerLifecycle.foreground`
emits `--rm`, and `ContainerLifecycle.detached` emits `--detach` with no
removal policy and no later reaping.

## Why This Is Not Simply The Retention Policy

Recursive-dogfood Stage 6 deliberately retains a successful successor so
Stage 7 can prove persistence, and deliberately retains failed runs as
diagnostic evidence. That retention is correct and must not be removed
blindly.

The defect is that retention is **indefinite, invisible, and unowned**:

- nothing distinguishes a container retained on purpose from one merely left
  behind after a normal exit;
- no command lists what DevCapsule is currently keeping, so a developer cannot
  discover the objects without knowing Docker;
- there is no expiry, no reaping, and no prompt; and
- the same silence applies to the run-owned staging directories and workspaces
  those containers reference.

The two containers above are labelled `devcapsule.e2e.*`, so exact,
ownership-checked cleanup is already possible. The information needed to do
this safely exists; nothing acts on it.

## Expected Behaviour

- A detached container that has exited is either removed, or retained under an
  explicit, recorded reason with an owner.
- A public command lists every container, staging directory, and workspace
  DevCapsule is currently retaining, together with why.
- A public command removes exactly those objects, selecting them by recorded
  identity and ownership labels rather than by name prefix.
- Cleanup never selects a container DevCapsule does not own, and never removes
  a run still recorded as retained evidence.
- The promise made to developers about environment lifecycle matches what the
  detached path actually does, or the documentation states the difference.

## Notes

The V1 backlog item *Owned Workspace And Manifest* already requires proving
that cleanup and repair affect only the exact ownership-marked run. This bug is
the user-visible consequence of that work being outstanding, and should be
closed by the same slice rather than separately.

Stage 7 of the recursive dogfood milestone is the natural home for the
implementation, since it already owns persistence and deterministic cleanup.
Until then, do not remove the two containers above: they are the retained
Stage 6 and Stage 7 evidence.
