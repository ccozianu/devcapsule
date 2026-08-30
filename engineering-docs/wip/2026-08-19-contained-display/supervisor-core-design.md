# Supervisor Core: Design Note

Written 2026-08-30 by `contained-display`. Status: **draft for product-owner
review** — the numbered decision points below are the review agenda; each
carries a recommendation, none is decided until reviewed.

## Where It Slots In

The container-side entrypoint already exists:
`devcapsule_runtime/entrypoint.py` runs as PID 1, prepares the filesystem and
environment from `RUNTIME_PLAN.json`, and then `os.execvpe`s the IDE — the
IDE *replaces* the entrypoint and capsule lifetime becomes IDE lifetime. The
supervisor is a change to exactly that last line: spawn and supervise instead
of exec and vanish. Everything upstream — resolution, materialization, the
runtime plan, the OCI generic-entrypoint contract — keeps its shape; the plan
schema grows a child declaration and the entrypoint stops abdicating.

V1 scope, per the ratified split: PID-1 duties, a declarative child list, an
explicit session end, and a headless mode. No tray, no control socket, no
secondary IDEs, no restart policies, no health probes.

## D1. PID-1 Strategy: Pure Python, Or `tini` In Front

A PID 1 must reap orphaned zombies and forward signals. Options:

- **Pure Python supervisor as PID 1** — a `SIGCHLD`-driven `waitpid` loop and
  explicit signal forwarding. No base-image change, no new binary, and the
  supervisor is ordinary product code testable with fake children.
- **`tini` (or `docker run --init`) wrapping the Python supervisor** — reaping
  correctness outsourced; our process becomes PID 2 with
  `PR_SET_CHILD_SUBREAPER`.

**Recommendation: pure Python.** The reap-and-forward core is small and
well-trodden; taking a new binary into the curated base to avoid writing it
contradicts the component-curation posture, and `--init` is host-flag
dependent — exactly the kind of ambient variation the runtime plan exists to
eliminate. `tini` remains the recorded fallback if signal semantics prove
subtler than expected.

## D2. Child Declaration

The runtime plan gains an ordered `children` list. Each child:

- `name` — stable identifier, used in logs and evidence;
- `kind` — `infrastructure` (X server, window manager, VNC bridge),
  `surface` (the interactive IDE; **at most one in V1**, per the stated
  one-interactive-IDE limitation), or `job` (headless work);
- `command` and environment additions;
- `readiness` — `none`, or wait-for-socket/wait-for-file with a timeout, so
  an X server is accepting connections before its IDE starts.

Start order is list order gated on readiness; shutdown is reverse order.

**Backward compatibility:** a plan with no `children` list means one implicit
`surface` child built from today's launch command. Existing configurations
keep working unmodified; the E3 assertion set (generic OCI entrypoint and
command) is unchanged.

## D3. Lifetime Binding: What Ends The Session

Today, IDE exit ends the capsule as a side effect. Under the supervisor:

- **Interactive mode:** the session ends when the `surface` child exits, or
  on explicit end (D4), whichever first. Closing the IDE still ends the
  capsule — no behavior change an existing user would notice — but the
  ending is now *supervised*: orderly shutdown, honest exit code.
- **Infrastructure child death** is a session **failure**, not a quiet
  event: the supervisor terminates everything in reverse order and exits
  non-zero naming the dead child. No restarts in V1 — a restart policy is
  post-V1 surface.
- **Headless mode:** no `surface` children; the session ends when the `job`
  child exits, and the supervisor propagates its exit code. A headless plan
  with no `job` either is rejected at validation.

**Recommendation:** exactly the above. The display's session-persistence
story ("disconnecting leaves the IDE running") is a *display* property —
disconnect is not surface-exit — and needs nothing extra from the supervisor.

## D4. Control Surface: Signals Only In V1

The explicit session end is `SIGTERM` to PID 1 — which is precisely what
`docker stop` sends. So the V1 control story is: `docker stop <capsule>` is
the explicit end, documented as such; the supervisor answers with
reverse-order graceful shutdown (child `SIGTERM`, grace period, `SIGKILL`
stragglers), then exits honestly. `SIGINT` behaves identically for
foreground runs.

A control socket (one-click secondary IDEs, session queries) is the post-V1
desktop layer's entry point and is deliberately absent; nothing in D2/D3
forecloses it.

**Recommendation:** signals only. It reuses Docker's own lifecycle verbs,
adds zero attack surface, and keeps "minimal" honest against the ledger
row's recorded pressure.

## D5. The Cleanup Boundary

The supervisor guarantees **internal** cleanliness: no orphaned children, no
half-dead process tree, an exit code that tells the truth. It cannot and
does not remove its own container — container removal stays host-side
launcher policy, which is the coordination backlog's reaping entry. The
division: *the supervisor makes the exit honest; the launcher makes removal
safe.* That division is the coordination this workstream owes the reaping
entry before it closes.

## D6. Child Output

Options: children inherit the supervisor's stdout/stderr directly
(interleaved, zero code, `docker logs` unchanged), or per-child prefixed
pipes.

**Recommendation:** the `surface`/`job` child inherits, so today's log
behavior is untouched; `infrastructure` children get line-prefixed pipes
(`[xvnc] …`), because interleaved unlabeled X server chatter is exactly what
makes display bugs undiagnosable. Sanitization rules apply at the prefix
point.

## D7. Headless Authorization Acknowledgements

Unattended runs need pre-recorded answers for authorization and acquisition
acknowledgements. That design rides the supervisor but is separable: it is
plan-validation work, not process-management work. It gets its own note
after this one is reviewed; nothing in D2/D3 constrains it beyond `job`
children existing.

## D8. User Interactivity: The Supervisor Asks Nothing — DECIDED

**Ruled by the product owner, 2026-08-30:** the supervisor inside Docker asks
nothing; all asks belong to the launcher that launches the Docker container,
host-side. The owner added the display half explicitly: the supervisor must
still *display* — asking nothing does not mean saying nothing.

What it displays, by mode:

- **V1 (host X11):** stdout/stderr — the launching terminal in foreground
  runs, `docker logs` always, and failure evidence in the run record. The
  fail-fast message is the supervisor's V1 "UI".
- **Under the contained display, later:** a display-only status surface on
  the capsule desktop is permitted and expected (session state, child
  health, "session ending"), because display-only content is harmless even
  if forged. It belongs to the desktop layer, not the V1 core.

The standing rule survives unchanged below: in-capsule UI may display
status; it never collects consent.

The original analysis follows.

Nearly all of the product's questions are answered before the supervisor
exists: authorization, acquisition acknowledgements, and configuration
elicitation run host-side in the launching terminal through the elicitation
engine, and headless runs are pre-recorded-answers-only by D7. What remains
mid-session is rare — a dead infrastructure child with a recoverable choice,
a future mid-session capability request.

**The trap, recorded as a standing rule.** The tempting mechanism once the
contained display exists — a consent dialog rendered on the capsule's own
desktop — is forgeable by construction: contained code, including an agent
running at full autonomy, can paint a pixel-perfect copy of any prompt the
capsule display can show. If users learn that real consent appears on the
capsule desktop, the forgery works. Therefore: **trust-bearing prompts —
authorization, capability grants, consent — are never rendered inside the
capsule. In-capsule UI may display status; it never collects consent.**
Consent is answered on the host side of the boundary, where contained code
cannot draw.

**Recommendation, in tiers:**

- **V1: the supervisor asks nothing.** Every question is answered before
  launch, pre-recorded, or the supervisor fails fast with an actionable
  message — the product's existing refuse-with-evidence posture. In
  foreground runs its stdout is the launching terminal, so the human sees
  why. Zero new surface.
- **Post-V1: the control socket is the transport, never the UI.** The
  supervisor emits question/answer requests over the seam D4 reserves;
  host-side surfaces render them — a CLI subcommand, the tray, a host
  notification. The supervisor stays toolkit-free and transport-agnostic.

## D9. Opinionated About The Capsule Desktop, Or Not?

Raised by the product owner at review: given the development load of the
contained display, are we opinionated about the capsule desktop, or do we
offer — at least to Linux/X desktop users — the ability to keep running
IDEs the way they do now, as native windows on their own desktop? The
product has so far deliberately taken the non-opinionated approach.

**Recommendation: non-opinionated about presentation, opinionated about the
boundary.** The dilemma has a third position because the two current modes
differ in *two* properties at once — where the window appears, and whether
the capsule holds the host session credential — and those properties are
separable:

1. **Contained desktop** (default): the capsule's own display over
   VNC/noVNC. Cross-platform, resumable, the boundary visible in every
   screenshot. The flagship.
2. **Native window on the host desktop** (Linux/X opt-in): a **nested X
   server with an isolated cookie** — the Xephyr shape from the 2026-08-19
   design input, promoted from interim stopgap to a permanent presentation
   option. The IDE appears on the user's desktop exactly as today, but the
   capsule is bound to one nested display socket with a cookie valid only
   there: **it passes the same session-credential regression test as the
   contained desktop.** Known costs stand: single screen, software GLX,
   Linux only.
3. **Raw trusted-cookie passthrough** (expert escape hatch, if retained):
   today's transport, opt-in and loudly declared, never the default —
   exactly the posture the ledger row already records ("X11 passthrough, if
   retained at all, is opt-in with its trade-off documented"). The run
   manifest and inspection state that the boundary test is waived; the
   yolo-by-default claim is honestly per-transport, and this mode does not
   carry it.

Two structural notes in favor:

- **The supervisor is what makes this affordable.** Transports differ only
  in the declared infrastructure children (none; nested-X bridge; Xvnc +
  window manager + noVNC) and the environment handed to the surface child.
  Being non-opinionated costs configuration, not architecture — this is the
  supervisor-first sequencing paying for itself.
- **The boundary claim stays uniform where it matters.** Modes 1 and 2 both
  pass the permanent regression test, so "the capsule cannot reach your
  host session" holds for every non-expert user regardless of taste in
  window placement. Opinionation lands only where the thesis needs it.

Awaiting the owner's ruling; the ledger row's transport method (spike, then
a full day of ordinary development) applies to mode 2 as well as mode 1 if
this is adopted.

## Testing Shape

- Unit: the reap/forward/shutdown state machine against fake children
  (sleep/exit/ignore-TERM scripts) — no Docker required.
- E2E: extend the existing recursive-e2e assertion set — supervisor is
  PID 1, declared children present with expected parentage, `docker stop`
  yields clean reverse-order shutdown and the documented exit code,
  headless job propagation, and second-launch persistence unchanged.

## Non-Goals, Restated Once

Tray, secondary IDEs, multi-IDE sessions, control socket, restart and health
policies, and any display-transport choice. The supervisor must run children
correctly under host X11 today and not care what they are.
