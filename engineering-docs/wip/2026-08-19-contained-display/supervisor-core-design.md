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

## D8. User Interactivity: The Supervisor Asks Nothing In V1

Raised by the product owner at review: when interactivity from the user is
needed, what UI mechanism does the supervisor get?

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
