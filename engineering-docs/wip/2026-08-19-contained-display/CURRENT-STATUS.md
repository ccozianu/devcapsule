# Workstream Current Status: Contained Display

Mnemonic: `contained-display`

Start date: 2026-08-19

State: active; resumed 2026-09-12 at the product owner's direction for the
display-transport spike (stage 2). Stage 1 is merged on `main`. The contained
display is implemented on `contained-display/display-transport` with unit,
type and runtime-image e2e evidence; awaiting PR delivery, a published
recipe-8 base, and the owner's ratification day. See *Resume And Current Task*.

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

`contained-display/display-transport`, forked 2026-09-12 from `main` at
`a27e0ed` for stage 2. The stage-1 branch `contained-display/supervisor-core`
(forked 2026-08-30 from `3017381`) is fully merged — zero commits ahead of
`main` — and is no longer edited.

## Resume And Current Task (2026-09-12)

**Resumed** at the product owner's direction after `project-management`
verified the pause condition (significant `component-catalog` progress) was
met by v0.2.11. Re-verified on resume: the supervisor module and its tests are
on `main`; the published base is recipe 7 and predates the display stack.

**Design settled with the owner in conversation** and recorded in the
[display-transport design note](display-transport-design.md), points T1–T9:
Xvnc (not Xvfb plus a scraper) as the IDE's display server; Xvnc, Openbox and
websockify as product-derived infrastructure children ahead of the single
foreground IDE; a `display` section in the runtime plan; RFB on a Unix socket
only, gated by a per-run X cookie and a per-run bridge token; a dynamically
allocated host-loopback port; the browser as the client; rollout by image
label; passthrough retained as the `host-x11` authorization. The owner's one
correction to the summary — "the supervisor also starts an Xvfb" — is
recorded as T1.

**Implemented on this branch (2026-09-12):**

- `container_runtime/contract.py`: `DisplayPlan` and the optional `display`
  section (`contained` with listen address, port, token path; `host-x11`);
  absent still means passthrough.
- `container_runtime/supervisor.py`: per-child readiness probe with timeout,
  so the window manager and bridge start only once the X socket exists; a
  child that exits or stalls before ready fails the start (exit 2, named).
- `container_runtime/display.py` (new): per-run `Xauthority` (wildcard
  cookie, written directly in libXau format), websockify token file, and the
  three children. `entrypoint.py` starts them ahead of the surface; headless
  jobs declare none.
- `base_image.py`: recipe **8** adds `tigervnc-standalone-server`,
  `xfonts-base`, `novnc`, `python3-websockify`, `openbox` and the label
  `devcapsule.base.display=contained`; `install_display` is separable so the
  e2e can layer it on an existing base.
- `display_client.py` (new, host side): token, loopback port, noVNC URL,
  readiness watcher that opens the browser (host-open bridge when the
  launcher itself runs in a capsule; print-only fallback).
- `configurations/pycharm/_launcher.py`: `display_transport` option; under
  `contained` no `DISPLAY`/`XAUTHORITY`/X-socket crosses, the token file is
  mounted read-only and the bridge port published to `127.0.0.1` (listens on
  host loopback directly under host networking); network `none` is refused
  with the alternatives named; a display disclosure joins the storage summary.
- `commands/project.py`: transport selected from the image label and the
  `host-x11` answer, with the reason printed; `host-x11` added to the
  run-once authorizations. `project_configuration.py`: `host-x11` as a
  workstation capability node with the trade-off in its description.
- README: base recipe 8, a *Display* section, runtime-plan contents.

**Evidence:** unit suite 611 passed, 1 pre-existing xfail; mypy clean on 128
files; new tests in `test_contained_display.py`, `test_display_client.py`,
and additions to `test_supervisor.py`, `test_pycharm.py`,
`test_project_commands.py`, `test_base_image.py`. Spike record in the design
note (Xvnc on a Unix socket with no TCP listener, cookie refusal, token gate).
Runtime-image e2e (`tests/e2e/test_runtime_image.py`, run 2026-09-12 with
`DEVCAPSULE_E2E_BUILD_NETWORK=host` against the lock's recipe-6 base plus the
display packages, PEX rebuilt from this source): passed in 95 s. It proves,
from inside the running capsule, that the only TCP listener is the bridge on
6080, that Xvnc's X socket exists, that the right token gets the RFB
greeting and a wrong or missing one is closed, that `vnc.html` is served,
that Xvnc, Openbox and websockify are direct children of PID 1 running as
uid 1000, that the fixture IDE sees `DISPLAY=:1` and the per-run
`XAUTHORITY`, and that `docker stop` still ends the session with 143. The
passthrough and headless runs in the same test are unchanged and pass.

**Planned next step:** deliver this branch by pull request; then the owner
builds or publishes a recipe-8 base (`devcapsule images build --type base`
from this source; publication is a release step the owner drives) and runs
the **ratification day** — a full day of ordinary development inside the
contained desktop, aesthetics judged at hour six — before the ledger row
moves from `proposed` to ratified. Only after ratification does the X11
passthrough bug close.

**First owner run, 2026-09-13:** the contained run failed at start with
Xvnc's "server already running": under the host networking this repository's
project authorizes, the capsule's `:1` collided with the owner's host display
`:1` through the abstract socket namespace. Fixed the same day (design note
T2a): the entrypoint picks a free display number from `:10` and Xvnc listens
on its filesystem socket only. Verified against the owner's daemon before the
change, then by the unit suite (612 passed), mypy, and the runtime-image e2e
rerun, which now also asserts that no abstract X socket of ours exists.
The hands-on script is unchanged; rerun it from `build`.

**Open threads (2026-09-12):**

- **Reconnect from a second `project run`**: the second launcher cannot
  recover the first run's token; today the URL lives in the first launcher's
  output. Design candidate: keep the token beside the launcher's runtime
  files keyed by container name, so a second run prints the URL instead of
  failing on the duplicate name.
- **Clipboard in practice** (T8): Java `CLIPBOARD` versus the VNC selection
  is a ratification-day finding; `autocutsel` is the remedy if needed.
- **Aesthetics**: Openbox runs on its distribution defaults (a harmless
  message about a missing Debian menu file); a minimal `rc.xml`, HiDPI
  scaling and the default geometry are ratification-day inputs.
- **Network `none`** cannot carry the display (T4); recorded, not fixed.
- **Recursive successor** still launches on passthrough by default (its
  options do not set `display_transport`); switching the dogfood successor to
  the contained display is deliberate follow-up work once a recipe-8 base is
  the lock's base.
- The host-side `webbrowser` opener is untested against a real desktop in
  this container; the readiness watcher and the bridge fallback are unit
  tested.

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

Recorded 2026-09-12 on resume:

- **`2026-08-30-project-management-component-contract-is-load-bearing.md` —
  acknowledged.** The pause it recorded is over (resume above), and its
  standing instruction is honoured by construction: this stage changes no
  part of the supervisor–component contract. `ComponentDefinition`,
  `ComponentRuntimeTemplate`, the state-slot model and catalog selection are
  untouched; the runtime plan grew an *additive* `display` section that no
  component declares or reads, and the supervisor grew a readiness probe that
  no component sees. Nothing needs routing to `component-catalog` first. The
  item's warning stays in force for any later deliberate contract change.

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
- Two live observations: the first successor's ~45 s clean exit was the
  owner closing the IDE from its X window — so the D3 interactive
  contract was itself exercised live: a human closed the real IDE and
  the supervised session ended with an honest exit 0 (an earlier
  single-instance-activation hypothesis recorded here was wrong); and
  the fabricated retained-run workspace used to drive stage 5/6 by hand
  was removed after the proof — the protocol still has no CLI that
  creates a fresh pre-launch retained run.
- The published base still predates the supervisor; publishing a
  post-`500909d` base remains a release step the owner drives.
- **The base-image override is still active on the owner's checkout**:
  `base-image` is authorized to local `devcapsule-base:supervisor-stage1`
  (and `claude-code-download` to `true`), so the next `project run` on
  this checkout launches from the supervisor base. Revert with
  `devcapsule project config authorize base-image <locked reference>` if
  the published base is wanted before a new one ships.
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

- [Display transport design note](display-transport-design.md) — T1–T9,
  settled with the product owner 2026-09-12 and verified by the same day's
  spike: the contained display's mechanism (Xvnc, Openbox, websockify under
  the supervisor), the runtime plan's `display` section, the two per-run
  gates, host-side port and browser handling, rollout by image label, the
  `host-x11` authorization, clipboard, the regression test, and the recorded
  stretch options (native-window modes, GPU streaming).
- [try-contained-display.sh](try-contained-display.sh) — the owner's hands-on
  script for the ratification day: build the PEX and a local recipe-8 base
  from this branch, select it for a checkout, run the contained desktop (the
  default) and the legacy passthrough (`--authorize host-x11 true`) side by
  side, verify mounts, ports, processes and the manifest, then revert.
- [Supervisor core design note](supervisor-core-design.md) — D1–D9, all
  reviewed with the product owner 2026-08-30; the authoritative record of
  the supervisor scope, the transport lineup (contained desktop offered,
  native-window stretch, passthrough by authorization), and the D2
  restaging to one distinguished foreground child.
