---
description: What a capsule and its coding agents can reach on your computer by default, what stays isolated, and which permissions you can grant or withdraw.
role: containment
weight: 1
updated: 2026-10-30
---
# The boundary

A capsule runs your IDE and coding agents inside a container with an explicit
boundary: your project directory and the checkout's own persistent state cross
by default, while the rest of your computer stays out of reach unless you
record an authorization—and every authorization can be inspected and withdrawn.

## Shared by default

| What crosses | How it works | Why |
|---|---|---|
| Project working tree | Mounted read-write at `/workspace/<slug>` (or the manifest's `project.mount`) | Edits change your real repository files; Git tracks and reverts changes |
| Per-checkout persistent home and component slots | Managed host directories under your [configuration home](../configuration/home.md), mounted into the capsule | Preserves IDE preferences, plugins/extensions, agent sign-ins, and `/opt/xtras` across container replacements ([What persists](../sessions/what-persists.md)) |
| Outbound internet (`bridge` network) | Standard Docker bridge networking: outbound requests work, host `localhost` services stay unreachable, and no capsule ports are exposed except loopback session endpoints | Package managers, language servers, and hosted AI APIs need outbound HTTPS |
| Contained desktop and web console | Loopback-only (`127.0.0.1`) ports with fresh per-run tokens for the desktop tab and (on base recipe `11`+) the read-only/request [web console](../sessions/web-console.md) | Gives you the IDE desktop and session inspector in your browser without exposing your host display session |

Also mounted read-only on startup when present: your active configuration
home's `settings.toml` (channel trust names and resource defaults, containing
no credentials) so `devcapsule home show` works inside the capsule; see [The
configuration home](../configuration/home.md#inside-a-capsule).

## Not shared by default

- **Your host home directory (`$HOME`)**, shell dotfiles, `~/.ssh` keys, cloud
  CLI profiles, browser cookies, and password stores—agents inside the capsule
  cannot read them because they are not mounted.
- **Your host clipboard**—text crosses only when you copy or paste through the
  contained desktop's clipboard panel ([Clipboard and
  browser](../everyday-development/clipboard-and-browser.md)).
- **Your host display server**—the capsule renders on its own virtual display
  and cannot capture your host windows or keystrokes.
- **Your host Docker daemon**—processes inside the capsule cannot start or
  inspect host containers.
- **Your host network namespace**—services listening on `127.0.0.1` on your
  computer are not reachable as `localhost` inside the capsule.
- **Host root privileges**—unprivileged capsules run with `--cap-drop ALL` and
  `no-new-privileges`, and never gain root on your host regardless of what you
  authorize.

## What you can grant

Every permission below is an authorization node visible in `devcapsule project
config show`. A project manifest may recommend host access with a reason, and
only you can grant it; see [Granting and withdrawing
access](granting-and-withdrawing.md) for the commands.

| Authorization | What it opens | Grant it when |
|---|---|---|
| `network host` | Shares your host network namespace: host `localhost` services and capsule ports become one namespace | Your app needs direct access to host-bound services or dynamic local ports ([Services and ports](../your-project/services-and-ports.md)) |
| `docker-daemon host-socket` | Mounts `/var/run/docker.sock` into the capsule | Your build or test suite runs Docker or Testcontainers—treat this as full control over your host Docker daemon |
| `development-sudo true` | Grants passwordless `sudo` **inside the capsule container** (never on your host) | You need to install temporary OS packages inside a session |
| `host-browser true` | Forwards `http://` and `https://` URLs opened inside the capsule to your host browser through a URL-only broker | OAuth sign-ins and external documentation links are more convenient on your host browser |
| `host-x11 true` | Runs the IDE directly on your host X11 display instead of the contained desktop | Almost never—X11 lets clients read keystrokes, clipboard, and windows across your entire host display session; manifests cannot recommend it |
| `vscode-download`, `claude-code-download`, `antigravity-download` (`true`) | Permits DevCapsule to download that vendor's pinned artifact under its license terms (when not already covered by home channel trust) | You selected that IDE or agent and accept its vendor terms ([Vendor software and trust](../configuration/software-approvals.md)) |
| `base-image` (`default` or `<image>`) | Approves the lock's pinned base digest for this checkout or selects an inspected [local base image](../configuration/local-base.md) | Settled once via home `devcapsule-base` trust or per-checkout consent |

Authorizations take effect on the **next** launch (never mutating a running
container), can be granted for a single run without saving (`project run
--authorize ...`), and are never self-granted by a Git repository.

## Why coding agents can run unthrottled here

Inside a default capsule, an autonomous coding agent can edit your repository,
run builds and tests, and update its own per-checkout tool state—while your
personal files, SSH keys, other repositories, and host desktop stay physically
absent from the container, and Git tracks every change to your project tree.
Widening that boundary is always an explicit, per-checkout decision that you
can audit with `devcapsule project config show` and withdraw at any time.
