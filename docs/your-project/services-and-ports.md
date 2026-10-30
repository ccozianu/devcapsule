---
description: Run databases, caches, and companion services alongside a capsule and reach web applications inside the capsule from your host browser.
weight: 4
updated: 2026-10-30
---
# Services and ports

By default, a capsule runs on Docker's `bridge` network: outbound internet
connections work normally, and only the capsule's per-run desktop port (plus
the [web console](../sessions/web-console.md) port on base recipe `11` or
newer) is published on `127.0.0.1` with a one-run token. Application ports
inside the capsule are isolated from your host network unless you expose one or
opt into host networking.

## Reaching a web server running inside the capsule

Choose the option that matches how much of your host network you want to share:

### 1. Preview inside the capsule (zero configuration)

Any server started in the IDE terminal (`npm run dev`, `flask run`, `mvn
spring-boot:run`) is reachable immediately at `http://localhost:<port>` from a
browser or Playwright test running **inside** the capsule desktop, with no port
publishing or host authorization.

### 2. Publish specific ports to `127.0.0.1` on the host (`bridge` network)

To open your app in your **host** browser while keeping Docker bridge
isolation, pass `--publish` (`-p`) bound to `127.0.0.1` either for one session
or saved privately for this checkout:

```bash
# One launch only:
devcapsule project run -- --publish=127.0.0.1:3000:3000

# Or save for every launch of this checkout:
devcapsule project config docker-args set -- --publish=127.0.0.1:3000:3000
devcapsule project run
```

Keep two details in mind when publishing over `bridge`:

- **Always prefix `127.0.0.1:`** (`127.0.0.1:3000:3000`, not `3000:3000`),
  otherwise Docker binds `0.0.0.0` on your host and exposes the dev server to
  your local network.
- **Bind the server inside the capsule to `0.0.0.0`** (for example, `vite
  --host 0.0.0.0` or `python3 -m http.server --bind 0.0.0.0 8000`). A server
  listening only on container `127.0.0.1` rejects connections forwarded across
  the Docker bridge.
- Remember that `docker-args set` replaces the checkout's saved argument list
  (including saved `config env` entries); place `--publish=...` tokens cleanly
  and re-check with `devcapsule project config docker-args list` ([Saved Docker
  arguments](../configuration/project-versus-personal.md#saved-docker-arguments)).

### 3. Share the host network namespace (`network host`)

When an application opens dynamic callback ports or talks to several local
services, authorize `network host` for the checkout (or one launch):

```bash
devcapsule project config authorize network host
devcapsule project run
```

With `network host`, `localhost` inside the capsule is your host's `localhost`:
servers listening on `127.0.0.1:3000` inside the capsule open directly at
`http://localhost:3000` in your host browser without `0.0.0.0` binds, and the
capsule can reach every port listening on your computer. Withdraw it anytime
with `devcapsule project config deny network` (or `forget network`).

## Running databases, caches, and message brokers

Containers exit and are removed whenever you close the IDE, so choose where
stateful services run deliberately:

### Option A: Run services on the host (or host Docker Compose)

Start PostgreSQL, Redis, or your `docker compose` stack from a host terminal so
its lifecycle and volumes stay independent of IDE restarts:

- **With `network host`:** connect from the capsule to `localhost:5432` (or
  `127.0.0.1:6379`) directly.
- **On the default `bridge` network:** map the host gateway into the capsule:

  ```bash
  devcapsule project config docker-args set -- --add-host=host.docker.internal:host-gateway
  ```

  Then point your app inside the capsule at `host.docker.internal:5432` (ensure
  the host service listens on the Docker bridge interface as well as
  `127.0.0.1` and requires authentication).

Declare connection variables in `.devcapsule/devcapsule.toml` without committing
credentials:

```bash
devcapsule project config require postgresql-client --because "migrations and psql run inside the capsule"
devcapsule project config require env POSTGRES_HOST POSTGRES_PASSWORD --because "connects to local development Postgres"
devcapsule project config env set POSTGRES_HOST localhost
devcapsule project config env set POSTGRES_PASSWORD
```

### Option B: Run Testcontainers or Docker Compose from inside the capsule

If your test suite starts containers itself (such as Testcontainers) or you run
`docker compose` from the IDE terminal:

1. Require or offer the Docker CLI in the manifest (`devcapsule project config
   require docker-cli`).
2. Authorize the host Docker socket on checkouts that run those tests:

   ```bash
   devcapsule project config authorize docker-daemon host-socket
   ```

Understand two consequences of `docker-daemon host-socket`:

- **Security:** control of the host Docker socket is equivalent to root-level
  control over your host Docker daemon ([The
  boundary](../containment/the-boundary.md)).
- **Sibling containers, not nested ones:** containers started through
  `host-socket` run alongside the capsule on your host daemon. Bind mounts use
  host paths, and under default `bridge` networking their published ports
  appear on the host rather than on the capsule's `localhost` (pair with
  `network host` or `--add-host=host.docker.internal:host-gateway` when tests
  inside the capsule connect to published ports).

### Option C: Embedded or user-space databases inside the capsule

Embedded stores such as SQLite and DuckDB—or lightweight user-space dev
servers—work inside the capsule with zero extra permissions. Keep their data
files inside your mounted project directory (gitignored) or under
`/home/devcapsule` so they survive container replacement; files under `/tmp`
disappear when the session ends ([What persists](../sessions/what-persists.md)).
