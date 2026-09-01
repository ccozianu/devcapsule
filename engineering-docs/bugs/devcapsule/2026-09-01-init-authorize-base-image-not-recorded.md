# Bug: `init --authorize base-image` Left The Checkout Unauthorized

Date opened: 2026-09-01

Status: open; reported by the product owner during the tictactoe codium
smoke; fix scheduled after the smoke completes

Requirements: R-PRODUCT-001

## Symptom

Initializing the tictactoe sample copy with the full non-interactive
command:

```bash
devcapsule project --path . init \
  --need node --need frontend-ide \
  --slug tictactoe-5inrow \
  --creator mailto:ccozianu@gmail.com \
  --project-mount /workspace/tictactoe-5inrow \
  --authorize base-image "docker.io/mycodespaceai/devcapsule-base@sha256:695f9eb6dd269dc694b3367f6a2570d500b938998d6f7aa3aa00e5d04cc7394a"
```

did not record the base-image authorization: a subsequent
`devcapsule project config list` showed **none** for `base-image`.

Context that may matter: the same terminal session had just suffered a
copy-paste line-split failure (`--name: command not found` — the shell ran
a continuation line as its own command), and the command was retried in
variations, so the failing sequence likely involved a partial or repeated
`init` rather than a single clean invocation.

## What Reproduction Established (2026-09-01, revision `7e1e857`)

The single-invocation paths are all correct and loud:

- A clean non-interactive `init` with the identical `--authorize
  base-image <reference>` carrier **works**: it prints `Authorized for
  this checkout: base-image.` and `config list` shows `authorized` with
  the reference.
- Re-running the same full `init` over the completed checkout refuses
  loudly (`already fully initialized … --regenerate`), without touching
  authorizations.
- A wrong or truncated reference fails validation loudly
  (`accepts yes, no, or the exact value …`).

So the reported silent outcome is sequence-dependent and not yet
reproduced. The owner's exact terminal transcript would settle which
sequence produced it.

## Suspected Product Gaps (worth fixing regardless of exact sequence)

1. **No idempotent authorize-repair through `init`.** Once a first
   (possibly flag-starved, paste-split) `init` completes, re-running the
   full intended command refuses outright instead of applying the
   authorization carriers it carries; the remedy silently shifts to
   `config authorize` + `config resolve`. A user retrying their intended
   command should either have its authorizations applied or be told
   explicitly that the `--authorize` flags were ignored and what to run
   instead — the current refusal message does not mention them.
2. **A flag that never reached the process is indistinguishable from a
   recorded one.** When the shell splits a paste, `init` runs with fewer
   flags than the user believes; the only tell is the *absence* of the
   `Authorized for this checkout: …` line. The init report could state
   authorization outcomes explicitly (including "base-image: not
   authorized; run 'config authorize …'") so a missing carrier is visible
   rather than silent.

## Immediate Workaround

```bash
devcapsule project --path . config authorize base-image "<locked reference>"
devcapsule project --path . config resolve
```

## Fix Scope

Scheduled after the tictactoe smoke. Decide and implement: make repeated
`init` apply authorization carriers to the standing checkout (or name
their being ignored in the refusal), and make the init report enumerate
authorization outcomes explicitly. Add regression tests for the repeated
and partial-init sequences alongside the existing single-invocation
coverage.
