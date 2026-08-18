# V2 Task: Recover Per-Run Resources After Launcher Loss

Status: deferred to V2 by the product owner on 2026-08-18

Release target: V2

## Problem

`devcapsule.pex` may launch a DevCapsule from the host OS or, less commonly,
from inside another DevCapsule. It normally cleans the temporary resources it
creates for the launched container. A crash, `SIGKILL`, host restart, or other
abnormal termination can prevent that launcher process from reaching its
cleanup path.

Recursive detached launch also demonstrates the more general lifecycle rule:
the process that creates a container can exit normally before the container's
resources should be removed. DevCapsule owns those resources, but their
lifetime cannot be represented solely by the lifetime of one launcher process.

V1 does not need a recovery service or reconciliation mechanism for this. The
current launcher allocates few, low-impact transient resources, and an
occasional leftover after a launcher crash does not justify the additional
product and operational complexity.

## V2 Task

Provide an idempotent recovery operation for exclusive per-run resources after
the original launcher is no longer available. It must:

- accept the random run ID and derive exact resource names and containing paths
  from it rather than accepting arbitrary cleanup targets;
- work from the host or from an authorized DevCapsule connected to the same
  Docker daemon;
- retain support resources while the corresponding GUID-named container is
  still active;
- remove abandoned transient files, sockets, containers, and any future
  exclusive per-run resources after the applicable container-lifecycle policy
  permits removal;
- be safe to repeat and safe after partial cleanup;
- leave persistent developer state, shared images, build cache, credentials,
  and resources belonging to every other run untouched; and
- define how a later DevCapsule invocation finds or is given unfinished run
  IDs without treating the IDs as secrets or weakening Docker authorization.

A permanent background service is not assumed. V2 may choose an explicit
`cleanup`/`reconcile` command, recovery during a later launch, a bounded reaper,
or a combination after evaluating the user experience and operational cost.

## Acceptance Direction

An automated recovery test should launch a child from a disposable launcher,
terminate the launcher without its normal cleanup path, and prove that:

1. an active child and its required support resources are preserved;
2. reconciliation can later remove only that run's abandoned transient
   resources using its run ID;
3. a repeated reconciliation succeeds without damage; and
4. unrelated decoy resources remain unchanged.

This task does not reopen recursive-dogfood Stage 6 or add a V1 closure
condition. Normal-path cleanup and deterministic cleanup for the active E2E
scenario remain separate from recovery after launcher loss.
