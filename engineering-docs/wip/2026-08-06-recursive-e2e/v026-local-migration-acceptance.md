# v026 Local Migration And Acceptance

Use this checklist after leaving the existing development capsule and returning
to the physical host. It validates the matched v026 CLI/base-image pair, the
native-X11 host-browser bridge, and the repaired development Python selection.

The committed project lock still recommends the published v024 base digest.
Do not edit that lock merely to test the developer-built v026 image. Select the
v026 tag through the checkout-local `base-image` authorization instead, then
regenerate the checkout-local resolution.

## 1. Verify The Released CLI And Local Image

The released PEX is directly executable and must not be run through a system
Python, Conda, pip, or a virtual environment.

```bash
set -eu

ROOT=/workspace/301e4208ef81-ChatGPT_Codex
PEX="$HOME/.local/bin/devcapsule.pex"
IMAGE=mycodespaceai/devcapsule-base:ubuntu-24.04-v026

mkdir -p "$HOME/.local/bin"
curl -fL \
  https://github.com/ccozianu/devcapsule/releases/download/v026/devcapsule.pex \
  -o "$PEX"
chmod 0755 "$PEX"

printf '%s  %s\n' \
  b7959c52f90b0e6c5043be787045968f94416e0b0faf75465696d47e53bab11c \
  "$PEX" | sha256sum --check

"$PEX" version --json

test "$(docker image inspect "$IMAGE" --format '{{.Id}}')" = \
  'sha256:cf72aa7b7926ff480f3b4fbec1b2e5c02e43044519d3679104dda1e7430dfdb2'
```

The version output must identify repository
`https://github.com/ccozianu/devcapsule` and revision
`91d50b1dd15468a706f5f965ae0dd6197ffd9ab7`. If the image inspection fails,
the physical-host Docker context is not the daemon on which the local v026
image was built; do not silently substitute the older registry image.

## 2. Select v026 For This Checkout

Review and record the exact developer-owned decisions, resolve configuration,
and confirm that `config list` reports the base as `authorized-local`:

```bash
cd "$ROOT"

"$PEX" project --path "$ROOT" config authorize base-image "$IMAGE"
"$PEX" project --path "$ROOT" config authorize docker-daemon host-socket
"$PEX" project --path "$ROOT" config authorize network host
"$PEX" project --path "$ROOT" config authorize development-sudo true
"$PEX" project --path "$ROOT" config authorize claude-code-download true
"$PEX" project --path "$ROOT" config resolve
"$PEX" project --path "$ROOT" config list
```

The host-browser bridge is deliberately not persistent project configuration.
It is an explicit run-once capability. Launch from the physical host, not from
an older capsule that did not inherit a bridge:

```bash
"$PEX" project --path "$ROOT" run \
  --docker-daemon host-socket \
  --development-sudo \
  --host-browser
```

## 3. Validate v026 Inside The New Capsule

In a terminal inside the newly launched PyCharm capsule, run:

```bash
set -eu

test "$BROWSER" = "/opt/devcapsule/bin/devcapsule.pex host-open"
test "$DEVCAPSULE_HOST_OPEN_SOCKET" = /run/devcapsule-host-open.sock
test -S "$DEVCAPSULE_HOST_OPEN_SOCKET"

printf '%s  %s\n' \
  b7959c52f90b0e6c5043be787045968f94416e0b0faf75465696d47e53bab11c \
  /opt/devcapsule/bin/devcapsule.pex | sha256sum --check
/opt/devcapsule/bin/devcapsule.pex version --json

xdg-open 'https://example.com/?devcapsule=v026'
```

Confirm that the test URL opens in the physical host's default browser. Also
click a normal HTTP(S) hyperlink directly in PyCharm and confirm the same
behavior. URL forwarding is expected only for absolute HTTP(S) URLs.

This acceptance is for the native-X11 launcher. noVNC or another browser-based
desktop will need an explicit URL-handling decision and might instead embed a
browser in the DevCapsule image.

## 4. Validate Development Python Selection

PEX execution and repository development are separate boundaries. The PEX
does not require a virtual environment. Nox development does use the ignored
`devcapsule-src/.venv`:

```bash
cd "$ROOT/devcapsule-src"

.venv/bin/python -c \
  'import sys; print(sys.executable); print(sys.prefix); print(sys.base_prefix)'
.venv/bin/python -m nox --version

source .venv/bin/activate
test "$(command -v python)" = "$PWD/.venv/bin/python"
python -m nox -s build
```

`sys.executable` and `sys.prefix` must resolve inside the current
`devcapsule-src/.venv`; `sys.base_prefix` remains `/usr`. If the checkout's
filesystem path changes, recreate the ignored virtual environment instead of
reusing it because Python virtual environments are not safely relocatable.

## 5. Verify Host-Broker Cleanup

Close PyCharm and allow the foreground `project run` command to return. On the
physical host, this command must print nothing:

```bash
for directory in "${XDG_RUNTIME_DIR:-}" /tmp; do
  test -n "$directory" || continue
  find "$directory" -maxdepth 1 -type d \
    \( -name 'devcapsule-host-open.*' \
       -o -name "devcapsule-host-open-$(id -u).*" \) -print
done
```

An empty result proves that the launcher removed its private runtime directory
and broker socket after the IDE container exited.
