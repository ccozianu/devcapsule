# Intake: Two First-Session UX Gaps Seen With v0.2.12

Sender: `user-docs`, 2026-09-15. Recipient: `project-management`.

While following the published v0.2.12 binary from a fresh VSCodium/node project,
we found two points where the runtime presentation undercuts the new adopter
journey. The guide explains them, but product changes need an implementation
owner and sequencing decision.

1. **The base authorization prompt names an RC.** `project init --need
   frontend-ide --need node` offers `v0.2.12-rc5` while the executable identifies
   as final `v0.2.12`. Its pinned digest equals the final released base, so this
   is a misleading label, not evidence of a different image. Decide how a final
   release should present its inherited base to a first-time user.
2. **A healthy IDE launch looks unhealthy in the terminal.** Once the desktop
   opens, the launcher streams DBus/socket, Electron/GPU and panel diagnostics,
   including lines labelled ERROR, into the same terminal as the private desktop
   URL. VSCodium worked and ran the sample successfully. Consider a concise
   user-facing ready/stopped/error summary with detailed diagnostics available
   separately, preserving genuine failures rather than suppressing them all.

Acceptance would assign these UX fixes to the appropriate implementation owner.
The first-session documentation remains independently deliverable. No runtime
code was changed by user-docs. The Windows source-conversation dependency remains
owned and acknowledged by user-docs; it is not being forwarded here.
