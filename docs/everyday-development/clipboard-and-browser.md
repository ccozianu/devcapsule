---
description: How text moves between your computer and the capsule's desktop, how keys and fullscreen behave in the browser tab, and how links open.
weight: 5
updated: 2026-09-28
---
# Clipboard, keys and browser

The capsule's desktop is a web page. That keeps your computer's display
session out of the capsule, and it changes three everyday habits.

## Clipboard

The capsule cannot see your computer's clipboard; nothing crosses without a
gesture from you. Open the sidebar at the left edge of the desktop tab. Text
copied inside the capsule appears in its clipboard box, from which you copy
it on your side; text going into the capsule is pasted into that box and is
then available to the IDE. This is more work than Ctrl+C and Ctrl+V and it
is a known place for improvement; the intended route is a browser feature
that hands a page the clipboard only during your own paste, which keeps the
boundary.

## Keys, Escape and fullscreen

In a normal tab, every key the browser does not reserve reaches the
capsule, Escape included. Do not use the fullscreen button on the desktop's
sidebar: browsers leave that kind of fullscreen on Escape, so Escape never
reaches your editor. Use the browser's own fullscreen instead: focus the
address bar with Ctrl+L, press F11, click back into the desktop. Shortcuts
the browser owns, such as Ctrl+W, Ctrl+T and Alt+Tab, never reach the
capsule; closing the tab by accident does not end the session, and the
printed URL reopens it.

## The desktop

One virtual desktop, a panel at the bottom with a button per window and a
clock, the IDE maximized and following the browser window. Any window,
including a dialog behind the IDE, is one click away on the panel, and a
right click on the empty background lists them. Nothing can disappear.

## Links

A link opened inside the capsule has no browser to open in, unless you
grant `host-browser`, which lets the capsule ask your computer's browser to
open a URL and nothing more; see [Granting and withdrawing](../containment/granting-and-withdrawing.md).
Without it, copy the URL out through the clipboard box.
