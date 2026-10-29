# Product gap: a scratch directory in the capsule contract, with a persistent option

Date: 2026-10-22
From: maintenance
To: project-management

## Handoff

The owner found a product gap on 2026-10-22 and asked that it be filed
with project-management for planning: a capsule has no scratch directory
that the launcher provides. Whatever large temporary work a developer, a
test suite or an agent needs goes to `/tmp`, a 2 GB tmpfs, or to a
directory made by hand on the container's overlay filesystem, which dies
with the container. The owner's words: scratch should not need to be
created over Docker's overlay; the developer of DevCapsule should mount
external directories for such things. And: it may be scratch, but it must
have an option to be persistent scratch.

This item carries no priority and no release target; both are yours. It
is not a 0.3.0 request.

## The motivating case

This repository's gate writes its test scratch under
`/opt/devcapsule-gate/pytest`, as *Validation Commands* in
`WORKFLOW-LOCAL.md` says, because the gate overflows `/tmp`. The
directory lives on the overlay. After the capsule's restart under rc1 on
2026-10-21 it was gone, and the first test run failed at setup in every
test that takes a temporary directory, until the agent recreated it. The
instructions name a directory that nothing creates and nothing keeps.

## What the contract should say, as the owner sees it

- The launcher provides a scratch directory inside every capsule, backed
  by a host directory, not by the overlay. It is listed by `project info`
  under persistence beside the others, with its path, its backing and its
  lifecycle, and reaches the capsule's environment by a name, as
  `DEVCAPSULE_LOG_DIR` does for the logs.
- Two lifecycles, chosen per checkout: **ephemeral** scratch, cleared when
  the container is removed or at each launch; and **persistent** scratch,
  surviving container replacement like the `cache` kind, so that a gate's
  scratch, a build cache or a downloaded corpus does not have to be made
  again. The persistent option is the owner's explicit requirement.
- A budget or a cleanup command for the persistent form belongs to the
  same design as the log budget and the image-cleanup slice; the launch
  context's `temporary` list, `/tmp`, `/run`, `/var/tmp`, `/dev/shm`,
  stays as it is.
- Once it exists, this repository's *Validation Commands* point the gate's
  scratch there, and the hand-made directory under `/opt` goes.

Schema names, the default lifecycle, the path inside the capsule and the
host location are design choices for the implementing workstream with the
owner, not settled here.

## Evidence

- The launch context of this capsule, `/etc/devcapsule/launch-context.json`,
  lists the persistence mounts and marks `/tmp`, `/run`, `/var/tmp` and
  `/dev/shm` as lost when the container is removed; nothing is listed for
  scratch.
- The maintenance status file, entry of 2026-10-22, and the memory note
  `gate-scratch-on-overlay` the agent kept for the workaround.
- `WORKFLOW-LOCAL.md`, *Validation Commands*, the `/tmp` remark.

## What accepting this means

Project-management records the gap and sequences it; the implementing
workstream and the target are its to choose. Nothing is asked of
maintenance beyond updating *Validation Commands* when the mount exists.
