# Design Research: Full-Stack FastAPI Development With PyCharm In Docker

Reference notes on using JetBrains tooling for a FastAPI backend + JS/TS frontend inside an
isolated Docker container running autonomous coding agents (Claude Code in
`--dangerously-skip-permissions` mode), and on why the network isolation strategy should stay
bridge-based rather than `--network host`.

---

## 1. IDE Choice: PyCharm Alone Is Sufficient — No WebStorm Needed

**WebStorm is effectively a subset of PyCharm.** PyCharm (Professional / Pro tier) includes all
of WebStorm's functionality for JavaScript, TypeScript, HTML, and CSS. Anything you can do in
WebStorm, you can do equally well in PyCharm.

- The **JavaScript and TypeScript plugin** is not third-party — it is bundled by JetBrains in
  IntelliJ IDEA, WebStorm, PhpStorm, PyCharm, RubyMine, GoLand, Rider, and CLion, and
  auto-activates when it detects relevant files.
- JetBrains markets PyCharm as a full-stack IDE supporting Python, Django, Flask, **FastAPI**,
  JavaScript, TypeScript, and databases out of the box.
- Framework support (React, Vue, Angular, Svelte) ships bundled or is a one-click Marketplace
  install — the same plugins WebStorm uses. React Buddy (component palettes, previews,
  Storybook integration) supports React 19 as of 2026.2 and works in PyCharm. Tailwind CSS
  support is likewise available.

### Licensing status (2025–2026 unification)

- **2025.1**: JetBrains merged PyCharm Community and Professional into a single unified
  product — one download, free core tier + paid Pro tier. PyCharm Community 2025.2 was the
  final standalone Community release; from 2025.3 onward everyone is on the unified build.
- **2026.1**: JavaScript, TypeScript, and CSS support — previously Pro-only — moved to the
  **free core tier**, including advanced navigation and code intelligence for web files.
- FastAPI-specific project tooling (dedicated project type, run configurations, endpoint
  tooling) remains on the **Pro** side.
- Existing Pro licenses carry over unchanged into the unified product.

**When would WebStorm ever make sense?** Only for fully separate IDE instances per concern or
a pure-frontend team (WebStorm is now free for non-commercial use). For a solo full-stack
project in a dockerized setup, it would just mean a second container image to maintain for
zero added functionality.

---

## 2. Recommended Project Setup

### Monorepo, one PyCharm project

```
project-root/
├── backend/     # FastAPI app (uvicorn)
└── frontend/    # Vite + React/Vue/... (npm)
```

- PyCharm indexes both halves; cross-file navigation works across the stack.
- Claude Code sees the entire tree from a single volume mount — matches the existing sandbox
  volume layout.

### Node.js inside the container

- Configure **Settings → Languages & Frameworks → Node.js** to point at a Node binary.
- Because PyCharm itself runs inside Docker, **Node must be installed in that container** —
  the TypeScript language service, ESLint, and Prettier integrations all shell out to it.
  Bake node/npm into the PyCharm container image (same principle as the Node 22 base in the
  Claude Code sandbox).

### Run configurations

- Create a **compound run configuration** starting both:
  - `uvicorn main:app --reload` (backend)
  - `npm run dev` (frontend)
- One-click full-stack startup, with the debugger attachable to the Python side.

### Port exposure

- Publish both service ports so the host browser can reach them:
  - `8000:8000` — uvicorn
  - `5173:5173` — Vite dev server (default)
- Keep npm registry domains on the firewall allowlist for installs.

---

## 3. Network Isolation: Why Not `--network host`

Premise considered: host networking is "a bit less isolated but not by much" since frontier
agents (Claude, Codex, Antigravity) are unlikely to deliberately attack the local machine.
Conclusion: **stay on bridge networking** — for three reasons.

### 3.1 It inverts the firewall design (the concrete footgun)

`init-firewall.sh` writes iptables rules inside the container (via `NET_ADMIN`). With
`--network host`, the container **shares the host's network stack**, so those rules land in
the *laptop's* firewall, not a container-scoped one:

- Best case: the egress allowlist suddenly applies to the whole machine and breaks everything
  else.
- Worst case: cleanup doesn't run on container exit, leaving the host unable to reach anything
  except the allowlisted registries.

Host networking therefore forces removing the firewall script entirely — i.e., giving up
egress control altogether. It is not a marginal reduction in isolation; it actively defeats
the design.

### 3.2 The real threat model is steering, not hostility

The failure mode is not the agent turning malicious — it is the agent being **steered**:

- Autonomous agents fetch web pages, read dependency READMEs, run install scripts, and execute
  test suites.
- A **prompt injection** in any of that content — or a malicious npm/PyPI package — can direct
  an obedient agent to exfiltrate readable data (`.env`, mounted source, credentials in
  volumes) to an arbitrary endpoint, or `curl | bash` a payload.
- The egress allowlist converts "agent got confused by hostile input" from an incident into a
  non-event. This protection is worth more than the container/host boundary itself.

### 3.3 What host networking additionally exposes

Everything listening on localhost becomes reachable from the agent:

- Local Postgres/Redis with no auth (common in dev setups)
- Other dev servers
- The Docker API, if ever exposed on TCP
- The LAN: router admin pages, NAS, etc.

None of this is reachable from a default bridge network.

---

## 4. The Middle Ground: Bridge Networking with Targeted Holes

Keeps the zero-approval-prompt agent workflow fully intact:

| Need | Solution |
|---|---|
| Agent must reach a host service (e.g. local DB) | `extra_hosts: ["host.docker.internal:host-gateway"]` in compose + allowlist just that host |
| Host browser must reach agent-run dev servers | Plain port publishing (`8000:8000`, `5173:5173`) — no host networking required |
| Lower friction on egress | Widen the allowlist domains rather than removing the wall |

**Bottom line:** the sandbox is what makes `--dangerously-skip-permissions` reasonable to run
in the first place. Dropping the network boundary to save a little compose configuration
spends exactly the safety margin that allows the agents to run unattended.
