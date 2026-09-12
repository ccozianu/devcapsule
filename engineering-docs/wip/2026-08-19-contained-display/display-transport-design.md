# Contained Display Transport: Design Note

Written 2026-09-12 by `contained-display`. Status: **design settled with the
product owner in conversation on 2026-09-12; mechanism verified by a spike the
same day; implementation in progress on `contained-display/display-transport`.**
The numbered points record what was decided and why, so the implementation
can be checked against them and a later reader does not have to reconstruct
the conversation.

## Where It Slots In

The transport *ruling* is already made and is not reopened here: section D9 of
the [supervisor core design note](supervisor-core-design.md) settles that V1
offers exactly one transport, the contained desktop over Xvnc and noVNC, that
native-window modes (Xephyr, Xpra) are a recorded stretch, and that host X11
passthrough survives only behind an explicit authorization. The
[V1 scope ledger](../2026-08-09-project-management/v1-scope-ledger.md) row
*Contained Display And Desktop Integration* states the required outcome:
no host X socket, credential, or `xhost` grant; a loopback-only endpoint on a
dynamically allocated port; per-run token authorization recorded in the run
manifest; and a full day of ordinary development before ratification. The
[X11 passthrough bug](../../bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md)
is what this closes.

This note is the mechanism: which processes, started by whom, listening
where, authorized how, and what the host side does with them.

## T1. The Display Server Is Xvnc, Not Xvfb Plus A Scraper

The product owner's summary was "the supervisor also starts an Xvfb that
becomes the display server for our IDE". The corrected form: the supervisor
starts **Xvnc**, which is the same virtual-framebuffer X server with the RFB
server built in. Xvfb plus `x11vnc` would be two processes, with the second
polling the framebuffer for changes; Xvnc knows exactly which rectangles its X
clients damaged and encodes only those. One process, no scraping. TigerVNC's
Xvnc (1.13.1 on Ubuntu 24.04) is the implementation.

## T2. Process Tree Under The Supervisor

Everything below is a supervised child of the PID-1 supervisor from stage 1;
the display costs configuration, not architecture, exactly as D9 predicted.
Start order, all product-derived infrastructure children except the last:

1. **`xvnc`** — `Xvnc :1`, run as the capsule user. Listens for RFB on a
   Unix socket beneath `XDG_RUNTIME_DIR`, mode 0600, and on **no TCP port at
   all** (`-rfbport -1`). X access is gated by a per-run cookie in a
   per-run `Xauthority` file. Geometry 1920x1080, depth 24, DPI 96;
   `AcceptSetDesktopSize` (on by default) lets the client resize it.
2. **`window-manager`** — Openbox on `:1`. Not optional: Java IDEs need a
   window manager for focus, dialogs, and popups, so a bare Xvnc fails the
   hour-six test. Openbox is the smallest well-behaved stacking WM in the
   distribution.
3. **`novnc`** — websockify serving noVNC's static page and bridging
   WebSocket to the RFB Unix socket. This is the **only** listener the
   capsule exposes, and it is reachable only as T4 describes.
4. **The IDE** — the single foreground child, with `DISPLAY=:1` and the
   per-run `XAUTHORITY`. Its exit ends the session; nothing else does.

Nothing in the user's manifest names the infrastructure children. The
entrypoint derives them from the runtime plan's `display` section (T3). The
supervisor's contract is unchanged in kind: it still runs an ordered child set
with one foreground child. One addition it needed: a **readiness probe** per
child, because the window manager cannot start before the X socket exists and
websockify must not be advertised before it accepts connections. A child whose
probe does not succeed within its timeout is an infrastructure failure.

Headless mode (`-- COMMAND`) declares no display children at all; the job
runs exactly as in stage 1.

## T3. The Runtime Plan Carries A `display` Section

The runtime plan is the in-container contract and the honest record of what a
run was. It gains an optional top-level `display` object:

```json
"display": {
  "transport": "contained",
  "listen_address": "0.0.0.0",
  "port": 6080,
  "token_path": "/run/devcapsule-display-token"
}
```

- `transport` is `contained` or `host-x11`. A plan with no `display` section
  is read as `host-x11` so that older plans keep their meaning; the launcher
  always writes the section when it launches an image that has the display
  stack (T6), so a plan from this version onward is explicit.
- `listen_address` and `port` are where websockify listens *inside* the
  container. The launcher chooses them (T4) because only it knows the
  network mode.
- `token_path` names the file holding the per-run token, bind-mounted
  read-only by the launcher. The token itself is deliberately **not** in the
  plan, so the plan stays free of secrets and can be logged and inspected.

`host-x11` carries no listener and no token; the section exists so that the
manifest says, in so many words, that this run put the host session
credential inside the capsule.

## T4. What Is Exposed, And How Access Is Authorized

Two independent gates, both per run, both verified by the spike:

- **X access**: a cookie generated per run and written to a per-run
  `Xauthority` file owned by the capsule user. `xdpyinfo` without it is
  refused with "Authorization required".
- **RFB access**: websockify's `TokenFile` plugin maps the per-run token to
  the RFB Unix socket (`token: unix_socket:/path`). A request whose `token`
  query parameter is wrong or absent is closed without an upgrade; the right
  one receives the `RFB 003.008` greeting. Xvnc itself runs with no RFB
  security type because the only way to reach its socket is through that
  gate or by already being the capsule user.

The launcher generates the token with `secrets.token_hex`, writes it to a
0600 temporary file under `XDG_RUNTIME_DIR`, and bind-mounts it read-only at
`token_path`. The entrypoint reads it and writes websockify's token file
beneath the capsule's own runtime directory. The token appears in the run's
disclosure only as "token-authorized", never as its value.

Where websockify listens depends on the network mode the run already
authorizes:

- **bridge** (the default): websockify listens on all container interfaces
  on port 6080, and Docker publishes it to a **dynamically allocated host
  loopback port** (`-p 127.0.0.1:PORT:6080`). The token gate is what makes
  the bridge-side exposure to sibling containers harmless.
- **host**: there is no container network to publish from. websockify
  listens on `127.0.0.1:PORT` directly, with the same dynamically allocated
  port.
- **none**: nothing can be published and the display cannot be reached. The
  launcher refuses the contained transport under `none` with a message
  naming the alternatives (bridge, or the `host-x11` authorization). This is
  a recorded limitation, not a silent fallback.

The port is allocated by binding `127.0.0.1:0` on the host and releasing it.
The residual race between release and `docker run` is accepted and reported
honestly if Docker then fails to bind.

## T5. The Client Is A Browser; Nothing Host-Side Is Installed

The launcher prints the URL and opens it in the developer's default browser
once the host port accepts connections:

```text
http://127.0.0.1:PORT/vnc.html?autoconnect=1&resize=remote&path=websockify%3Ftoken%3D<token>
```

`resize=remote` makes the desktop follow the browser window through
`SetDesktopSize`, which matters for the aesthetics test. The URL is printed
before it is opened, so a native VNC viewer or a manual browser tab works
without any further support; that is the entire "native viewer optional"
commitment. When the launcher itself runs inside a capsule (the recursive
case) it has no desktop of its own: it asks the host-browser bridge if one is
authorized, and otherwise only prints.

Closing the browser tab does **not** end the session: the IDE keeps running
on `:1` and reopening the URL resumes it exactly where it was. `docker stop`
or closing the IDE ends it, as in stage 1. Reconnecting to an already running
capsule from a *second* `project run` is a recorded follow-up (the second
launcher does not know the first run's token); for now the URL stays in the
first launcher's output.

## T6. Rollout: The Launcher Selects The Transport From The Image

The display stack lives in the base image. Base recipe **8** adds
`tigervnc-standalone-server`, `xfonts-base` (Xvnc needs the core `fixed`
font), `novnc`, `python3-websockify`, and `openbox`, and labels the base
`devcapsule.base.display=contained`. Nothing in the component contract
changes.

The launcher reads that label from the materialized image it is about to
run (Docker inherits labels through `FROM`). If the label is present, the
contained transport is the default and host X11 passthrough is available
only through the `host-x11` authorization (T7). If it is absent, the image
predates the display stack and the launcher keeps today's passthrough
behaviour, still stating the exposure. This keeps every existing lock and
every published base working through the transition and makes the transport
an explicit fact of the manifest rather than a version guess. Publishing a
recipe-8 base is a release step the owner drives; the spike and its e2e
evidence build one locally.

## T7. Host X11 Passthrough Becomes The `host-x11` Authorization

Per D9 as amended: retained, never a default, never recommended by a
project, granted only by the developer's explicit answer with the trade-off
stated at the point of decision. It is a workstation capability node like
`host-browser`, answerable persistently through `config authorize` or once
through `--authorize host-x11 true` on `project run`. When granted on an
image that has the display stack, the launcher binds the host X socket and
cookie exactly as today, writes `display.transport = host-x11` into the plan,
and the disclosure states that the capsule holds the full host session
credential and that the session-credential regression test is waived by
authorization for this run.

## T8. Clipboard

The asymmetric policy from the 2026-08-19 design input (automatic out,
explicit in) falls out of the chosen stack with no code: TigerVNC's Xvnc
publishes both the `CLIPBOARD` and `PRIMARY` selections to the client
(`SendPrimary`, `SendCutText`, defaults on), and noVNC exposes what arrived in
its clipboard panel, from which the developer copies; text going *into* the
capsule is an explicit paste into that panel. Whether Java's `CLIPBOARD` and
the VNC selection line up well enough in practice is a finding for the
ratification day; `autocutsel` is the known remedy if they do not, and it is
not installed until that finding says so.

## T9. The Regression Test

The runtime-image e2e (the one that already proves the supervisor is PID 1)
gains a contained-display run against a locally built recipe-8 base:

- the container is started with **no** `/tmp/.X11-unix` bind, no host
  `XAUTHORITY`, and no `DISPLAY` inherited from the host;
- Xvnc holds no TCP listener; the only listener is websockify on the plan's
  port;
- a WebSocket upgrade with the run's token receives the RFB greeting; one
  with a wrong or missing token is closed;
- the fixture IDE runs with `DISPLAY=:1`, finds the X socket, and its exit
  still ends the session with its own exit code;
- `docker stop` still ends the session in reverse order with exit code 143.

Unit tests cover the plan contract's `display` section, the supervisor's
readiness probe, the entrypoint's child declarations for each transport, the
base label, the launcher's docker arguments (no X11 mounts and a published
port under `contained`; the X11 mounts under `host-x11`), and the
authorization node.

## Recorded Stretch Options, Not Pursued

- **Native-window modes** (Xephyr presumptive, Xpra): see D9.
- **GPU-accelerated streaming**: Selkies (WebRTC with NVENC or VA-API and a
  software x264 fallback) is the credible future occupant of the "optional
  performance upgrade" slot, and a GPU device authorization would be its
  companion. The NVIDIA desktop-in-Docker images confirm the contained
  architecture but are a whole opinionated desktop, need an NVIDIA GPU for
  their value, and exclude the macOS and Windows adopters the browser client
  is meant to win; they are not a drop-in.
- **wayvnc/neatvnc** offers GPU-encoded VNC but is Wayland-only; an X11 Java
  IDE would need XWayland in the middle.

## Spike Record (2026-09-12)

Scratch image `ubuntu:24.04` plus the T6 packages, run as uid 1000:

- `Xvnc :1 -auth … -rfbunixpath … -rfbunixmode 0600 -rfbport -1
  -SecurityTypes None` started, created `/tmp/.X11-unix/X1` and the 0600 RFB
  socket, and `/proc/net/tcp` showed no listener.
- `xdpyinfo` with `XAUTHORITY=/dev/null`: "Authorization required, but no
  authorization protocol specified". With the cookie: 1600x900, X.Org vendor.
- Openbox started on the display (a harmless message about a missing Debian
  menu file).
- `websockify --web /usr/share/novnc --token-plugin TokenFile --token-source
  <dir> 127.0.0.1:6080` with a token line `TOKEN: unix_socket:<socket>`:
  the right token got `HTTP/1.1 101` followed by the frame `RFB 003.008`;
  `token=nope` and no token were closed before any response, with "Token
  'nope' not found" and "Token not present" in websockify's log.
- `GET /vnc.html` returned 200.
