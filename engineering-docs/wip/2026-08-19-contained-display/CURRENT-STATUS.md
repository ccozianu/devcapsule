# Workstream Current Status: Contained Display

Mnemonic: `contained-display`

Start date: 2026-08-19

State: active; stage 1 (supervisor core) implemented and verified 2026-08-30

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

**Stage 1 is implemented and verified** (2026-08-30, commits `500909d` and
`a3036ec` on this branch), exactly per the owner-reviewed
[design note](supervisor-core-design.md):

- `devcapsule/container_runtime/supervisor.py` is the pure-Python PID 1
  (D1): SIGCHLD-driven reaping including adopted orphans, SIGTERM/SIGINT
  forwarding, TERM-grace-KILL shutdown in reverse start order (5 s grace,
  deliberately below `docker stop`'s 10 s), honest exit codes — the
  foreground child's own code, 128+signal for signal deaths, and
  EX_SOFTWARE (70) naming the dead child when a non-foreground child dies
  first. The machinery runs over an ordered child set; exactly one
  foreground child is exposed (D2 as restaged).
- The entrypoint supervises instead of exec-ing; the base-image ENTRYPOINT
  dropped `tini` (recorded fallback, still installed) so the supervisor
  really is PID 1, and the formation descriptor's entrypoint contract
  followed, so materialization identities roll over.
- **Headless mode** is the same distinguished slot with no GUI:
  `devcapsule runtime RUNTIME_PLAN.json -- COMMAND...` runs the job in the
  project directory and propagates its exit code — the decided
  non-interactive-runs mechanism. The runtime plan schema is unchanged.
- The supervisor asks nothing and announces on stderr (D8).
- Evidence: fake-children unit tests (`tests/test_supervisor.py`, driven
  in a dedicated process because the supervisor owns its thread's signal
  mask) cover exit propagation, signal deaths, the explicit end, an
  ignore-TERM straggler, and infrastructure-death failure; the runtime
  image e2e asserts the supervisor is PID 1 with the IDE as its child, the
  headless exit-code propagation with no zombies after an orphan reap, and
  `docker stop` → graceful end with exit code 143; the recursive successor
  probe now asserts the supervised process tree too. Unit suite 442
  passed; mypy clean; `nox -s e2e` green except the contributor-bootstrap
  test, blocked by pre-existing local checkout state (see *Open Threads*).

The cheap rider landed: the launcher no longer advises
`xhost +SI:localuser:<user>`; it states the passthrough exposure instead.

**The next task is the display-transport spike** described under *Next
Resumable Task*.

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

## Open Threads

- **All suites are green on this branch** (checkout cleaned by the owner
  2026-08-30): unit + mypy, `nox -s e2e` including contributor bootstrap,
  and `nox -s recursive_dogfood_e2e` (dry-run stage plus the clean-clone
  protocol). The supervised process tree is proven live in the
  runtime-image e2e, which builds a base from the current PEX.
- **The live successor proof landed** (2026-08-30, after the owner pointed
  at the command-line override path): a base was built from this source
  (`devcapsule images build --type base --pex dist/devcapsule-local.pex
  --allow-local-source --network host`, tagged
  `devcapsule-base:supervisor-stage1`) and authorized for this checkout
  (`project config authorize base-image …`, plus the recommended
  `claude-code-download true`, both developer-owned checkout state). A
  successor capsule launched from it reached **stage-6
  inspection-passed** — PID 1 is the supervisor and PyCharm's `java` is
  its direct child under host X11 — and `docker stop` ended the real IDE
  session gracefully with exit 143 and the supervisor's announce in the
  logs. Commit `c34ea1f` fixed the probe on the way: the PEX scie
  re-execs through its unpacked interpreter, so PID 1 must be asserted by
  its runtime invocation signature, not the `/opt` pex path.
- Two live observations worth carrying into the display stage: the first
  successor exited cleanly after ~45 s, most plausibly JetBrains
  single-instance activation against the concurrently running dogfood
  IDE sharing `/ide-config` on host network (the supervisor propagated
  the clean exit honestly; a second launch stayed up); and the fabricated
  retained-run workspace used to drive stage 5/6 by hand was removed
  after the proof — the protocol still has no CLI that creates a fresh
  pre-launch retained run.
- The published base still predates the supervisor; publishing a
  post-`500909d` base remains a release step the owner drives.
- The D7 pre-recorded authorization/acquisition-acknowledgement design
  note is still to be written; headless *mechanics* landed with stage 1,
  the unattended-answers shape did not (it is plan-validation work).
- The reaping-semantics coordination owed to `project-management`'s
  backlog entry is now concrete: the supervisor makes the exit honest
  (internal cleanliness, truthful exit code); container removal stays
  host-side launcher policy. That division should be delivered to close
  the entry.
- Implementation subtlety worth keeping: the supervisor must hold its
  children's `Popen` objects for the whole session — a collected `Popen`
  reaps its zombie behind the supervisor's back and the exit is never
  attributed. Recorded as a comment at the spawn site.

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
