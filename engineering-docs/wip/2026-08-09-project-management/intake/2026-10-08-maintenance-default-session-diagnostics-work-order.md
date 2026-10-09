# Proposed work order: persistent, bounded diagnostics for capsule sessions

Date: 2026-10-08
From: maintenance, at the product owner's explicit request
To: project-management
Status: proposal for routing and scheduling; no implementation started

## Requested decision

Accept and route a work order for default, persistent diagnostics across the
critical capsule components. This was investigated from the maintenance
checkout, but the supervisor/display scope is associated with the open
`contained-display` workstream in main's workstream list. Its live published
state was absent from `workflow status` during this handoff; project-management
should verify that workstream's current ownership and readiness rather than
assuming it is staffed. The IDE adapters and launcher also participate.
Project-management owns assignment, sequencing and any release target; this
message assigns none and does not switch the sending checkout's workstream.

Acceptance means recording the owner's requested behavior as requirements,
assigning the work and finish criteria, and resolving the policy choices below.
This item contains the complete proposed work order so it can be routed without
waiting for a maintenance PR. Promote it to the normal work-order location and
index it when accepted, according to the repository workflow.

## Problem and evidence

The owner reported that the browser's noVNC session disconnected and could not
reconnect. The owner subsequently stopped the attached container with Ctrl-C.
The provided console log establishes a successful WebSocket-to-Unix-socket
connection and VNC negotiation at 08:25:04 on 2026-10-08, plus transferred
framebuffer updates. It has no identifiable record of the reported disconnect
or unsuccessful reconnect attempts before Ctrl-C. At shutdown, around 08:47:57,
the supervisor reports SIGINT; websockify's traceback runs through its SIGTERM
handler, and the launcher ends with KeyboardInterrupt. XIO and broken-pipe
messages appear during that shutdown. They do not establish the cause of the
earlier failure. The startup warnings and 404 have no demonstrated causal link.

Source inspection, at `4be56a7da060d6605ac41fcdf8da2da25a031ff0`, found:

- `devcapsule-src/devcapsule/container_runtime/display.py`: no explicit debug
  logging configuration for Xvnc or websockify; readiness checks socket
  existence or TCP acceptance.
- `devcapsule-src/devcapsule/container_runtime/supervisor.py`: children inherit
  stdout/stderr; direct-child exit supervision does not diagnose a hang or an
  individual websockify worker's failure.
- `devcapsule-src/devcapsule/display_client.py`: the host readiness watcher
  returns after opening the browser; it is not a continuing health monitor.
- `devcapsule-src/devcapsule/launch/pycharm/_launcher.py`: attached launch uses
  `--rm`, transient tmpfs directories, and no dedicated persistent display log
  capture. Persistent IDE logs already exist and must be incorporated.

This is evidence of an observability gap, not a reproduced root cause. The
exact incident executable/image was not independently inspected. No Docker
experiments or runtime changes were performed. The pasted token-bearing URL
and full console dump are deliberately omitted from this handoff.

## Owner's direction

Replace the prior proposal to require `project run --diagnostics display` for
baseline capture. Logging must be enabled by default for every critical
component, including the X server, desktop/window manager, bridge, IDE and
supervisor, in separate logs in a discoverable log directory. Use the equivalent
of Java WARNING as the baseline severity, with logrotate-style bounded rotation
and compressed older archives before age-based deletion. Prevent excessive disk
use. An optional verbosity override may help a later investigation, but ordinary
failure evidence must not depend on anticipating the failure and restarting with
a special flag.

## Proposed requirements and scope

1. **Persistent session identity and logs.** Allocate a session ID and a private,
   host-backed log directory for each ordinary launch. Print its location and
   expose it through supported project inspection. Record UTC timestamps,
   component identity, PID and session identity consistently. Preserve separate
   streams for the launcher/supervisor, Xvnc, window manager, panel, websockify
   and selected IDE as applicable. Capture startup failures as well as runtime
   output. Record exact launcher/component versions and image identity so a
   future incident can be tied to its inputs. Logs survive browser closure,
   Ctrl-C, IDE exit and automatic container removal; flush during the session,
   not just in an exit handler.

2. **Useful default severity.** Map WARNING-and-higher to each component's actual
   logging interface; do not assume numeric levels are interchangeable. Keep a
   small lifecycle/connection event record even when upstream classifies those
   events as INFO: child start/readiness/exit/signal, connection open/close,
   close reason when available, failed handshake/authentication and explicit
   session-end request. These are necessary to reconstruct this incident class.
   Plain stdout/stderr without reliable severity metadata must be retained under
   the same size budget rather than discarded by guessing from text. Integrate
   existing IDE-native logs and rotation rather than creating an unmanaged
   duplicate or lowering their useful existing detail without review.

3. **Rotation with an enforceable storage budget.** Rotate active files by size;
   compress closed segments (gzip or a suitable documented equivalent), retain a
   bounded number and maximum age, and delete oldest eligible archives when the
   aggregate budget requires it, even before that age. Enforce a budget across
   sessions, not just per component: otherwise frequent launches accumulate
   indefinitely. Account for active files and compression scratch space; specify
   and test any transient overshoot. One initial policy for review is 10 MiB per
   segment, five archives per component, seven days maximum age and a 256 MiB
   aggregate budget per checkout. These numbers are proposed, not owner-decided.
   Publish the actual retention rules and report pruning or dropped records.

   Choose logrotate or an equivalent streaming writer based on the actual
   process ownership and reopen behavior. A daily timer alone is insufficient
   for a size bound during a noisy session. Avoid the copytruncate loss window;
   do not rename files while leaving producers writing indefinitely to an old
   descriptor. Compression and logging must not deadlock or indefinitely block
   the supervised children. Permission errors, disk full and logger failure
   need bounded, visible behavior that preserves session control.

4. **Live diagnostic snapshot and export.** Provide a supported command (name
   to be chosen; `project diagnose` was suggested) that can run from another
   launcher terminal while the session is broken, without restarting it. Save
   process/worker state, resource usage and limits, available cgroup/OOM
   evidence, relevant sockets and bounded probes of HTTP, WebSocket and RFB
   separately. Socket existence and TCP acceptance must not be presented as
   end-to-end health. Time out every probe; identify unavailable evidence and
   label diagnostic connections so they are distinguishable from user attempts.
   Include retained logs and a sanitized manifest in an export. Do not rely on
   querying Docker only after `--rm` has removed the container. Capture relevant
   state/events while it exists. Any continuing sampling must have a defined
   low overhead and retention bound.

5. **Browser evidence.** Server-side files cannot capture every browser failure.
   Provide a documented, usable way to retain/export noVNC connection and
   reconnect events, WebSocket close code/reason when available, and JavaScript
   errors. The export must remain usable when the bridge is unreachable. A
   browser developer-tools procedure is an acceptable initial slice if its
   manual nature and coverage limits are explicit; automatic client capture is
   a separate design choice. Do not claim browser logs are included in the
   host-side bundle unless collection is actually implemented.

6. **Honest shutdown and handling of sensitive content.** Persist an explicit
   shutdown boundary and final result. Handle expected launcher Ctrl-C without
   an uncaught KeyboardInterrupt traceback; do not hide unexpected errors.
   Redact token-bearing URLs and known credentials in generated diagnostics and
   exports. Keep local logs private and define treatment of IDE-native logs,
   which can include project content; do not promise universal redaction of
   arbitrary application output. No desktop, keystroke or clipboard payload
   recording by default. No additional host-access authorization is implied.

## Finish criteria and validation

- An ordinary launch without diagnostic flags produces discoverable separate
  logs and the correlation manifest, with the documented severity mapping.
- Evidence remains readable after normal IDE exit, Ctrl-C and container removal.
  Abrupt termination retains already-written evidence and records limitations.
- A bounded fault-injection exercise covers browser disconnect/reconnect,
  websockify connection-worker failure, bridge hang and Xvnc exit. The resulting
  artifacts distinguish observed failures from later intentional shutdown and
  expose what remains unknown. This does not claim to reproduce the owner's
  original incident.
- A controlled high-volume writer and repeated launches demonstrate rotation,
  archive readability, compression, age/count cleanup and the aggregate cap,
  including concurrent writers and logger/disk failure behavior. Specify actual
  tolerances rather than claiming a perfectly instantaneous disk bound.
- Export checks cover token redaction, permissions and missing-browser-evidence
  reporting. Bounded capture does not make a hung session harder to stop.
- Follow the required repository gate for implementation and targeted runtime
  acceptance using a fresh workspace under the existing E2E rules. Do not run a
  broad performance or infrastructure campaign absent a concrete concern.
- Update current user documentation with log locations, retention, snapshot and
  browser-evidence instructions; record implementation and acceptance evidence.

## Decisions retained for the receiving workstream and owner

Confirm scope/ownership and scheduling; choose the exact storage limits and
their configuration interface; decide the browser-capture slice; choose the
rotation implementation and native-IDE integration; define any periodic health
sampling. Default persistent component logs, bounded rotation/compression and
the WARNING baseline are the owner's direction. The lifecycle exception,
numeric retention proposal and detailed snapshot/export design above are
engineering recommendations for review. Repair of the original disconnect
remains separate: its cause is still unknown. Automatic restart is not proposed
as a substitute for preserving evidence.

## Upstream references checked during analysis

- [noVNC troubleshooting](https://github.com/novnc/noVNC/wiki/Troubleshooting):
  browser console logging and `logging=debug`.
- [websockify](https://github.com/novnc/websockify): verbose/file logging support.
- [Xvnc](https://tigervnc.org/doc/Xvnc.html): component-specific `-Log` settings.
- [Docker run](https://docs.docker.com/reference/cli/docker/container/run/#clean-up---rm):
  automatic container removal and loss of the retained container filesystem.

Check options against the exact packaged component versions before implementing.
