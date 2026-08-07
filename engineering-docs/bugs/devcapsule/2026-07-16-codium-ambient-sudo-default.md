# Bug: Codium Grants Ambient Passwordless Sudo By Default

Date opened: 2026-07-16

Status: open; diagnosed and evidenced, no fix implemented

Requirements: R-SCOPE-001, R-DOCKER-001, R-FRAMEWORK-001, root R-PRODUCT-002

## Symptom

Every `devcapsule codium_with_claude run` session gives the mapped IDE user
unconditional passwordless root inside the container. The user never asks for
it, no option controls it, and no user-facing document mentions it.

The equivalent PyCharm capability is opt-in behind `--dev-sudo` / `--sudo`, and
the PyCharm default profile actively drops capabilities instead.

## Environment

- Image: `codium-with-claude:latest`
- Launcher: `devcapsule codium_with_claude run`
- Entrypoint: `devcapsule-src/devcapsule/assets/codium_with_claude/entrypoint.sh`
- Launcher module: `devcapsule-src/devcapsule/configurations/codium_with_claude/_launcher.py`

## Evidence

`devcapsule-src/devcapsule/assets/codium_with_claude/entrypoint.sh` wrote the sudoers rule
unconditionally, on every launch:

```bash
printf '%s ALL=(ALL) NOPASSWD:ALL\n' "${user_name}" > /etc/sudoers.d/devcapsule-developer
chmod 0440 /etc/sudoers.d/devcapsule-developer
```

`build_codium_run_command` emitted no counterbalancing isolation arguments. The
default Codium `docker run` plan contained no `--cap-drop`, no
`--security-opt no-new-privileges`, and no `--read-only`.

By comparison, `_launcher.py` for PyCharm applies, for the non-sudo default:

```python
args.extend(["--cap-drop", "ALL", "--security-opt", "no-new-privileges"])
```

and adds `--read-only` unless `--writable-root` or Docker-in-Docker is active.

A repository-wide search on 2026-07-16 found no user-facing documentation of
Codium sudo. The only sudo references were the parity bug record's own list of
options Codium was missing, which framed sudo as an absent capability rather
than an ambient default.

## Expected Behavior

Codium's default profile should carry no ambient privilege escalation. Sudo,
writable root, and native-debug capabilities should each be explicit, opted
into per launch, documented beside the option, and consistent with the PyCharm
security model.

## Actual Behavior

Sudo was always on, capabilities were never dropped, `no-new-privileges` was
never set, and the container root filesystem was always writable.

## Root Cause

The Codium proof point was built to reach a working GUI quickly. The entrypoint
took the shortest path to a usable development container and no isolation
profile was ever layered back on. The parity bug recorded the missing
*options*, but nobody noticed the underlying *default* was the relaxed one.

## Proposed Fix Direction

Not implemented. No code has been written for this bug. The following is a
sketch for whoever picks the work up, not a record of work done.

This bug overlaps the shared-runtime work in
`2026-07-13-codium-run-option-parity.md`, whose item 4 covers development and
isolation profiles. It should probably be fixed through that shared model
rather than by patching the Codium launcher alone.

- Consider an IDE-neutral isolation model in `devcapsule-src/devcapsule/runtime.py` covering
  `dev_sudo`, `writable_root`, and `debug_native`.
- `--dev-sudo` implying a writable root would match accepted PyCharm semantics.
- The Codium entrypoint would write the sudoers rule only when an explicit
  environment flag is set by the launcher.
- The default Codium plan would need `--cap-drop ALL`,
  `--security-opt no-new-privileges`, and `--read-only`. Whether the current
  image and VSCodium tolerate a read-only root is unverified and is the main
  open risk. PyCharm pairs `--read-only` with `--tmpfs` mounts for `/tmp`,
  `/run`, and `/var/tmp`; Codium likely needs an equivalent, and Electron may
  need more.
- Enabling sudo should print an explicit warning to stderr, as PyCharm does.

Whether PyCharm adopts the shared model in the same change is an open decision.
It was manually validated on 2026-07-12, so there is a regression risk in
touching it.

## Verification Target

None of the following has been performed.

1. Automated: assert the default Codium plan has no sudo, and does have
   `--cap-drop ALL`, `no-new-privileges`, and `--read-only`.
2. Automated: assert `--dev-sudo` implies a writable root and drops
   `--read-only`.
3. Automated: assert the entrypoint gates the sudoers rule on the explicit
   launcher flag.
4. Manual: rebuild the Codium image, confirm the default session cannot sudo,
   confirm VSCodium and Claude Code still work under a read-only root, and
   confirm `--dev-sudo` restores package installation.

## Close Criteria

Close when a default Codium session is unprivileged and still fully usable,
`--dev-sudo` remains a working development profile, the automated checks above
pass, and the manual host validation in item 4 confirms the result.

## Reopen If

A later image, entrypoint, or launcher change reintroduces privilege
escalation, writable root, or added capabilities into the default profile
without an explicit option and matching documentation.
