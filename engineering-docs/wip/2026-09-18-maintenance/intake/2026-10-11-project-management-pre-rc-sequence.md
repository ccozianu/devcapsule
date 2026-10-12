# 0.3.0 sequence: consent and forced configuration before RC work

Date: 2026-10-11
From: project-management, at the owner's direction
To: component-upgrades, maintenance

## Decision

The planning session's purpose is to shorten the road to a 0.3.0 release
candidate. The owner directed that the two substantial implementations be
handled first: consent/vendor trust (#1, component-upgrades), and
forced-configuration preview and launch (#6, maintenance). The remaining
release work can be handled during the RC cycle. Project-management is now
paused at the owner's direction; this message preserves the sequence.

Accepting means reflect this sequence in the owning workstream's plan. It
does not authorize a release cut, choose the release driver, waive the eleven
user-docs decision gate, or remove release acceptance obligations.

## Scope clarified during planning

- Network authorization is a bounded bug fix: make project run --authorize
  network host work without a project recommendation, also permit the saved
  checkout choice, and retain bridge as the default. No raw --network flag
  or new networking subsystem is requested.
- Terminal cleanup means stop presenting harmless desktop diagnostics as a
  broken launch and make Ctrl+C stop without a Python traceback. Check what
  the new logging work already covers before counting remaining implementation.
- The normal image-build optimization is delivered. The remaining image work
  is reuse of installed Docker content with an empty launcher cache, plus
  safe cleanup of obsolete images and caches.
- Diagnostics logging and rotation have merged. Snapshot/export, browser
  evidence and any remaining acceptance are the work to assess.
- Ecosystem bootstrap is moved to 0.9 by the separate delivered decision.

The agent cautioned that the remaining diagnostics and image cleanup/reuse
could still become substantial. Their precise RC scope and any deferral remain
open with the owner; no deferral was decided. Do not use that caution to add
new pre-RC gates or silently drop previously accepted 0.3.0 work.

## Evidence

Owner planning conversation on 2026-10-11; recorded in the project-management
CURRENT-STATUS.md and 2026-09-27-0216-release-planning.md at this checkpoint.
Existing consent decisions D-0011 through D-0013 and the accepted maintenance
configuration requirement remain the implementation contracts.
