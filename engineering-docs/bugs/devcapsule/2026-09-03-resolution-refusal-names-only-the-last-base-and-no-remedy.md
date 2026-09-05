# Bug: The Resolution Refusal Names Only The Last Base Tried And Offers No Remedy

Date opened: 2026-09-03

Status: **fixed 2026-09-05** on `component-catalog/antigravity-cli` at
the owner's direction, with one ruling sharpening the scope: *every*
refusal names `--unverified` — adopters must be able to try new
components and bases ahead of the matrix and report back. As
implemented: the refusal lists each base's gap on its own line, newest
first (replaying the symptom command now leads with "v0.2.9: no
verified pycharm version"); the remedy sentence names `--unverified`
and states the one thing it cannot bypass (a base that does not ship a
needed toolchain); and a refusal reached *with* `--unverified` already
passed says the flag cannot help instead of recommending it again.
Regression tests cover the newest-first ordering, the remedy line, and
the exhausted-flag wording. Closes on the owner seeing the new message
in practice. Originally reported by the product owner while spinning
the three-provider demo formations (v0.2.9 stretch, matrix
`embedded-11`)

Requirements: R-PRODUCT-001

Related: `2026-09-02-init-and-run-answers-not-persisted-as-authorizations.md`
(closed) — same family: the tool knows the way forward and does not put it
on the screen.

## Symptom

The owner asked init for a pycharm formation carrying all three agent
CLIs:

```bash
devcapsule-local.pex project init --need node --need python-ide \
  --need antigravity-agent --need claude-code-agent --need codex-agent \
  --authorize base-image devcapsule-local:v0.2.9 --regenerate
```

and was refused with:

```
devcapsule: No verified combination satisfies antigravity-agent,
claude-code-agent, codex-agent, node, python-ide on linux-amd64: no
verified antigravity-cli version against base v026 (substrate
ubuntu-24.04-gen1)
```

Two defects in one message:

1. **It reports the wrong (least useful) gap.** Resolution tried all
   three bases, newest first. v0.2.9 and v0.2.8 (gen2) failed because
   *pycharm* has no gen2 edge — the interesting gap, one owner smoke away
   from closing. v026 (gen1) failed because *antigravity* has no gen1
   edge. The message names only the v026 reason, pointing the user at the
   oldest base's problem and hiding that the newest base is one
   component short.
2. **It offers no path forward.** `--unverified` exists precisely for
   this situation (owner ruling 2026-09-03: strict first, then a gentle
   warning past the matrix on request) and resolves this exact need to
   v0.2.9 naming one unverified combination — but the refusal never
   mentions the flag. A user staring at this message has no remedy on
   the screen, against the house rule that refusals name the sanctioned
   lever.

The confusion is not hypothetical: the owner read the message as the
(just-removed) codex×pycharm coupling refusing the formation, when the
actual mechanism was per-component substrate edges.

## Mechanism (from code reading, revision `147d03b`)

`ResolutionMatrix.resolve` iterates `reversed(self._bases)` (newest
first) and overwrites a single `failure` string on every base that
fails; the final `ResolutionError` therefore always carries the
*oldest* base's failure. Nothing in the raise site appends the
`--unverified` remedy, and `_verified_selection`'s per-base reasons are
discarded except for the last one.

## Expected

A refusal that reports the failure per base (or at least the
newest/best base's gap) so the user sees which combination is closest
to resolving, and that names `--unverified` as the sanctioned way to
proceed past the matrix. In the spirit of the one-command contract:
the message should let the user fix their command without reading the
matrix source.

## Fix Scope

Message-only, self-contained in `resolve()`:

1. Accumulate the per-base failure reasons instead of overwriting one
   string, and render them newest-first (e.g. one line per base:
   `v0.2.9: no verified pycharm version (substrate ubuntu-24.04-gen2)`).
2. Append the remedy sentence naming `--unverified` (and what it does:
   gentle warning, unverified combinations recorded in the lock) when —
   and only when — the unverified fallback would in fact produce a
   formation; a need no base can satisfy (missing base capability)
   keeps its hard refusal.
3. Regression tests: a multi-base refusal message names every base's
   gap; the remedy line appears exactly when `allow_unverified=True`
   would succeed.

## Verification Target

Re-running the symptom command against the fixed client shows all
three bases' gaps and the `--unverified` remedy; adding the flag then
resolves to v0.2.9 with the pycharm combination named — no source
reading required.
