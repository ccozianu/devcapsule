# Bug: X11 Passthrough Grants The Container A Full Host Session Credential

Date opened: 2026-08-16

Status: open

Requirements: R-SCOPE-001, R-PRODUCT-002, R-DOCKER-001

## Symptom

The PyCharm launcher shares the host X session with the container by binding
`/tmp/.X11-unix` and supplying an X authority cookie. The cookie supplied is the
developer's existing **trusted** cookie, so the container receives full-privilege
access to the entire host desktop session rather than to its own display only.

A client holding a trusted X11 cookie can, on the host session:

- read every keystroke typed in any window, including passwords typed into
  unrelated applications;
- capture the contents of any window on the display;
- inject synthetic keyboard and pointer events through XTEST; and
- read and overwrite the clipboard used by other applications.

This is a boundary the product otherwise declares, inspects, and verifies.

## Evidence

`devcapsule/configurations/pycharm/_launcher.py`:

- `write_xauthority` runs `xauth nlist "$DISPLAY"` and re-merges the resulting
  entries with the address family rewritten to the wildcard `ffff`. These are
  the developer's live trusted credentials, not a display-scoped or untrusted
  cookie.
- The launcher binds `type=bind,src=/tmp/.X11-unix,dst=/tmp/.X11-unix,ro` and
  the generated cookie at `/tmp/.docker.xauth`, then sets
  `XAUTHORITY=/tmp/.docker.xauth` in the container environment.
- When no cookie can be copied, the warning advises running
  `xhost +SI:localuser:<user>`, which also grants full session access.
- The launcher refuses to start without `DISPLAY`, so this path is not optional
  for GUI use.

The `,ro` flag on the socket-directory bind does not constrain this. Read-only
applies to directory contents, not to the ability to connect to the socket and
speak the X protocol.

## Why This Matters More Than Usual Here

DevCapsule's central claim is an explicit, inspectable host boundary, and the
Stage 6 inspector verifies mounts by set equality precisely so that no
unplanned access exists. That inspector reports this mount as planned and
correct, because it is planned. Nothing in the plan, the inspection output, or
the user documentation states that one of those planned mounts carries a
credential to the developer's whole desktop.

An adopter reading the current documentation would reasonably conclude that a
containerized agent cannot observe activity outside its container. On an X11
launch, it can.

## Contributing Factor: No Desktop Integration Either

The same design gives the container pixels and nothing else. There is no
`xdg-open` handler, so link clicks from the IDE go nowhere; clipboard behavior
depends on X selection negotiation and is intermittently unreliable with the
JetBrains runtime; and there are no file associations or notifications. The
security exposure and the poor desktop integration are the same root cause.

## Expected Behaviour

- A containerized GUI must not receive a credential that grants access beyond
  its own display surface.
- Any residual host-session exposure must be stated in the runtime plan, in
  inspection output, and in user documentation, so that it is an explicit
  authorization rather than an implicit consequence of running a GUI.
- If X11 passthrough is retained in any form, it is an opt-in path with a
  documented security trade-off, not the default.

## Candidate Resolutions

Recorded for the display-transport decision rather than decided here.

- A contained display server inside the capsule, such as Xvnc plus a window
  manager reached over VNC or noVNC. Nothing host-side is shared, so the
  exposure closes completely. This is the current product direction; see the
  [V1 scope ledger](../../wip/2026-08-09-project-management/v1-scope-ledger.md).
- Xpra in seamless mode, which also avoids sharing the host session while
  presenting individual application windows.
- X11 with the SECURITY extension and untrusted cookies. Recorded for
  completeness; untrusted cookies are known to break JetBrains applications in
  practice and are not treated as a viable fix.

## Notes

The `xdg-open` forwarding shim that fixes link clicking is required under every
candidate transport and can be implemented independently of this bug.
