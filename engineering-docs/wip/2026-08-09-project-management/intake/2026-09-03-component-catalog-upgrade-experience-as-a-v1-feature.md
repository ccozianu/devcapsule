# Intake: The Upgrade Experience Is A V1 Feature

Delivered 2026-09-03 by `component-catalog`, at the product owner's
direction, given during the v0.2.9 validation session: "we need to
flush out upgrade-friendly messages and warning of obsolescence as
well as the project of upgrading. It's an important feature for v1."

## What Is Being Handed Over

Design and ownership of the developer-facing upgrade story, three
strands the owner named:

1. **Upgrade-friendly messages**: when a newer pinned component, base,
   or matrix exists, the tool should say so helpfully — today the only
   voice is a refusal after the fact.
2. **Obsolescence warnings**: a checkout whose lock, base, or
   components have fallen behind should learn it gently and early, not
   discover it as a hard error at the next `--regenerate`.
3. **The project of upgrading**: the process and tooling by which pins
   advance — who verifies, what evidence gates the advance, how
   adopters are moved along, and what happens to superseded artifacts.

## Why It Belongs To `project-management`

The owner's earlier statement of the narrower "component update
mechanism" (2026-08-31, recorded in the `component-catalog` handoff's
open threads) already assigned it to project-wide planning:
advancing pins spans the resolution matrix, the CLI's message surface,
the release process, and every workstream that owns a component. The
broader feature the owner has now named subsumes it and crosses the
same boundaries; `component-catalog` can host the matrix data changes
but cannot own the product surface.

## Evidence

The 2026-09-02/03 v0.2.9 validation stretch is a complete case study,
recorded in the `component-catalog` handoff and bug records:

- A checkout whose lock predated the current matrix failed loudly
  ("unsupported recipe … expects …") with `--regenerate` as the only
  remedy — correct, but the obsolescence was knowable long before the
  refusal.
- The matrix advanced five times in two days (`embedded-4` →
  `embedded-9`), each advance hand-edited; the sustainability of that
  is already a recorded backlog item in the `component-catalog`
  handoff (resolution-matrix cleanup), and the update *process* is the
  missing other half.
- The claude-code pin advance to 2.1.236 (Fable 5.1) worked and the
  owner confirmed it, but it was performed entirely by hand: discover
  the stable version, download, checksum against the vendor manifest,
  edit the pin, re-verify edges provisionally. Every future component
  release implies the same manual round.
- Superseded multi-GB canonical images accumulate with no lifecycle
  (the 2026-09-02 formation-identity bug record) — the disposal half
  of upgrading.
- `init --unverified` (owner-ruled 2026-09-03) now lets a sophisticated
  user run ahead of the matrix with a gentle warning; the upgrade
  story is its complement — moving the matrix itself forward so the
  escape hatch stays rare.

## What Accepting Would Mean

Owning the feature's shape for V1: where upgrade/obsolescence messages
surface (init, run, config list, a dedicated verb), what the pin-advance
process is (evidence gates, provisional edges, who smokes), and how
superseded artifacts age out. The owner has stated it is an important
V1 feature; sequencing against the rest of V1 is the receiving
workstream's judgment, per protocol.
