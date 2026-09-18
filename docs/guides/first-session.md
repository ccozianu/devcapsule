# Your first DevCapsule session

Open a real IDE, run a little JavaScript, then close it and return to your work.
This first exercise needs no AI account, Git checkout, or language installation
on your computer. Already have a project? Install DevCapsule below, then go to
[use your own project](your-project.md).

## Before you start

This guide uses [DevCapsule v0.2.12](https://github.com/ccozianu/devcapsule/releases/tag/v0.2.12)
on **Linux, Intel/AMD 64-bit**, with a web browser and Docker running locally.
The current executable does not run natively on macOS or Windows, or on ARM.
**On Windows, read the [WSL2 setup notes](windows-wsl2.md) before installing.**

Run these commands in your computer's terminal (your Linux terminal on WSL2):

```bash
uname -sm
docker info
docker buildx version
```

Expect `Linux x86_64`, Docker server information, and a Buildx version. If
Docker is missing or reports a connection/permission error, complete
[Docker's installation instructions](https://docs.docker.com/engine/install/)
for your system first. Docker must work as your ordinary user; do not run the
DevCapsule walkthrough with `sudo`.

You also need `curl` and `sha256sum` for the download below. The first launch
downloads a development image and an IDE: allow several GB of disk space and
time for those downloads. Later launches reuse them.

## 1. Get DevCapsule

Paste this block into that same terminal. It checks the download before
installing the executable in your own `~/.local/bin` directory.

```bash
(
  set -eu
  download_dir="$(mktemp -d)"
  cd "$download_dir"
  release_url="https://github.com/ccozianu/devcapsule/releases/download/v0.2.12"
  curl --fail --location --output devcapsule.pex "$release_url/devcapsule.pex"
  curl --fail --location --output devcapsule.pex.sha256 "$release_url/devcapsule.pex.sha256"
  sha256sum --check devcapsule.pex.sha256
  mkdir -p "$HOME/.local/bin"
  install -m 0755 devcapsule.pex "$HOME/.local/bin/devcapsule"
)
```

You should see `devcapsule.pex: OK`. If the block reports an error, stop there
and retry the failed download; do not continue with an unverified file.

```bash
~/.local/bin/devcapsule version
```

Expect `v0.2.12`. The commands below use the full executable path, so they work
even if `~/.local/bin` is not on your shell's search path. No Python, pip, or
DevCapsule source checkout is needed.

## 2. Make a first workspace

Still in your computer's terminal:

```bash
mkdir -p ~/hello-devcapsule
cd ~/hello-devcapsule
~/.local/bin/devcapsule project init --need frontend-ide --need node
```

This selects VSCodium, a VS Code-family IDE, and Node.js. Initialization asks
for the decisions below; here is what to answer for this exercise:

| Prompt | Answer |
|---|---|
| Project creator | Your email address or project URL. This identifies the project; it is not a sign-in. |
| Select the default agent (`antigravity-agent`)? | Type `no` for this first exercise. You can [add an agent afterward](your-project.md#add-a-coding-agent). |
| Recommend `docker-daemon`, `network`, `development-sudo`, or `host-browser`? | Press Enter at each prompt to keep `none`. The exercise needs none of these extra host permissions. |
| Authorize this checkout to execute the base image? | Press Enter to accept the displayed DevCapsule image if you want to proceed. |

In v0.2.12 the base prompt still says `v0.2.12-rc5`; its pinned image is the
same base shipped with v0.2.12. That label does not mean you downloaded an RC.

Success ends with `Project initialized; 'devcapsule project run' starts it.`
DevCapsule has written `.devcapsule/` in this folder and saved your local
choices separately. Initialization is a one-time step for this checkout.

## 3. Open the IDE

```bash
~/.local/bin/devcapsule project run
```

Keep this terminal open. The first run downloads and assembles the tools; build
output is normal. When ready, DevCapsule prints a `http://127.0.0.1:…/vnc.html?…`
URL and tries to open it in your browser. If no tab opens, copy the **whole URL**
from the terminal into your browser on this computer.

You should see VSCodium with `hello-devcapsule` in its Explorer. This is the
capsule's own desktop inside a browser tab. Your host desktop is not shared.
The URL grants access to this session; keep it private and keep the terminal
output so you can reopen the tab.

The project folder is shared read/write with the capsule: edits here really
change your files on disk. Other host access remains subject to your choices.

## 4. Run something

Inside VSCodium:

1. If the top banner says **Restricted Mode**, click **Manage**, then trust
   this folder. You just created it for this exercise.
2. In the Explorer, right-click `HELLO-DEVCAPSULE`, choose **New File**, and
   name it `hello.js`.
3. Type the line below and save it using **File → Save**:

   ```javascript
   console.log("Hello, DevCapsule!");
   ```

4. Choose **Terminal → New Terminal** inside the IDE, then run:

   ```bash
   node hello.js
   ```

You should see **`Hello, DevCapsule!`**. Node ran inside the capsule; you did
not need to install it on your computer. Change the greeting, save, and run it
again to make it yours.

For pasting longer text from your computer, open noVNC's sidebar at the left
edge and use its clipboard panel, then paste inside the IDE. Your host
clipboard is not automatically shared.

## 5. Stop and come back

Save your file, then choose **File → Exit** inside VSCodium to end the
session. Wait for the launcher terminal to return to its prompt. Later, even
from a new terminal:

```bash
cd ~/hello-devcapsule
~/.local/bin/devcapsule project run
```

Open the new URL, open `hello.js`, and run `node hello.js` in the IDE terminal
again. Your saved greeting and IDE state persist; running processes restart.
You do not need to initialize again.

Closing just the browser tab leaves the capsule running. Reopen that run's
printed URL to return. Each new run gets a new URL; a second `project run`
cannot recover the URL of an already-running session yet.

**Next: [use your own project and add a coding agent](your-project.md).**

## If something gets in the way

| What you see | What to do |
|---|---|
| Docker connection, permissions, or Buildx error | Recheck the three prerequisite commands in the same terminal. On Windows, check [WSL integration](windows-wsl2.md). |
| `already fully initialized` | Initialization succeeded earlier. Use `project run`. |
| `Local resolution is stale` or missing | From the project folder, run `~/.local/bin/devcapsule project config resolve`, then retry `project run`. |
| Download/build failure | Check the reported URL, internet connection and available disk space, then retry `project run`. Keep the specific error if asking for help. |
| No browser tab | Open the full printed URL manually on the computer running Docker. |
| Escape leaves fullscreen instead of reaching the editor | Exit noVNC's fullscreen mode. Use the browser menu's fullscreen option instead. |
| `KeyboardInterrupt` after pressing Ctrl+C in the launcher | v0.2.12 can print a traceback when interrupted. Prefer **File → Exit** inside the IDE for an ordinary stop. |
| A shortcut closes the tab | Some shortcuts belong to the browser. Reopen the printed URL and use the IDE menus. |

Still stuck? [Open an issue](https://github.com/ccozianu/devcapsule/issues/new)
with your OS, `devcapsule version` output and the failing command/error. Remove
private project details, access tokens and the desktop URL before posting.
