---
description: "Every configuration node a checkout can carry, its values, and which command records it: authorizations, declared values and bindings."
weight: 1
updated: 2026-10-28
---
# Configuration nodes

Every recorded choice in a checkout is a node with one name. `project config
show` prints them with the value the next launch uses and its source; the
commands below record them. All are yours, per checkout, outside the
repository. Home trust can cover published bases and vendor downloads;
per-checkout consents also remain supported. See
[Vendor software and trust](../configuration/software-approvals.md).

## Authorizations, `config authorize NAME VALUE [JUSTIFICATION]`

| Node | Values | Effect |
|---|---|---|
| `base-image` | `default` or the lock's exact digest; a local image tag or ID for a local base | Consent to run that image; binds to the image, so a lock change around an unchanged base keeps it |
| `network` | `host`, `bridge`; unanswered defaults to `bridge` | `host` shares the host network namespace; `bridge` denies that access; available on every project |
| `docker-daemon` | `host-socket`, `none` | `host-socket` mounts the host Docker control socket; `none` denies that access |
| `development-sudo` | `true`, `false` | The capsule user may elevate inside the container through a temporary, launcher-owned sudoers policy |
| `host-browser` | `true`, `false` | `xdg-open` in the capsule may ask the host browser to open a URL |
| `host-x11` | `true`, `false` | The host display session is bound into the capsule instead of the contained desktop; never recommended by a project; the contained desktop is the default |
| `claude-code-download`, `antigravity-download` | `true`, `false` | Per-checkout consent to that vendor's agent when its channel is not trusted in this home; `false` denies it even when it is |

`--all-recommended` previews every recommendation and authorizes all only on
`y`. For host access, `project run --authorize NAME VALUE` applies to one launch.
Add `--save` to record it for the checkout.
`config deny NAME` records a denial and `config forget NAME` removes your
answer. `config approve [NAME...|--all]` records new versions of vendor
software you consented to per checkout.

## Values, `config set NAME VALUE`

`memory` and `cpus` are the launcher's own, on every project; the other names
are the ones the project declares in its manifest, validated against the
declared type: `string`, `integer`, `boolean` or `memory-size`. `default`
forgets your answer and follows the project's recommendation and the
home's default again. Values with runtime effects today:

| Node | Effect |
|---|---|
| `memory`, `cpus` | The container's hard memory limit and CPU count; a manifest that declared a memory limit under its own name with `runtime-effect = "docker.memory-limit"` is read as `memory` |
| `runtime.devcapsule-command` | The name of the in-capsule DevCapsule command, `devcapsule` or `devcapsule0`; reserved for projects that develop DevCapsule itself |

## Bindings, `config bind RESOURCE PROVIDER:VALUE`

Bind a component's declared persistent resource to storage of your own. The
provider `host-directory:` takes an existing directory, which becomes a
read-write mount; `host-environment:` names a host environment variable for
a declared secret and records only its name.

| Resource | Holds |
|---|---|
| `home` | The capsule user's persistent home |
| `pycharm/config`, `pycharm/plugins`, `pycharm/system`, `pycharm/log`, `pycharm/cache` | PyCharm's directories |
| `codex/home` | Codex configuration and sign-in |
| `codex/openai-api-key` | `host-environment:OPENAI_API_KEY`; the listing warns that the value is visible to every process in the capsule |

The command reports the resource's sensitivity and whether its component
allows concurrent use. Every binding is revalidated when `project run`
derives the plan, before a launch uses it.
