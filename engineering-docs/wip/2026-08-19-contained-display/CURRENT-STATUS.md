# Workstream Current Status: Contained Display

Mnemonic: `contained-display`

Start date: 2026-08-19

State: active; first session 2026-08-30

Integration target: `main`

Delivery method: pull request

Requirements: `R-SCOPE-001`, `R-PRODUCT-002`, `R-DOCKER-001`

## Goal

Own the capsule supervisor core and the capsule's own display environment, as
one sequenced effort: the supervisor as the container's entry process and
lifecycle anchor first, then the contained display as its first consumer,
closing the host-session credential exposure and the desktop-integration gap
that shares its root cause.

The goal was widened from display-only on 2026-08-30, when the product owner
assigned the supervisor core here (see *Intake Dispositions* below). The
original display scope — transport decision, interim mitigation, clipboard
policy, regression test — is unchanged inside the widened goal.

## Why This Workstream Exists

Opened by `project-management` on 2026-08-19 at the product owner's direction,
to own the [V1 scope ledger](../2026-08-09-project-management/v1-scope-ledger.md)
row *Contained Display And Desktop Integration*. On 2026-08-30 the owner
assigned it the *Capsule Supervisor And Multi-IDE Sessions* row's V1 core as
well: the display is a process tree (X server, window manager, noVNC bridge,
IDE) that the current exec-the-IDE container model cannot host, so building
the display first would force a throwaway process manager. The supervisor is
that manager, built once, transport-agnostic.

It is named for its subject rather than for a release deliberately.

## Branch Association

`contained-display/supervisor-core`, forked 2026-08-30 from `main` at
`3017381` — the first branch of this workstream, created after the
registration and the supervisor assignment both reached `main` through
PR #46.

## Scope

In scope:

- **the supervisor core, V1 cut**: PID-1 duties (signal forwarding, child
  reaping), a declarative child list, an explicit session end, and a headless
  mode with no GUI children — the decided mechanism for non-interactive runs.
  The desktop-integration layer (tray, one-click secondary IDEs, multi-IDE
  sessions) is post-V1 and **not** in scope;
- the display transport decision, currently `proposed` pending a spike,
  between a contained VNC or noVNC session and Xpra seamless mode;
- an interim mitigation for the window before that transport ships, during
  which real projects containing agents run on X11 passthrough;
- clipboard policy and its declaration in the runtime plan and inspection
  output;
- the regression test that proves the capsule cannot reach the host session;
  and
- the design of pre-recorded authorization and acquisition acknowledgements
  for unattended (headless) runs, which rides the supervisor per the
  assignment.

Not in scope: the `xdg-open`/`BROWSER` forwarding shim (shipped under
`recursive-e2e`), and the post-V1 desktop layer.

## Current Task

**Design and implement the supervisor core**, per the owner's supervisor-first
direction: a design note settling process model, child declaration, session
end, signal/exit semantics, and the headless mode; then the implementation
under the existing configuration contracts, validated under host X11 (the
supervisor is transport-agnostic and must not wait for the display).

Two early, cheap items ride alongside rather than waiting:

1. **The launcher's `xhost +SI:localuser:<user>` advice** — the 2026-08-19
   design input's "cheaper floor". The launcher currently recommends the most
   dangerous available action; removing that advice and stating the exposure
   is a one-line-scale product change with immediate safety value.
2. **The Xephyr tire-kick** (interim mitigation candidate): no base-image
   change, doubles as the first half of the transport spike. It has a clock —
   the owner's real projects run agents on the trusted-cookie transport today.

## Next Resumable Task

After the supervisor core runs children under host X11: the interim
mitigation decision (Xephyr nested server versus documented exposure), then
the transport spike (contained VNC/noVNC versus Xpra seamless) with its
children supervised, then the ratification gate — a full day of ordinary
development inside the result. Aesthetics that hold at hour six are the
relevant test.

## Intake Dispositions

Recorded 2026-08-30, first session; reasoning here, one-line entries in the
[disposition log](intake-dispositions.md), files removed per the queue rule.

- **`2026-08-30-project-management-supervisor-core-assigned.md` — accepted.**
  The assignment, its scope cut, and what rides on it (non-interactive-runs
  design, reaping-semantics coordination, the display ratification test
  validating both) are folded into *Goal*, *Scope*, and *Current Task* above.
- **`2026-08-19-project-management-display-transport-design-input.md` —
  accepted as design input.** Its three contributions are adopted as working
  assumptions pending the spike: choose the transport on keylogging and
  injection grounds with clipboard as an independent dial; the Xephyr nested
  server enters the interim-mitigation candidates (with its stated costs);
  clipboard policy is asymmetric — automatic out, explicit in — declared in
  the runtime plan, with text-only reframed as a control. Its bug-closure
  bar is adopted verbatim: the bug closes on a permanent regression test
  (XTEST injection, root-window capture, keymap polling, host clipboard read
  all fail from inside the capsule), not on the transport landing. Its
  maturity table carries a currency caveat and is re-verified before
  commitment.

## External State And Risks

- The [X11 session-credential bug](../../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md)
  is open and is this workstream's subject; the owner's real projects run on
  the exposed transport until the interim mitigation or the display lands.
- `WORKFLOW.md` is frozen until a release candidate (2026-08-30 ruling);
  this workstream's work is product code and documents, unaffected.
- The supervisor revises the reaping semantics recorded in
  `project-management`'s coordination backlog; coordinate before that entry
  closes. The `codium-surface` scope (unowned) is decided to shape inside
  the supervisor model and may consult this work.
- The transport choice interacts with the proposed WSL2 work, the
  sample-project port and networking items, and the JCEF preview bug; the
  ledger row records how.

## Workstream Document Index

None yet; the supervisor design note is the first planned document.
