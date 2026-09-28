---
description: Open a real IDE in a capsule, run a small program, then close it and come back, in a quarter of an hour and with no AI account.
role: getting-started
aliases:
  - /docs/guides/first-session/
weight: 2
updated: 2026-09-28
---
# Your first session

Open a real IDE, run a little JavaScript, then close it and return to your
work. This first exercise needs no AI account, no Git checkout and no
language installed on your computer. Install DevCapsule first:
[Install](install.md). Already have a project? Skip to
[an existing repository](../your-project/existing-repository.md).

## 1. Make a first workspace

In your computer's terminal:

```bash
mkdir -p ~/hello-devcapsule
cd ~/hello-devcapsule
~/.local/bin/devcapsule project init --need frontend-ide --need node
```

This selects VSCodium, a VS Code-family IDE, and Node.js. Initialization asks
for a few decisions. For this exercise:

| Prompt | Answer |
|---|---|
| Project creator | Your email address or a project URL. It identifies the project; it is not a sign-in. |
| Select the default agent? | `no` for now. [Adding an agent](../working-with-ai/choose-an-agent.md) takes one command later. |
| Recommend `docker-daemon`, `network`, `development-sudo` or `host-browser`? | Press Enter at each to keep `none`. The exercise needs no extra host access; [Containment](../containment/the-boundary.md) explains each. |
| Authorize this checkout to execute the base image? | Press Enter to accept the displayed image. |

The base image is named after the build that produced it, so the prompt can
show an older build's release-candidate label. It is the same base that
ships with this version, not a candidate download. If you mistype an option
name, `init` says so before asking anything and suggests the right one; you
lose no answers.

Success ends with `Project initialized; 'devcapsule project run' starts it.`
DevCapsule has written `.devcapsule/` in this folder, the part that belongs
to the project, and saved your local choices separately. Initialization is a
one-time step for this checkout.

## 2. Open the IDE

```bash
~/.local/bin/devcapsule project run
```

Keep this terminal open. The first run downloads and assembles the tools;
build output is normal. When ready, DevCapsule prints a
`http://127.0.0.1:…/vnc.html?…` URL and tries to open it in your browser. If
no tab opens, copy the **whole URL** from the terminal into a browser on this
computer.

You see VSCodium with `hello-devcapsule` in its Explorer. This is the
capsule's own desktop in a browser tab; your computer's desktop is not
shared. The URL grants access to this session: keep it private, and keep the
terminal output so you can reopen the tab.

The project folder is shared read/write with the capsule: edits there really
change your files. Everything else on your computer stays out of reach unless
you grant it.

## 3. Run something

Inside VSCodium:

1. If the top banner says **Restricted Mode**, click **Manage** and trust
   this folder. You just created it.
2. In the Explorer, right-click `HELLO-DEVCAPSULE`, choose **New File**, and
   name it `hello.js`.
3. Type the line below and save with **File → Save**:

   ```javascript
   console.log("Hello, DevCapsule!");
   ```

4. Choose **Terminal → New Terminal** inside the IDE and run:

   ```bash
   node hello.js
   ```

You see **`Hello, DevCapsule!`**. Node ran inside the capsule; nothing was
installed on your computer. Change the greeting, save, run it again.

To paste longer text from your computer, open the sidebar at the left edge
of the desktop tab and use its clipboard panel, then paste inside the IDE.
Your computer's clipboard is not shared automatically; see
[Clipboard and browser](../everyday-development/clipboard-and-browser.md).

## 4. Stop, and come back

Save, then choose **File → Exit** inside VSCodium. The launcher terminal
returns to its prompt. Later, from any terminal:

```bash
cd ~/hello-devcapsule
~/.local/bin/devcapsule project run
```

Open the new URL, open `hello.js`, run it again. Your file and your IDE
state are there; running processes restart. You never initialize again.
[Stop and come back](stop-and-come-back.md) has the details, including what
closing the tab does.

**Next: [bring your own project](../your-project/existing-repository.md), or
[add a coding agent](../working-with-ai/choose-an-agent.md).** Something in
the way? [First-session troubleshooting](../troubleshooting/first-session.md).
