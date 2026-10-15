---
description: What to do when the first session stops at Docker, initialization, the download, the browser or the keyboard.
weight: 1
updated: 2026-09-28
---
# First-session troubleshooting

| What you see | What to do |
|---|---|
| Docker connection, permission or Buildx error | Recheck the three [prerequisite commands](../getting-started/install.md#check-your-computer) in the same terminal. On Windows, check [WSL integration](../platforms/windows-wsl2.md). |
| `unknown configuration name`, with a suggestion | You mistyped an option to `init`; nothing was written. Run it again with the suggested name. |
| `already fully initialized` | Initialization succeeded earlier. Use `project run`. |
| `Local resolution is stale`, or missing | From the project folder, `~/.local/bin/devcapsule project config resolve`, then `project run`. If it names pending decisions, see [Project versus personal](../configuration/project-versus-personal.md#when-the-project-changes). |
| Download or build failure | Check the reported URL, your connection and free disk space, then retry `project run`. Keep the exact error if you ask for help. |
| No browser tab | Open the full printed URL yourself, on the computer running Docker. |
| Escape leaves fullscreen instead of reaching the editor | You used the desktop sidebar's fullscreen button. Use the browser's own fullscreen; see [Clipboard, keys and browser](../everyday-development/clipboard-and-browser.md). |
| A traceback ending in `KeyboardInterrupt` after Ctrl+C | The capsule did stop. Prefer **File → Exit** in the IDE for an ordinary stop. |
| A shortcut closed the tab | The browser owns some shortcuts. Reopen the printed URL; use the IDE menus. |

Still stuck? [Open an issue](https://github.com/ccozianu/devcapsule/issues/new)
with your OS, the output of `devcapsule version`, and the failing command
and error. Remove private project details, access tokens and the desktop
URL before posting.
