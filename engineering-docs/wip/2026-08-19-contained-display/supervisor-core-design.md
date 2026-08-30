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

## D2. Child Declaration — RESTAGED 2026-08-30

**Ruled by the product owner at review:** stage 1 carries **one
distinguished foreground child only** — the IDE, or in headless mode the
job — because the configuration language and UX for declaring a children
list are genuinely tricky and deserve their own design exercise, taken only
after the supervisor has proven itself (especially for e2e testing and
non-interactive runs).

The staging is cleaner than a cut, because the declarative list below turns
out to have no V1 customer on the user-facing side:

- multiple foreground IDEs are post-V1 by the ratified supervisor split;
- infrastructure children (Xvnc, window manager, noVNC) arrive with the
  display stage but are **product-derived from the resolved transport,
  never user-declared** — they use the supervisor's internal API, not the
  configuration language;
- the headless job is the same distinguished slot with no GUI.

Stage-1 consequences: the runtime plan schema is **unchanged** — today's
single launch command *is* the declaration — so there is no migration and
the E3 assertion set is untouched; readiness gates are deferred to the
display stage that needs them; the internal state machine is still written
over a set of children (supervising N is no harder than 1 in the
reap/forward/shutdown core, and hardcoding 1 would be artificial), but
exactly one is exposed.

The original multi-child sketch below is retained as design input for the
later exercise, not as stage-1 scope.

### The original sketch (deferred)

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

**Ruled by the product owner, 2026-08-30:** mode 3 goes — the product does
not offer unwarranted security exposure it can help. Mode 2's tool is
decided later, between Xephyr and Xpra, by the spike. Two recorded nuances:

- **Mode 3 dies as an offered mode, not as the interim dogfood transport.**
  Until mode 1 or 2 lands, development — including the supervisor's own
  dogfooding — runs on X11 passthrough, so mode 3 will ironically be the
  best-tested path for a while. That is acceptable precisely because it is
  not offered: the exposure is ours, on our machines, already documented in
  the bug. The retirement lands when a replacement transport does.
- The ledger row's method (spike, then a full day of ordinary development)
  applies to whichever mode-2 tool the spike favors.

**Xpra arguments re-verified 2026-08-30**, per the 2026-08-19 note's
currency caveat, against the live project:

- *Maintenance*: healthier than the "one principal developer" line implied —
  active releases (6.5.2 on 2026-07-27), an LTS 5.1.x channel beside the
  6.x stable stream, prompt fixes. Softened, not reversed: concentration
  remains.
- *Surface*: confirmed and sharpened — recent releases fixed RCE
  vulnerabilities in URL parsing and tightened download-path handling. The
  fixes were prompt, but a display transport with its own RCE history is a
  real consideration for a containment product.
- *Java seamless weak spot*: **confirmed as structural, not stale.** The
  issue class — focus change requests failing in Java apps, seamless
  JetBrains windows not gaining focus, Java menus stuck above other
  windows, mouse offsets on undecorated Java windows — spans years of
  tickets and follows from remoting Swing's window-management assumptions
  through a synthetic WM. JetBrains' runtime keeps evolving on its side,
  so this is a moving target on both ends, and our reference IDE sits
  exactly on the weak spot.
- *Version skew*: confirmed by the project's own LTS/stable channel split.

**Topology and licensing, added 2026-08-30 at the owner's question.** Xpra
in seamless mode runs on *both* sides: the server inside the capsule (a
curated, pinned base-image component), the client on the host desktop —
and the host client is what the user installs, from a distro deb, PyPI, or
xpra.org's repos. The HTML5 client avoids the install but yields
desktop-in-a-browser, not seamless windows. Consequences: the mode breaks
"Docker plus our artifact is all you need" (acceptable for an opt-in, but
an asterisk mode 1 does not carry), and version skew doubles — we pin the
capsule server while the user's distro supplies the client, a mismatch we
cannot control. Xephyr is host-side *only*: one standard X.org-tree
package, MIT-licensed, frozen-stable, with **no capsule change at all** —
the capsule receives a bind of one nested display socket.

GPL-v2 is not a blocker in any shape used here: Xpra is invoked as
separate processes, never linked, never in the PEX; including the server
in the base image is the same obligation class as the GPL userland already
there, handled by F3's per-artifact license metadata.

**Final ruling, 2026-08-30: mode 2 is a stretch goal, not a V1 offering.**
The owner judged both candidates less than ideal for the same reason, which
is sharper than any per-tool asterisk: every host-side display component
makes adopters' desktops our debugging surface — Xephyr's GLX, grab, HiDPI,
and packaging variation, Xpra's all of that plus dual-side version pairing —
failing on machines we do not control and cannot reproduce. The contained
desktop inverts the ownership: the whole display stack lives in the curated
image, identical everywhere, and the universal client is a browser the
adopter already has. So:

- **V1 offers one transport: the contained desktop** (mode 1). The product
  is opinionated about presentation in V1 after all — because the
  opinionated option is the one whose failures are ours to debug.
- **Native-window modes are a recorded stretch**, not dropped: the analysis
  above stands as the design record, Xephyr presumptive over Xpra if the
  stretch is ever pursued, and pursuing it is a post-V1 or candidate-time
  call.
- **The spike simplifies** to the ledger row's original subject: Xvnc plus
  noVNC, with a native VNC viewer as an *optional* performance upgrade —
  optional with a browser fallback, so it never becomes a support
  obligation. The Xephyr-versus-Xpra bake-off leaves the V1 critical path.
- The interim dogfood window is unchanged: passthrough until mode 1 lands,
  unoffered; the cheaper floor (removing the `xhost` advice) still rides
  with the supervisor work.

**Amended by the product owner, same day: mode 3 is retained — behind
explicit authorization.** The earlier "mode 3 goes" is superseded. The final
transport lineup:

- **Mode 1, contained desktop: the offered default.** The only mode the
  product recommends, and the only one carrying the yolo-by-default claim.
- **Mode 2, native window via Xephyr/Xpra: stretch**, unchanged from above.
- **Mode 3, host X11 passthrough: retained as an explicitly authorized
  mode.** It becomes an authorization node in the configuration grammar,
  answered the way development sudo and host network already are: never a
  default, never elicited as a suggestion, granted only by the user's
  explicit answer with the trade-off stated at the point of decision — the
  capsule receives the full trusted host session credential: keystroke
  capture across the session, window capture, input injection, and
  clipboard access. The grant appears in the run manifest and inspection
  output; the session-credential regression test is recorded as *waived by
  authorization* for such runs, and the yolo-by-default claim is explicitly
  not carried in this mode.

What this buys, stated honestly: the native-window desire is served today
with zero host packages and zero new display code — the user trades the
boundary for the window placement, knowingly — and the mode ships
well-tested precisely because it is the path development lived on. This
also matches the ledger row's original language exactly: "X11 passthrough,
if retained at all, is opt-in with its trade-off documented, and is not the
default." It is retained, and that is its shape.

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
