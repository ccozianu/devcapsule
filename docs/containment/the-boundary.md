---
description: Exactly what a capsule and the agents inside it can reach on your computer by default, what they cannot, and the few things you can choose to grant.
role: containment
weight: 1
updated: 2026-09-28
---
# The boundary

A capsule is a container that runs your IDE and your agents. This page says
what crosses its boundary. The short version: your project folder and the
capsule's own persistent state cross; nothing else does unless you grant it,
and every grant is a recorded decision you can withdraw.

## Shared by default

| What | How | Why |
|---|---|---|
| The project folder | Mounted read/write at the same content | That is the work; edits are real, and Git is your undo |
| The capsule's persistent home and state | DevCapsule-managed directories on your computer, mounted into the capsule | So IDE settings, extensions, agent sign-ins and installed extras survive; see [What persists](../sessions/what-persists.md) |
| The internet, through Docker's ordinary bridge network | Outbound connections work; nothing on the host network is exposed to the capsule, and nothing in the capsule is exposed to the host except the desktop URL on loopback | Agents and package managers need it |
| The capsule's desktop | A browser tab on your computer, over a per-run loopback port with a per-run token | Nothing of your computer's display session enters the capsule |

## Not shared by default

- Your home directory, your shell configuration, your SSH keys, your cloud
  credentials, your password stores. An agent inside the capsule cannot
  read them because they are not there.
- Your computer's clipboard. Text crosses only when you paste it into the
  desktop tab's clipboard panel or copy it out of it.
- Your display session. The capsule has its own; it cannot see your windows
  or your keystrokes.
- Your Docker daemon. The capsule cannot start containers on your computer.
- Your host network namespace. Services on your computer are not reachable
  as `localhost` from the capsule.
- Root on your computer. A capsule never has it, whatever you grant.

## What you can grant

Each of these is an authorization: a project may recommend it, only you can
grant it, and `project config show` tells you which are pending. The
[granting and withdrawing](granting-and-withdrawing.md) page has the
commands.

| Authorization | What it opens | Grant it when |
|---|---|---|
| `network host` | The capsule shares your computer's network namespace: your local services become its `localhost`, and its ports become yours | The project talks to services running on your computer |
| `docker-daemon host-socket` | The capsule can control your Docker daemon | The project builds or runs containers; understand that this is control over the host daemon |
| `development-sudo true` | The capsule's user may become root **inside the capsule**, never on your computer | Installing system packages in the capsule |
| `host-browser true` | Links opened inside the capsule open in your computer's browser | Sign-in flows and previews are more convenient; nothing else changes |
| `host-x11 true` | The capsule uses your computer's display session instead of its own desktop | Almost never. It lets capsule programs see and inject input across your whole session; the launch says so. No project can recommend it |
| `<agent>-download true` | DevCapsule may download that vendor's agent under its terms | You selected the agent and accept the vendor's terms |
| `base-image <digest>` | This checkout may run that exact base image | Always asked once; a changed recommendation asks again |

A grant applies to the next launch, not to a running capsule. A grant can
also be given for one run only, without recording it. And a project cannot
grant itself anything: a recommendation committed in the repository is a
request to you, shown with its reason, and refused by default.

## What this means for an agent

An agent inside a capsule works without approvals because the worst it can
do is change your project, which Git protects, and its own state. That is
the boundary the *YOLO mode* on the landing page refers to. Widening it is
your decision, made per checkout, visible in one listing, and reversible.
