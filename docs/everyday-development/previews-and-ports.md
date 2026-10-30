---
description: Reaching a web application that runs in the capsule from your computer's browser, and publishing a port on purpose.
weight: 4
updated: 2026-10-30
---
# Previews and ports

When you start a web server in the IDE terminal inside a default capsule (`npm
run dev`, `flask run`, `uvicorn`, `mvn spring-boot:run`), opening
`http://localhost:3000` in your **computer's** browser will not connect yet. By
default, the capsule uses Docker's isolated `bridge` network and publishes only
its token-protected desktop port (plus the [web console](../sessions/web-console.md)
port on recipe `11`+ bases) on `127.0.0.1`.

Pick one of three ways to preview your application depending on your workflow:

## 1. Publish a specific port to `127.0.0.1` on your computer (`bridge` network)

To keep default network isolation and expose only the port you choose on your
host's loopback address, pass `--publish=127.0.0.1:<host-port>:<capsule-port>`
either for one launch or as a saved checkout argument:

```bash
# Expose port 3000 on host 127.0.0.1 for this session only
devcapsule project run -- --publish=127.0.0.1:3000:3000

# Or save it for this checkout across launches
devcapsule project config docker-args set -- --publish=127.0.0.1:3000:3000
devcapsule project run
```

Then start your server inside the capsule bound to **`0.0.0.0`** (all container
interfaces), not container `127.0.0.1`:

```bash
# Vite / React / Vue
npm run dev -- --host 0.0.0.0 --port 3000

# Python (FastAPI / Uvicorn or Flask)
uvicorn app:app --host 0.0.0.0 --port 3000
flask run --host 0.0.0.0 --port 3000

# Static files
python3 -m http.server --bind 0.0.0.0 3000
```

Now open `http://127.0.0.1:3000` (or `http://localhost:3000`) in your host
browser. Keep three details in mind:

- **Include `127.0.0.1:` in `--publish=127.0.0.1:3000:3000`.** Writing
  `--publish=3000:3000` without `127.0.0.1:` normally binds `0.0.0.0:3000` on
  your host and exposes your development server to other devices on your local
  network.
- **Why `--host 0.0.0.0` is safe inside the capsule:** `0.0.0.0` inside the
  container only accepts traffic forwarded across the capsule's private Docker
  bridge from `127.0.0.1:3000` on your host. A server listening on container
  `127.0.0.1` drops forwarded bridge packets, producing an empty response in
  your host browser.
- **`docker-args set` replaces the entire saved list** (including saved `config
  env` entries). Check `devcapsule project config docker-args list` first, pass
  all `--publish=...` flags you want to keep in one command, and reapply any
  saved environment variables with `config env set` ([Saved Docker
  arguments](../configuration/project-versus-personal.md#saved-docker-arguments)).

## 2. Share `localhost` with host networking (`network host`)

If your app spins up dynamic ports, runs OAuth callback servers expecting exact
`localhost` origins without `0.0.0.0` flags, or talks to multiple local
services on your host, grant `network host` for one launch or for the checkout:

```bash
# One session only
devcapsule project run --authorize network host

# Or save for this checkout
devcapsule project config authorize network host
devcapsule project run
```

With `network host`, the capsule and your computer share one network namespace:
a server listening on `127.0.0.1:3000` inside the capsule opens directly at
`http://localhost:3000` in your host browser without `--publish` or `--host
0.0.0.0` flags. If a port is already bound on your host, the server inside the
capsule fails immediately with `EADDRINUSE`. Return to bridge isolation on the
next launch with `devcapsule project config deny network` (raw `--network`
Docker flags are refused; use `--authorize network host` or `bridge`).

## 3. Preview inside the capsule desktop (`browser-automation`)

When your project includes `browser-automation` (or you add it locally with
`devcapsule project config add browser-automation`), Chromium is installed
inside the capsule alongside Python Playwright (`$DEVCAPSULE_PLAYWRIGHT_PYTHON`
and `$PLAYWRIGHT_BROWSERS_PATH`). Headed Playwright runs and browser checks
inside the capsule connect directly to `http://localhost:3000` on the capsule
desktop without publishing any port to your host.

For connecting to databases, Redis, `host.docker.internal`, or Testcontainers,
see [Services and ports](../your-project/services-and-ports.md).
