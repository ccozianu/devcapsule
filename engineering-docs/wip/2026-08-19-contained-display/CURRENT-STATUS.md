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

**Implement the supervisor core, stage 1**, per the completed and
owner-reviewed [design note](supervisor-core-design.md) — the design review
concluded 2026-08-30 with every decision point D1–D9 ruled or carrying a
ratified recommendation. Stage-1 scope, exactly:

- a pure-Python PID 1 in `devcapsule_runtime` (D1): reap, signal-forward,
  TERM-grace-KILL shutdown, honest exit codes;
- **one distinguished foreground child** (D2 as restaged): the IDE, or the
  headless job — the runtime plan schema is unchanged, today's launch
  command is the declaration, no migration;
- session ends on child exit or `docker stop`/SIGTERM (D3/D4), exit code
  propagated; headless mode is the same slot with no GUI (the decided
  non-interactive-runs mechanism);
- the supervisor asks nothing and displays via stdout/logs (D8, decided);
- internal machinery written over a set of children, exposing exactly one;
- fake-children unit tests for the state machine, plus the e2e assertion
  that the supervisor is PID 1 with the IDE as its child, under host X11.

One cheap item rides alongside: removing the launcher's
`xhost +SI:localuser:<user>` advice and stating the exposure instead — the
2026-08-19 design input's "cheaper floor", immediate safety value.

**Transport rulings from the review, superseding the scope bullets above
where they differ** (the design note is authoritative): V1 offers the
contained desktop (Xvnc + noVNC, native viewer optional); native-window
modes (Xephyr/Xpra) are a recorded stretch, Xephyr presumptive; X11
passthrough is retained behind an explicit authorization node with the
trade-off stated, the grant in the run manifest, and the regression test
recorded as waived by authorization. The Xephyr interim tire-kick is no
longer a scheduled item — dogfood continues on passthrough, unoffered,
until the contained desktop lands.

## Next Resumable Task

After stage 1 is implemented and verified: the display-transport spike —
Xvnc plus noVNC as supervised infrastructure children (product-derived,
not user-declared), the per-run loopback token, the clipboard bridge
implementing the asymmetric policy — then the ratification gate, a full
day of ordinary development inside the result. Aesthetics that hold at
hour six are the relevant test. The multi-foreground-child configuration
language is a separate design exercise after the supervisor proves itself,
per the D2 restaging.

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

- [Supervisor core design note](supervisor-core-design.md) — D1–D9, all
  reviewed with the product owner 2026-08-30; the authoritative record of
  the supervisor scope, the transport lineup (contained desktop offered,
  native-window stretch, passthrough by authorization), and the D2
  restaging to one distinguished foreground child.
