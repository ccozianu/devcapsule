# Observation: JetBrains Runtime Disables Alpha Compositing On X11

Date opened: 2026-08-03

Status: observed in external dogfood; low-priority review, not currently a V1
blocker

Requirements: R-ENV-001, R-DEV-001

## Observation

The v021-backed PyCharm 2026.2.0.1 launch printed:

```text
[JetBrains Runtime] Detected slow X11, switched off alpha compositing of images.
Control with -Dremote.x11.workaround={true|false|auto}.
```

No specific rendering defect, crash, or unacceptable latency was reported with
the warning. JetBrains Runtime is applying its own `auto` performance heuristic
and selecting reduced image compositing for the detected X11 connection.

## Current Assessment

This is not yet evidence of a DevCapsule bug. Containerized X11, software Mesa
rendering, and the deliberate no-MIT-SHM compatibility setting can reasonably
look like a slow or remote display to the runtime. The fallback may improve
responsiveness at the cost of transparency or other image-compositing fidelity.

V1 should retain JetBrains' `auto` behavior unless manual comparison shows a
material visual or performance problem. Forcing either value merely to remove
the warning would replace a vendor heuristic with an unvalidated product
default.

## Later Review

1. Capture the effective display, graphics, MIT-SHM, and software-rendering
   configuration used by the normal project launcher.
2. Compare `auto`, `true`, and `false` on the same supported host, recording
   startup time, UI responsiveness, CPU use, and visible rendering differences.
3. Exercise transparent icons/images, popups, editor overlays, Markdown/SVG
   preview, and other surfaces where alpha compositing is observable.
4. Confirm the property's precise JetBrains Runtime semantics for the pinned
   JBR version before setting it through component metadata.
5. If no user-visible defect exists, retain `auto`, document the console
   message as benign, and close this observation without a code change.

## Escalation And Close Criteria

Promote this to a V1 defect only if external dogfood shows corrupted or missing
transparency, unreadable UI, severe latency, excessive CPU use, or another
repeatable user-facing impact.

Close after a controlled comparison establishes the appropriate supported
default—or confirms that JetBrains' `auto` behavior is acceptable—and records
the manual evidence. Reopen if a JetBrains Runtime upgrade changes the warning
or produces a visible regression.
