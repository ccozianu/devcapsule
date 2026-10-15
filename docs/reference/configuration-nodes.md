---
description: "Every configuration node a checkout can carry, its values, and which command records it: authorizations, declared values and bindings."
weight: 1
updated: 2026-09-28
---
# Configuration nodes

Every recorded choice in a checkout is a node with one name. `project config
list` prints them with their state and source; the three commands below
record them. All are yours, per checkout, outside the repository.

## Authorizations, `config authorize NAME VALUE [JUSTIFICATION]`

| Node | Values | Effect |
|---|---|---|
| `base-image` | an exact `docker.io/…@sha256:` digest, or `default` for the project's current recommendation | Consent to run that image; binds to the image, so a lock change around an unchanged base keeps it |
| `network` | `host` | The capsule shares the host network namespace instead of Docker's bridge |
| `docker-daemon` | `host-socket` | The host Docker control socket is mounted; the capsule can control the host daemon |
| `development-sudo` | `true`, `false` | The capsule user may elevate inside the container through a temporary, launcher-owned sudoers policy |
| `host-browser` | `true`, `false` | `xdg-open` in the capsule may ask the host browser to open a URL |
| `host-x11` | `true`, `false` | The host display session is bound into the capsule instead of the contained desktop; never recommended by a project, stated at launch |
| `claude-code-download`, `antigravity-download` | `true`, `false` | Consent to acquire that vendor's agent under its terms |

`--all-recommended` previews every recommendation and authorizes all only on
`y`. A run-once form, `project run --authorize NAME VALUE`, records nothing.

## Declared values, `config set NAME VALUE`

Only names the project declares in its manifest, validated against the
declared type: `string`, `integer`, `boolean` or `memory-size`. `default`
records the project's recommendation; `config unset NAME` follows it again.
Two values have runtime effects today:

| Node | Effect |
|---|---|
| `runtime.memory-limit` | The container's hard memory limit, when declared with `runtime-effect = "docker.memory-limit"` |
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
allows concurrent use. Every binding is revalidated by `config resolve`
before a launch uses it.
