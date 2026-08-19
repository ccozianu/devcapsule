# Display Transport Options And Clipboard Policy

Written 2026-08-19 by `project-management`, from a design discussion with the
product owner while deciding whether v026 is fit to start real projects on.

**This is input, not a decision.** The contained-display direction is already
decided in the [V1 scope ledger](v1-scope-ledger.md) and the transport specifics
are `proposed` pending a spike. This note exists because the discussion produced
three things that document does not contain: an interim mitigation for the
window between now and v027, a maturity comparison of the candidates, and a
clipboard policy that the row treats only as an accepted regression.

The subject bug is the
[X11 session-credential exposure](../../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md).

## The Framing That Changes The Order Of Decisions

Of what a trusted X cookie grants the container — keystroke capture across the
whole host session, window capture, XTEST input injection, and clipboard access
— **only the last is addressable by a clipboard policy.** No clipboard setting
prevents a capsule from keylogging the developer's session.

The useful consequence: **once the X server lives inside the capsule, the
clipboard stops being architecture and becomes a dial.** Every candidate
transport shares the property that the container holds no host display
connection, so clipboard access becomes a bridge that is specified deliberately,
at whatever friction is chosen.

Therefore the transport should be chosen on the keylogging and injection
grounds, and the clipboard policy selected afterward and independently. The
clipboard question, which is the one a user notices first, should not influence
the transport choice at all.

## The Window This Note Exists For

The ledger row defers the transport to v027 on the explicit reasoning that the
change touches the base recipe, the launcher, port allocation, and the platform
matrix, and so is *incompatible with v026 being the base the product owner
starts projects on*. That reasoning is sound and is not challenged here.

Its consequence is that real projects, containing agents, will run for several
weeks on a transport that hands the container a full host session credential.
Neither the bug's candidate list nor the ledger row addresses that window.

## Interim Option Not Currently In The Candidate List: A Nested X Server

`Xephyr` runs a nested X server as an ordinary host process, rendering into a
host window.

**Mechanics.** The launcher starts `Xephyr :N -auth <cookie-for-:N>` on the
host. The container receives a bind of **only** `/tmp/.X11-unix/XN` — a single
socket
file, not the directory — and a cookie valid only for the nested display. The
capsule's clients therefore have no route to the host session: no keystroke
capture, no XTEST, no window capture, no host clipboard.

**Why it suits the interim window specifically.**

- **No base image change.** It is a host-side process plus a launcher change, so
  it does not invalidate v026 as the base the product owner is starting projects
  on — which was the entire reason the real fix was deferred.
- **It does not depend on the X SECURITY extension**, so the reason untrusted
  cookies were dismissed in the bug — known JetBrains breakage — does not apply.
  The IDE sees an ordinary, fully trusted X server that happens to be a
  different one.
- One host package and a small launcher change, not a spike.

**Honest costs.** A single virtual screen in one host window, so it previews the
v027 multi-monitor regression rather than avoiding it. Software rendering, with
weak GLX support, which may aggravate the existing
`jbr-slow-x11-alpha-compositing` bug and bears on the JCEF preview bug. Linux
only, so it does nothing for the macOS and Windows story that VNC subsumes. It
is a stopgap that buys the security property early, not a competitor to the
decided direction.

**The cheaper floor, if even that is too much.** Remove the
`xhost +SI:localuser:<user>` advice from the launcher warning, which currently
recommends the most dangerous available action, and state the exposure in the
runtime plan and user documentation as the bug already requires. Hours, not
days, and it converts an implicit consequence into an explicit authorization.

## Maturity Of The Candidates

The product owner's stated concern is introducing further points of failure into
the ensemble, so this compares on that axis rather than on features.

| | Xephyr | VNC (`Xvnc`/TigerVNC) + noVNC | Xpra |
|---|---|---|---|
| Age and lineage | ~20 years, in the X.Org tree | TigerVNC ~15 years; noVNC ~14 years | ~17 years |
| Maintenance | Frozen; stable, maintenance-only | Actively maintained, both halves | Active, but largely one principal developer |
| Deployment proof | Standard for nested-X testing and CI | Very large: cloud consoles ship browser VNC | Niche but real |
| New moving parts | One host process | Two to four | Three or more, wide surface |
| Java / JetBrains | Fine; weak GLX | Fine, well-trodden | Weakest spot: seamless plus Swing/JBR |
| Base image change | None | Yes | Yes |
| Version-skew risk | None | Low | Real: client/server matching |

Three notes that matter more than the table:

- **noVNC is only the client half.** The maturity question is really the server
  it is paired with. The naive stack is five parts — `Xvnc`, a window manager,
  `websockify`, noVNC, and a browser. `Xvnc` with a native viewer is two parts
  and performs better for a Java IDE. Treating noVNC as an additional client for
  demonstrations and zero-install access, rather than as the only client, keeps
  the browser out of the critical path while preserving the platform-matrix
  argument the ledger row makes.
- **`x11vnc` is the tool most tutorials name and is the wrong one here.** It
  attaches to an existing display, and has been effectively unmaintained since
  around 2020. For a fresh contained display, `Xvnc` is the maintained choice.
- **Xpra is the most capable and the most surface.** Seamless windows are a
  genuine product advantage and its clipboard direction control is a flag rather
  than an implementation. Against that: the widest feature surface, real
  version-skew sensitivity, maintenance concentrated in one developer, and a
  known weak area that is precisely Java seamless mode.

**On points of failure.** Count matters less than whether failure is loud. All
three fail visibly: no window, no connection, wrong colours. The status quo is
the only option with a silent failure mode — X11 passthrough works perfectly,
looks correct, passes the mount inspector, and leaks the session. Adding one
loud component to remove one silent one reduces risk even though it raises the
part count.

**Currency caveat.** Maturity claims about fast-moving projects — Xpra's current
release, and KasmVNC as a possible single-part alternative to the
`Xvnc` + `websockify` + noVNC stack — should be re-verified before commitment.
The ledger row's method, a spike followed by a full day of ordinary development
inside the result, is the right gate.

## Clipboard Policy, Once The Display Is Contained

From most to least friction:

1. No clipboard. Not viable for development.
2. Explicit push in both directions. noVNC's clipboard panel is exactly this.
3. **Asymmetric: automatic out, explicit in.** Recommended.
4. Automatic both directions, text only.
5. Automatic both directions including images and files. The largest
   exfiltration channel.

**Why the asymmetry.** The two directions carry different risk. Host to capsule
is the *leak*: an agent inside can read whatever was last copied — a password
from a manager, a token, customer data — and can poll for it. Capsule to host is
an *injection* risk: the capsule sets the host clipboard and hopes the developer
pastes it into a shell, which requires a human action. Allowing copy-out
automatically while requiring one deliberate gesture for paste-in keeps the
frequent low-risk direction seamless and makes silent polling of the host
clipboard impossible.

Mechanically, per transport: for VNC the clipboard is already explicit in the
protocol, so this is configuration rather than code, with per-direction switches
in TigerVNC and a clipboard panel in noVNC. For Xpra it is
`--clipboard-direction`, plus filtering. For Xephyr there is no bridge at all by
default, so explicit-in is a small host-side helper that reads the host
selection and pushes it into the nested display — the most auditable form of the
idea.

## Two Additions Proposed To The Ledger Row

**Make the clipboard policy a declared authorization.** The product's claim is
an explicit, inspectable boundary, and the bug's *Expected Behaviour* already
requires residual exposure to appear in the runtime plan, the inspection output,
and the documentation. A capsule reporting `clipboard: out-only` in its manifest
is consistent with how mounts and network access are already treated, and turns
the dial into something the inspector verifies rather than a launcher detail.

**Reframe one accepted regression.** The row records "clipboard becomes
text-only; images and files no longer cross" as a loss. For a containment
product it is also a control: images are the highest-bandwidth exfiltration path
a clipboard offers. Worth stating as a deliberate boundary rather than a
casualty.

## What Should Close The Bug

Not the transport landing — a test. From inside the capsule, under whatever
transport ships, all of the following must fail against the host session: XTEST
injection, root-window capture, keymap polling, and host clipboard read. That is
the Stage 6 inspector's set-equality philosophy applied to the display, and it
should remain a permanent regression test, because the failure mode here is a
future launcher change silently reintroducing a working path.
