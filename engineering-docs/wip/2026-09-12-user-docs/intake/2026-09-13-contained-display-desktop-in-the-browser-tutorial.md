# Intake: The Capsule's Desktop In The Browser — Material For A Short Tutorial

Delivered 2026-09-13 by `contained-display`, at the product owner's
direction after smoking the contained display from the dogfood capsule:
"put this in a note to be integrated into a short tutorial".

## What Is Being Handed Over

Adopter-facing facts about the new default display, written so they can be
folded into the first-session guide (or a short companion tutorial) without
re-deriving them. Nothing here is a design decision for `user-docs` to make;
the decisions are recorded in `contained-display`'s
[design note](../../2026-08-19-contained-display/display-transport-design.md).

## The Facts, In The Order A New Adopter Meets Them

1. **What they see.** From v0.2.12, `devcapsule project run` no longer puts
   the IDE on the host's own X session. The capsule runs its **own desktop**
   and the launcher prints a URL like
   `http://127.0.0.1:PORT/vnc.html?...token=...`, then opens it in the
   default browser once the capsule is ready. The IDE appears inside that
   browser tab. Nothing needs installing on the host beyond Docker and a
   browser; macOS and Windows adopters need neither XQuartz nor WSLg.
2. **Why.** Earlier releases handed the container the host's X session
   credential, which let anything inside capture keystrokes and windows
   across the whole desktop. The contained desktop closes that: no host X
   socket, credential or `DISPLAY` crosses into the container. This is worth
   one sentence in the tutorial because it is the product's central claim
   made visible.
3. **The URL is private to this run.** The port is on loopback only and
   the token in the URL is generated per run; both change every launch.
   Print-outs and shell history therefore hold nothing reusable.
4. **Closing the tab does not stop anything.** The IDE keeps running;
   reopening the printed URL resumes exactly where the adopter left off.
   The session ends when the IDE is closed or the launcher is interrupted
   (Ctrl-C) or `docker stop` is used.
5. **Resizing.** The desktop follows the browser window size.
6. **Keys, and Escape in particular** (owner-verified 2026-09-13):
   - In a normal tab every key the browser does not reserve reaches the
     IDE, Escape included. Terminal and vim-style editing work as expected.
   - **Do not use the fullscreen button on noVNC's side bar.** It requests
     the page kind of fullscreen, which every browser leaves on Escape, so
     Escape never reaches the editor.
   - To go fullscreen, use the **browser's** fullscreen: give keyboard
     focus to the address bar first (Ctrl+L), press F11, then click back
     into the desktop. Leave it the same way (Ctrl+L, F11). The focus step
     is needed because noVNC forwards F11 to the capsule while the desktop
     has focus. The browser menu's fullscreen entry works too.
   - Shortcuts the browser itself owns (Ctrl+W, Ctrl+T, Ctrl+N, Ctrl+Tab,
     Alt+Tab) never reach the capsule in any mode. Ctrl+W closes the tab;
     see point 4 for why that is harmless.
7. **Clipboard.** Text copied inside the capsule shows up in noVNC's
   clipboard panel on the side bar, from which it can be copied; text going
   *into* the capsule is pasted into that panel. (Behaviour with the
   JetBrains IDE is still being confirmed on the ratification day; word
   this cautiously or leave it out until then.)
8. **Keeping the old way.** Linux adopters who want the IDE as a native
   window on their own desktop can opt in with
   `devcapsule project run --authorize host-x11 true` (or persistently with
   `config authorize host-x11 true`). The launch states the trade-off: the
   capsule then holds the host session credential. This is never a default
   and no project can recommend it. Images built before base recipe 8 have
   no display stack and keep using this path automatically.
9. **Known limits, stated plainly.** Docker network mode `none` cannot carry
   the display and is refused with the alternatives named. A second
   `project run` while a capsule is already running cannot recover the
   first run's URL yet; keep the launcher's output.

## Where The Same Facts Already Live

The developer-oriented `devcapsule-src/README.md` has a *Display* subsection
with the same content in contributor language; treat it as the source to
check commands against, not as prose to copy.

## What Accepting Would Mean

Folding points 1, 3, 4, 6 and 8 into the first-session guide's launch and
resume steps (points 2, 5, 7 and 9 as short asides), and checking the
commands against the v0.2.12 release once it exists. Nothing blocks on it.
