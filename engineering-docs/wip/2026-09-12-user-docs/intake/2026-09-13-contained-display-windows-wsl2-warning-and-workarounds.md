# Intake: Warn Windows Adopters About WSL2, With The Owner's Workarounds

Delivered 2026-09-13 by `contained-display`, at the product owner's
direction after testing the v0.2.12-rc4 candidate on Windows: "I did not
know the situation with WSL2 being so flaky has stayed as bad as it is now.
We must warn our users."

## What Is Being Handed Over

The owner worked through the WSL2 problems and their workarounds in a
conversation with Gemini and wants that material placed prominently in the
documentation for Windows adopters:

```text
https://share.gemini.google/uwp9NGLIBYMo
```

That is the whole conversation, in the owner's words, and the source of
truth for the symptoms, the settings and commands that fixed them, the
versions involved, and what still does not work. Note that the page is a
signed-in Gemini application: fetched without a Google session it returns
only the application shell, so an agent cannot read it. Ask the owner for a
pasted copy or an export if the link does not open for you.

## What The Owner Wants

- A **prominent** warning for Windows adopters — before they install
  anything — that running DevCapsule on Windows means WSL2, and that WSL2
  has sharp edges the guide addresses. The root README landing page is the
  natural place for the call-out, with a dedicated guide holding the
  detail (for example `docs/guides/windows-wsl2.md`; root `docs/` is the
  current user-facing documentation).
- The guide written from the conversation: symptoms as they were met, the
  exact workarounds, versions, and the honest list of what remains broken.
  Sanitized of anything personal. Later entries correct; earlier ones are
  not rewritten.
- The first-session tutorial (your earlier intake from `contained-display`,
  2026-09-13) inheriting the warning at the Windows branch of its
  prerequisites step.

## Context From `contained-display`

- The contained display's host-facing surface is one loopback TCP port
  published by Docker; everything else is inside the container, so WSL2
  issues are about Docker Desktop, localhost forwarding, DNS, and opening
  a browser from the distro, not about the display itself (design note
  T5; handoff TODO *WSL2 browser opener*).
- On WSL2 the launcher prints the display URL rather than opening it,
  because the distro has neither `xdg-open` nor `BROWSER`; `BROWSER=wslview`
  from the `wslu` package makes it open in the Windows browser. Automatic
  detection is a recorded TODO on `contained-display`.
- During the v0.2.12 candidates the contained desktop is the opt-in
  (`project run --authorize host-x11 false`); at the release it becomes the
  default with no answer needed.

## What Accepting Would Mean

Owning the Windows guide and the landing-page call-out, sourced from the
owner's conversation, and keeping them current as the WSL2 situation
changes. `contained-display` will fold whatever the conversation says about
opening URLs from WSL2 into its opener TODO, and nothing there blocks you.
