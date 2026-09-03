# Bug: `init --authorize base-image` Left The Checkout Unauthorized

Date opened: 2026-09-01

Status: **closed 2026-09-03** — validated by the owner across the v0.2.9
smokes: the 2026-09-02 tictactoe smoke, the 2026-09-03 five-way smoke, and
the same-day hands-on check of base selection at init with the v0.2.9 CLI
("thoroughly as expected and no trace of previous behavior"). The
`--authorize base-image` carrier path itself was subsequently reworked
into an informed-consent base *selection* — see the closures of
`2026-09-02-authorize-base-image-conflates-consent-with-selection.md` and
`2026-09-02-init-and-run-answers-not-persisted-as-authorizations.md`.
Fix implemented 2026-09-01.

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

## Fix (2026-09-01)

The owner moved the fix ahead of the smoke and additionally reported that
after a successful init a manual `config resolve` was needed before
`project run` — contradicting init's stated postcondition ("a fresh
resolution stands; 'devcapsule project run' starts it").

Implemented, keeping init non-idempotent over authored artifacts:

- A repeated `init` over a **fully initialized, fresh** checkout that
  carries `--authorize`/`--set`/`--bind` answers now **applies them** to
  the standing checkout through the same primitives the config family
  uses, then refreshes the resolution — so re-pasting the intended full
  command self-heals, and `project run` works immediately afterward. A
  repeat carrying **no** answers still refuses loudly naming
  `--regenerate` and the config family.
- Partial and stale states were already init's repair job and remain so;
  the owner's recovery flow (`rm -rf` of the checkout's config directory,
  then the identical init) is now covered by a regression test, alongside
  repeated-init-with-answers, repeat-without-answers-still-refuses, and
  an init-then-run test that asserts no `config resolve` is needed in
  between.

The exact sequence that produced the original silent "none" remains
unreproduced (all single-invocation paths were verified loud); with the
repair path in place, every suspected sequence now converges to a correct
state by re-running the intended command.
