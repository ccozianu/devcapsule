# Intake: Display Transport Design Input, And The Interim Window

Delivered: 2026-08-19

From: `project-management`, routing the design discussion that opened this
workstream.

## What Is Being Handed Over

A design note:
[Display transport options and clipboard policy](../../2026-08-09-project-management/2026-08-19-display-transport-options.md).

It is input, not a decision. The contained-display direction is already decided
in the [V1 scope ledger](../../2026-08-09-project-management/v1-scope-ledger.md)
and the transport specifics are `proposed` pending a spike. The note records
three things that row does not contain, produced in discussion with the product
owner on 2026-08-19 while deciding whether v026 is fit to start real projects
on:

1. **An interim mitigation** for the window between now and v027.
2. **A maturity comparison** of Xephyr, VNC with noVNC, and Xpra, on the
   points-of-failure axis rather than on features.
3. **A clipboard policy**, which the ledger row currently treats only as an
   accepted regression.

## Why This Is Urgent Rather Than Merely Open

The ledger deferred the transport to v027 on sound reasoning: the change touches
the base recipe, the launcher, port allocation, and the platform matrix, and is
not compatible with v026 being the base the product owner starts projects on.

The product owner has now decided that v026 is good enough to start real
projects
on, and those projects will run agents. For the several weeks until v027, real
work will therefore run on a transport that hands the container the developer's
**trusted** X cookie — full keystroke capture across the host session, window
capture, XTEST input injection, and clipboard read and write. Neither the bug's
candidate list nor the ledger row addresses that window. That is the gap this
workstream should close first, and it is why the handoff names it as the next
resumable task.

## The Three Contributions, In Brief

**The framing.** Of everything a trusted cookie grants, only clipboard access is
addressable by clipboard policy. Once the X server lives inside the capsule, the
clipboard stops being architecture and becomes a dial. So choose the transport
on
the keylogging and injection grounds, then choose clipboard policy independently
— the question a user notices first should not drive the architecture.

**The interim option, not currently in the bug's candidate list.** A nested X
server on the host: `Xephyr :N` with its own auth cookie, the container given a
bind of only `/tmp/.X11-unix/XN` — one socket file, not the directory — and a
cookie valid only for the nested display. The capsule then has no route to the
host session at all. Two properties make it fit this window specifically: it
needs **no base image change**, so it does not disturb v026; and it does not
depend on the X SECURITY extension, so the reason untrusted cookies were
dismissed in the bug does not apply. Its costs are stated in the note — single
screen, software rendering with weak GLX, Linux only — and it is a stopgap, not
a
competitor to the decided direction. The product owner's reaction was that it
looks easy to kick the tires with, and kicking those tires is also the first
half
of the transport spike.

There is a cheaper floor if even that is too much: remove the
`xhost +SI:localuser:<user>` advice from the launcher warning, which currently
recommends the most dangerous available action, and state the exposure in the
runtime plan and documentation as the bug already requires.

**On maturity.** Summarized in the note's table. The three points that matter
most: noVNC is only the client half, and `Xvnc` with a native viewer is two
parts
rather than five; `x11vnc` is the tool most tutorials name and the wrong one
here, being for attaching to an existing display and effectively unmaintained
since around 2020; and Xpra is the most capable and the most surface, with its
known weak area being precisely Java seamless mode. The note also carries a
currency caveat: these claims should be re-verified before commitment.

**On clipboard.** The recommendation is asymmetric — automatic out, explicit in
—
because host-to-capsule is the leak an agent can poll, while capsule-to-host is
an injection risk requiring a human action. Two additions to the ledger row are
proposed: declare the clipboard policy in the runtime plan and inspection output
so the inspector verifies it, and reframe text-only clipboard as a deliberate
control rather than a regression, since images are the highest-bandwidth
exfiltration path a clipboard offers.

## What Should Close The Bug

Not the transport landing — a test. From inside the capsule, under whatever
transport ships, XTEST injection, root-window capture, keymap polling, and host
clipboard read must all fail against the host session. That is the Stage 6
inspector's set-equality philosophy applied to the display, and it should remain
a permanent regression test, because the failure mode is a future launcher
change
silently reintroducing a working path.

## Boundaries

The `xdg-open` and `BROWSER` forwarding shim is **not** yours. It ships in v026
under `recursive-e2e` because it behaves identically under every candidate
transport.

Nothing in the note or this item overrides the ledger row's ratification method:
spike a contained VNC or noVNC session and Xpra seamless mode, then perform a
full day of ordinary development inside the result before ratifying it into V1.
Aesthetics that hold at hour six are the relevant test.

Items sent by `project-management` cannot be forwarded. The design note is an
argument; disagreeing with any part of it is this workstream's prerogative.
Priority between the interim mitigation and the permanent transport is yours,
subject to the urgency stated above.
