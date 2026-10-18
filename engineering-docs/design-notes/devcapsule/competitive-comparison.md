# DevCapsule: Competitive Landscape & Critical Viability Analysis

*Target Version Reviewed: **v0.2.15** (current release track, with `0.2.16.dev0` in active development)*  
*Repository: `github.com/ccozianu/devcapsule` (Apache-2.0) | Docs: `devcapsule.mycodespace.ai`*

Last verified: 2026-10-16

Status: research and positioning input; recommendations are not adopted
product decisions.

Provenance: the original survey of 2026-08-15 compared `WORKFLOW.md` with
agent workflow frameworks; the
[2026-09-13 refresh](https://github.com/ccozianu/devcapsule/blob/164d7d0/engineering-docs/design-notes/devcapsule/competitive-comparison.md)
retracted several of its uniqueness claims against Spec Kit, OpenSpec, BMad,
Memory Bank, Beads, GSD Core, and Kiro, and that text is preserved in Git. This
revision, produced with Gemini 4 on 2026-10-16, widens the subject to the
whole product and does not repeat the workflow comparison; where it touches
the same ground, the September findings still bind. It was reviewed against
the repository's documentation the same day; the [review notes](#7-review-notes-2026-10-16)
at the end list every correction and every challenged claim.

Evidence standard: competitor statements rest on upstream documentation read
on the date above, not on installation or benchmarking. DevCapsule statements
rest on the `docs/` tree and source of the `0.2.16.dev0` checkout. Prices,
traffic figures, and other numbers without a cited source are omitted.

---

## 1. Executive Thesis: The Gap in the 2026 Agentic Coding Stack

The rise of autonomous CLI coding agents (Claude Code, Codex CLI, Aider, OpenCode) broke the traditional local development model. Developers want to run agents in autonomous ("skip-permissions" / YOLO) modes to iterate rapidly, but doing so directly on a host workstation exposes `~/.ssh`, `~/.aws`, browser sessions, and the host filesystem to hallucinated commands or prompt-injected supply-chain attacks.

Existing tools force developers into an uncomfortable compromise:
* **Run natively on the host:** Fast and ergonomic, but one bad agent loop or malicious dependency compromises the workstation.
* **Run in an ephemeral agent sandbox:** Safe for execution, but lacks the project's full SDK toolchain, loses installed tools on restart, and forces the human and the agent to work in separate worlds.
* **Run in enterprise DevContainers:** Heavyweight, tightly coupled to VS Code's proprietary remote server architecture, and blind to multi-agent workflows and host-trust boundaries.

**DevCapsule occupies a distinct, underserved niche:** a **local-first, stateful, capability-driven container workstation** where a real GUI IDE, interactive terminals, and multiple AI coding agents live together inside the exact same isolated environment—governed by explicit host boundaries and versioned project memory.

---

## 2. Competitive Matrix: Why Existing Efforts Fall Short

| Dimension | **DevCapsule (v0.2.15)** | **Docker Sandboxes (`docker sandbox`)** | **VS Code DevContainers / DevPod** | **Cloud Agent Sandboxes (Daytona, Upstash Box, E2B)** | **Host Env Managers (Nix, Devbox, devenv)** |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary Design Goal** | Stateful local capsule uniting a real GUI IDE + AI agents + project memory | Quick ephemeral isolation for a single CLI agent (e.g., Claude Code) | Standardizing team/enterprise container config for VS Code / Cloud | Programmatic, headless cloud microVMs billed per second for AI execution | Reproducible package management directly on the host OS |
| **Security & Host Boundary** | **High & Explicit:** Separates what a repo *declares* from what the developer *authorizes* on the host; nothing of the host's home, keys or display session is present by default | **Medium-High:** microVM with its own daemon, filesystem and network; declared sharing and documented credential handling, but no repository-versus-developer split | **Low-Medium:** A cloned repo's `.devcontainer.json` can execute arbitrary host/mount hooks if trusted | **High (Remote):** Runs off-device in cloud microVMs; requires network/cloud trust | **None:** Agents run with full host user privileges and can read `~/.ssh` or wipe `$HOME` |
| **IDE Model** | **Full GUI IDE inside the capsule** (PyCharm, IntelliJ IDEA, Eclipse, Rider, VSCodium), shown as the capsule's own desktop in a browser tab over a per-run loopback port and token | **None:** Terminal-only; host IDE fights the container over mounted files | **Split Client-Server:** Proprietary VS Code server or brittle JetBrains Gateway projection | **Headless / API-first:** Built for SDK calls (`code_run`), not daily human IDE work | **Host IDE:** Plugins and language servers still collide on the host machine |
| **Configuration Ergonomics** | **Capability-first** (`.devcapsule/devcapsule.toml`: required and optional capabilities with SDK majors owned by the project; IDE, agents and extras chosen per developer) + persistent user `/opt/xtras` | **Imperative CLI flags:** Changing env vars or tools often requires destroying/recreating the sandbox | **Committee JSON + Dockerfiles:** Heavy lifecycle hooks and complex feature registries | **SDK / Imperative Code:** Configured via Python/TS SDKs and cloud API keys | **Nix DSL / JSON:** Steep learning curve when non-standard binaries are needed |
| **Stateful Persistence** | **Resumable `$HOME` & `/opt/xtras`:** Survives container stop, rm, and image recreation | **Fragile:** Ephemeral outside the mounted workspace; restarts wipe ad-hoc tools | **Volume-dependent:** Rebuild cycles often wipe non-Dockerized user tweaks | **Cloud Snapshots:** Paid storage ($/GB/mo) and per-second vCPU billing | **Host-bound:** Everything lives on the host disk |
| **Agent Context & Memory** | **First-Class & Agnostic:** installs and maintains versioned `AGENTS.md`, `WORKFLOW.md`, `CURRENT-STATUS.md`; compliance by the agent is not enforced | **None:** Restarting the sandbox often loses agent session context | **None:** Pre-dates agentic coding workflows | **Proprietary Harness:** Tied to vendor SDK state | **None:** Unaware of agents |

### Why DevCapsule Beats the Closest Alternatives for Individual Developers

DevCapsule is opinionated and batteries included: a quick, no-nonsense way to do development in the age of AI. It brings three things together that the alternatives above deliver only in part:

* **Agents that run safely and at full speed.** No approve-this-or-that question at every step. The agent works in YOLO mode because the worst it can reach is the project folder, which Git protects, and nothing of the host's home, keys, or sessions is present.
* **The IDE, in the same capsule.** A real IDE, so the human can get into the guts of the codebase. We believe that is necessary, not optional: as agents write more of the code, keeping control of the architecture and the serviceability of the codebase is the human's job, and it is done in an IDE, not in a terminal scrollback.
* **A workable workflow** ([V1 Roadmap](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/wip/2026-08-09-project-management/coordination-backlog.md#item-16-the-workflow-from-workable-to-state-of-the-art-for-v1)) for humans and agents on one repository, with status, decisions, and next steps recorded in files so that any person or any agent resumes cold, growing toward state-of-the-art engineering practice ([V1 Roadmap](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/wip/2026-08-09-project-management/coordination-backlog.md#item-16-the-workflow-from-workable-to-state-of-the-art-for-v1)). We use it to build DevCapsule.

Four consequences follow, and they are where the comparison is decided:

1. **The environment the agent tests in is the one you debug in.** Run `docker sandbox run claude` and the agent is isolated, but the moment it needs a specific JDK, a Python C-extension, or a custom linter, the generic sandbox lacks parity with your IDE. In DevCapsule the IDE, the SDKs, the terminals, and the agents share one capsule; there is no second world.
2. **Your tools, without touching the team's definition.** In a DevContainer, a personal CLI tool, database client or experimental agent binary vanishes at the next rebuild unless it goes into the team's shared `Dockerfile`. DevCapsule gives you `/opt/xtras`: no `sudo`, on `PATH` for the IDE and the agents, survives container removal and recreation, never touches the project's lockfile.
3. **Security best practices by default.** What runs in your development environment runs inside the capsule. Most of it is software you can trust, vetted and run by others: DevCapsule itself, the SDKs, the agents. Some of it you cannot review package by package, the hundreds of dependencies that `npm`, `mvn` or `dotnet` pull recursively on your behalf, and that is exactly why they run in a capsule. The project declares what it needs, checked into Git; the developer authorizes what the host gives, owned locally; an untrusted repository cannot reach past that line. The experience of reviewing and approving the software you bring onto your box is one we will improve ([V1 Roadmap](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/wip/2026-08-09-project-management/coordination-backlog.md#item-17-review-and-approve-the-software-you-bring-onto-your-box-for-v1)).
4. **No vendor lock-in.** Your project does not become the prisoner of one agentic tooling. The proof is our own dogfood: DevCapsule is developed interchangeably and cooperatively with the big three, Claude Code, Codex, and Gemini's Antigravity, each reading the same project memory, starting from the standard `AGENTS.md`, and going into very detailed project management, with many episodes of separate LLMs reviewing the others' work. The memory files alone are not the differentiator, every agent vendor documents something similar; the bundle is: the memory, the environment, and the boundary maintained together, by one tool, for any agent. More are coming: open-source agents and open-weights models ([V1 Roadmap](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/wip/2026-08-09-project-management/coordination-backlog.md#item-8-opencode-evaluation)).

---

## 3. Critical Eye: Limitations of DevCapsule Today (v0.2.15)

Despite a strong architectural vision, evaluating DevCapsule at **v0.2.15** (and the `0.1.x–0.2.x` lifecycle) reveals concrete product and adoption hurdles:

### 3.1 Documentation: The Onboarding Path Is Written, The Everyday Pages Are Next
* The path a new developer walks is complete: *Start here*, *Your first session*, *Choose an agent*, *The boundary*, *Extra tools* and *Project capabilities and personal choices* are written and verified against the 0.2.15 executable. Thirteen pages in the `0.2.16.dev0` tree still carry `status: planned` and a *coming soon* body: the everyday-development pages (Git, previews and ports, run, debug and test), the project pages (what a project declares, services, and ports), the command reference and the project-info fields, two session pages, IDE preferences, hosted and local models, review and change agents, and cleanup.
* **What this means in practice:** a developer can run the first session and declare an ordinary project, because the capabilities page documents `init --required`, `--optional`, `--sdk-major` and `config capabilities`. Beyond that they fall back to `--help` or the source: the boundary page promises that SSH keys and cloud credentials never enter the capsule, and the page that should say how a push then works is a stub. Git, services and ports, and what a project declares are the three that block real work; the command reference and project-info fields are what agents reading the documentation miss most.
* **Where this stands:** the stubs are the next item of the documentation workstream, written in that order and each replacing its stub after verification in a real session; see [the user-docs plan](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/wip/2026-09-12-user-docs/CURRENT-STATUS.md#last-task-and-planned-next-step). Which further documentation improvements ship with the next release is [decision 2 of the release proposal](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/wip/2026-08-09-project-management/2026-09-27-0216-release-planning.md#decisions-still-needed).

### 3.2 The Browser Desktop and the Other Platforms
* Linux is the platform of choice for development, and DevCapsule is built on that conviction: the executable is Linux-only and the launcher assumes a Linux Docker host with the project folder on the same filesystem. Since v0.2.12 the capsule has **its own desktop**, delivered to a browser tab on the host over a per-run loopback port with a per-run token. Nothing of the host's display session enters the capsule; the earlier X11 passthrough survives only as the `host-x11` boundary node, which no project may recommend and which the launch announces when granted.
* **Windows** runs through WSL2 and Docker Desktop's Linux integration with the project in the Linux filesystem, and the desktop opens in the Windows browser. We used it that way ourselves, developing inside the browser over noVNC, and found it satisfactory; it has its own platform page because the prerequisites differ, not because the desktop is fragile. **macOS** is not supported and a port has not been started; the browser desktop makes a future port rendering-neutral, so the obstacle is the launcher, Docker Desktop file sharing and networking. **ARM Linux** is outside the release.
* **What remains, and where it stands:** the unavoidable friction between a desktop in a browser tab and an opinionated desktop platform, shortcuts that compete with the browser's, a clipboard that crosses only through the panel, a frame path that is not native. For V1 we take an item to explore alternative designs that remove it without reopening the boundary, first among them the remoting the VS Code family already has: VSCodium or VS Code running natively on the host, its editor on the host and its workspace, terminals and agents inside the capsule, connected over SSH or directly through Docker tooling; see [the desktop-friction item](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/wip/2026-08-09-project-management/coordination-backlog.md#item-14-desktop-platform-friction-alternative-designs-for-v1) in the pre-V1 backlog. The browser desktop stays the default and the containment design.

### 3.3 The Capability Catalog Ceiling
* A declarative, capability-first system (`init --required python --sdk-major python=3 --optional browser-automation`; the older `--need` form is legacy) is a pleasure when your stack is in the catalog. When a polyglot developer needs something it does not know, a specific `sbt` with GraalVM `native-image`, a CUDA toolkit, Rust with custom system C libraries, the declarative system stops at the catalog's edge.
* **What ships today:** `/opt/xtras`, personal, persistent, on `PATH`, no `sudo`. It covers every tool a developer installs for themselves. It does not cover a **project-level** need that every contributor must have and that the catalog lacks; the capabilities page says plainly that naming a new provider does not install it, and there is no documented way yet for a repository to carry its own component. That is the real ceiling, and it is a serious one.
* **Where this is going:** improving it is on the roadmap, tentatively for V1, and it starts from exactly the place a developer already stands: a component tested privately under `/opt/xtras/<name>`. From there, two ways out. Contribute it, as a pull request that puts `<name>` on the list of components DevCapsule monitors and installs. Or federate it, the quicker path: publish your own feed of components in a repository of yours and reference it from the project, with the trust decision made explicit the way every other declaration is. See [the catalog item](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/wip/2026-08-09-project-management/coordination-backlog.md#item-15-the-capability-catalog-ceiling-contributed-and-federated-components-for-v1) in the pre-V1 backlog.
* **Why components look the way they do:** DevCapsule has no wish to be yet another `.deb`, `.rpm`, PyPI or Maven repository. Its view is that software is best delivered as an archive unpacked into one directory and run from there, which is how every IDE, SDK, and agent in the catalog is installed today, by digest, into a directory of its own. Oracle's database ran that way long before modern tooling made it easy; in the age of AI there is no reason for software to arrive as an archive plus an install script that scatters its files across the filesystem. We undertake to publish that analysis with the mechanism, including what it costs for software that resists the model.

### 3.4 Secret Injection vs. Exfiltration Prevention
* DevCapsule's documented default is already the lower-exposure path: agents sign in interactively inside the capsule and the resulting token lives in the capsule's persistent home on the developer's computer, never in the repository. An API key enters only when the developer binds a named host environment variable explicitly (`codex/openai-api-key` from `host-environment:OPENAI_API_KEY`), and the listing warns that the value is then visible to every process in the capsule. Host SSH keys and cloud credentials are not present at all. The Git page that would explain how a push authenticates from inside the boundary is still a stub.
* What remains exposed is therefore the sign-in token in the capsule home and any explicitly bound key. A malicious test script in an untrusted repository can read either and send it out over the capsule's ordinary outbound network. Cloud sandboxes have moved on this: Upstash Box's *attach headers* and Modal's sandbox secret injection put a TLS-intercepting proxy on the host that adds the credential to matching outbound requests, so it never exists in the container's environment, files, or memory; Docker Sandboxes documents its own credential handling. DevCapsule has no outbound egress control and no host-side injection; the boundary is strong inward and open outward.

### 3.5 Search Visibility (work in progress)
* Search visibility is a barrier to adoption today: a developer searching for *"run Claude Code in Docker with PyCharm"* or *"isolated container for AI coding agents"* is unlikely to find this site yet. The sitemap is submitted and accepted and every page carries share metadata since October 2026; indexing and the rest of the search work are in progress, and a full accounting is planned for the V1 release: see [the search discoverability item](https://github.com/ccozianu/devcapsule/blob/main/engineering-docs/wip/2026-08-09-project-management/coordination-backlog.md#item-13-search-discoverability-the-rest-of-the-seo-objective) in the project's pre-V1 backlog.

---

## 4. Challenging Core Assumptions: What Might Change in the Future?

Any infrastructure tool built during a platform shift carries architectural bets that could be invalidated as the ecosystem matures:

### Assumption 1: "Developers Still Need a Full Heavyweight IDE" (The Vibecoding Debate)
* **The Contention:** A vocal movement in software engineering argues that traditional IDEs (JetBrains, VS Code) are legacy artifacts. If 80–95% of code is "vibecoded" or generated by autonomous multi-agent loops (Claude Code, Codex, Devin-style background workers), the human only needs a terminal orchestration dashboard and a lightweight diff viewer. If true, optimizing DevCapsule to run a heavy GUI IDE inside a container solves yesterday's problem.
* **The Counter-Reality (Why DevCapsule's Bet Still Holds—With a Catch):**
  * Pure "vibecoding" works for greenfield prototypes and disposable scripts, but breaks down in complex production systems where subtle concurrency bugs, architectural drift, and type-system constraints require deep static analysis, interactive debuggers, and refactoring engines (precisely where JetBrains IDEs shine).
  * In fact, as agents write *more* code, the human role shifts from **typist** to **high-leverage auditor and debugger**. Auditing a 2,000-line multi-file agent change is vastly safer inside a full IDE with semantic call-hierarchy navigation and integrated test runners than inside a terminal scrollback.
  * **The Pivot Risk:** Even if IDEs remain essential, developers may increasingly use **AI-first fork editors** (Cursor, Windsurf, Zed) running natively on their host OS rather than classic Linux GUI IDEs running inside X11/Wayland containers. If DevCapsule remains strictly wedded to running the GUI IDE *inside* the container rather than also supporting seamless host-editor attachment when desired, it narrows its addressable market.

### Assumption 2: Local Workstation Containers vs. Instant Cloud MicroVMs
* **The Contention:** With Docker Cloud Sandboxes, Daytona, and GitHub Codespaces offering suspendable cloud microVMs, why run heavy containers and LLMs on a laptop battery?
* **The Counter-Reality:** Cloud sandboxes bill for active compute and stored snapshots, introduce network latency on every keystroke, complicate local hardware and LAN testing, and raise corporate IP concerns. Power developers with 32GB–128GB RAM workstations strongly prefer free, zero-latency local compute that works offline and keeps proprietary code on-device.

### Assumption 3: OS-Native Sandboxing Could Replace Docker for Agents
* **The Contention:** Agent CLI makers are beginning to integrate OS-native sandboxing (Apple's `sandbox-exec`/Seatbelt on macOS, `landlock`/`bubblewrap` on Linux) directly into the agent binary so it cannot touch files outside the project directory without needing Docker at all.
* **The Counter-Reality:** OS-native process sandboxes only restrict file/network access for the agent binary; they **do not solve workstation hygiene**. They cannot isolate conflicting Java/Python/Scala toolchains, nor can they prevent IDE plugins and global packages from polluting the host OS. DevCapsule's dual value (Security Sandbox + Workstation Hygiene) protects it from being obsoleted by lightweight process wrappers.

---

## 5. The "Lone Wolf" Risk: Extinction vs. Maintainability

Adopting a developer tool maintained primarily by a single author (`ccozianu/devcapsule`) carries an inherent **"Bus Factor = 1"** risk. In June 2026 the VC-backed Daytona archived its open-source repository and moved development private, leaving the last AGPL release at v0.190.0; a community fork, Nightona, continues from that tag ([fork README](https://cdn.jsdelivr.net/gh/nightona-co/nightona@main/README.md)). The episode cuts both ways: a well-funded project can close overnight, and a permissive, standard-primitives codebase gets forked the same month. If the primary author of DevCapsule loses interest or moves on, does the project die, or can an adopter/small team take it over with minimal effort?

### Why DevCapsule Is Uniquely Survivable (Low Takeover Friction)
1. **Permissive Licensing:** Licensed under **Apache-2.0**, giving users and enterprises explicit patent and copyright clearance to fork, modify, and maintain internally without legal ambiguity.
2. **Thin Orchestration Layer Over Standard Primitives:** DevCapsule does not invent a custom hypervisor, proprietary container daemon, or closed-source remote server binary. It orchestrates standard OCI/Docker containers, standard Linux filesystem conventions (`/opt/xtras`, persistent `$HOME`), and human-readable `.devcapsule/devcapsule.toml` manifests.
3. **Self-Documenting "Project Memory" (Dogfooding):** Ironically, one of DevCapsule's greatest defenses against lone-wolf extinction is its own core feature. The repository uses its own structured, versioned project memory (`AGENTS.md`, `WORKFLOW.md`, `CURRENT-STATUS.md`, and a documented Development Journal). Any competent developer—or an AI coding agent pointed at the repo—can read the architectural intent, active workstreams, and current status immediately without reverse-engineering tribal knowledge.
4. **No Cloud Control Plane to Keep Alive:** Because DevCapsule runs 100% locally on the developer's machine, if upstream development stops tomorrow, existing installations will continue working indefinitely. There is no SaaS coordinator that can be shut down.

### Where the Hidden Maintenance Burden Lies
While the core CLI orchestrator is straightforward to maintain, a new maintainer would face two recurring maintenance taxes:
1. **Base Image & Capability Matrix Rot:** Developer toolchains move fast. Maintaining curated capability definitions and base images across rolling releases of JetBrains IDEs, Python, JDKs, Node, and rapidly changing AI agent CLIs is recurring work. Part of it is already automated and should be named: a daily GitHub Action publishes a component compatibility feed and status page on the `component-status` branch, version sets record the exact platform, base, components, and recipe of a working environment, and `project versions rollback` returns to the last successful set. What is not automated is base-image rebuilding against vendor releases. If that stays manual, the tool will feel outdated within months of inactivity.
2. **Cross-OS Display/Mount Edge Cases:** Debugging WSLg regressions after Windows updates or X11/Wayland permission quirks across Linux distros is tedious support work.

**Maintainability Verdict:** If the solo maintainer stepped away, an individual power user or small engineering team could fork and maintain DevCapsule for their own stacks, *provided* the capability definitions and Dockerfile composition templates are modular and data-driven rather than hardcoded in imperative logic. The effort has not been measured; the Gemini draft's "a few hours a month" is withdrawn as an estimate without evidence. The honest statement is that the Python-only toolchain, the Apache-2.0 licence, and the absence of a cloud control plane keep the takeover cost low, and that a reviewer can read the maintenance workstream's own records to see how much base-image and vendor-adapter work one release actually took.

---

## 6. Consolidated Strategic Recommendations Ledger

To maximize adoption and insulate DevCapsule against both competitive pressure and solo-maintainer burnout, here is the updated product recommendation ledger:

### **Pillar 1: Onboarding & Capability Ergonomics**
* **Rec 1.1 — Finish the Planned Pages, Git and Services First:** Of the ten `status: planned` pages, *Git*, *Services and ports* and *What a project declares* block real work; the command reference and project-info fields block agents that read documentation. Publish them with copy-pasteable `.devcapsule/devcapsule.toml` recipes for polyglot stacks (Python + Java/Scala, Node + Postgres).
* **Rec 1.2 — A Project-Level Custom Capability:** `/opt/xtras` already solves the personal case. The open question is whether a repository may carry its own capability definition or layer under `.devcapsule/` so that a team is never blocked waiting for the catalog. This is a boundary question as much as a convenience: a repository-supplied layer is code the developer runs on trust, exactly what the project-versus-developer split exists to govern.

### **Pillar 2: Cross-Platform Performance & GUI Flexibility**
* **Rec 2.1 — Decide the Host-Editor Question Explicitly:** The browser desktop is the containment design, not a stopgap: it is why nothing of the host display session enters the capsule. A "host IDE, capsule runtime" mode would reopen that boundary for the editor process and would need its own boundary node, like `host-x11`, with the same warning. The recommendation is to decide and document the position, not to assume the mode is wanted. The macOS motivation given in the draft does not apply, because macOS is unsupported for other reasons.
* **Rec 2.2 — Keep the Project on the Linux Filesystem, and Say Why:** The Windows page already follows Microsoft's guidance to keep the project in the WSL2 filesystem, which is the whole of the bind-mount performance problem. State the reason on that page and make the launcher refuse or warn on a `/mnt/c` project path, rather than engineering volume shadowing for a platform that does not exist yet.

### **Pillar 3: Hardening "The Boundary" for Autonomous Agents**
* **Rec 3.1 — Outbound Credential Injection and an SSH Agent Socket:** Host keys already stay out. The gap is outbound: an agent's sign-in token or bound API key can be read and sent anywhere. A host-side proxy that attaches credentials to matching outbound requests, as Upstash Box and Modal document, and an SSH agent socket forwarded as a boundary node would let agents authenticate to Git and LLM APIs without any secret existing in the capsule. This is the one place the matrix's "High & Explicit" boundary is weaker than the cloud alternatives, and it should be said so in the comparison.
* **Rec 3.2 — Name Git as the Undo, Then Ask What It Misses:** The boundary page already says "Git is your undo" for the project folder, and `project versions rollback` already restores the environment. A `devcapsule checkpoint` would add value only for what neither covers: the capsule's persistent home, where an agent's own configuration and installed extras live. Scope the recommendation to that, or drop it.

---

## 7. Review Notes (2026-10-16)

Reviewed by Claude Fable 5.1 against the `0.2.16.dev0` checkout's `docs/`
tree and the sources linked below, at the product owner's request, as a pull
request against the project-management branch. Each item says what the Gemini
4 draft stated, what the evidence says, and what was done.

| # | Draft statement | Evidence | Action |
|---|---|---|---|
| 1 | The IDE window is projected to the host over X11/Wayland; macOS suffers XQuartz/VNC quirks | `docs/containment/the-boundary.md`: the capsule's desktop is a browser tab over a per-run loopback port and token; `host-x11` is an opt-in node no project may recommend. `docs/platforms/macos.md`: not supported, port not started | Section 3.2 rewritten; Rec 2.1 and 2.2 refocused |
| 2 | Two sidebar pages are placeholders | Ten pages carry `status: planned`, including the command reference, project-info fields and Git | Section 3.1 corrected; Rec 1.1 reprioritized |
| 3 | Capability syntax `--need python-ide --need java-sdk:21` | `docs/configuration/capabilities.md`: `init --required`, `--optional`, `--sdk-major`, `config capabilities`; `--need` is the legacy form | Section 3.3 and the matrix corrected |
| 4 | No escape hatch for unindexed capabilities | `/opt/xtras` is the documented personal escape hatch; no project-level one exists | Section 3.3 split into the solved and the open case |
| 5 | Agents hold raw API keys in environment variables | `docs/working-with-ai/sign-in-and-defaults.md`: interactive sign-in is the default; a key enters only by explicit `host-environment` binding, with a warning | Section 3.4 rewritten around the real exposure, outbound egress |
| 6 | Vendor-neutral agent memory is a differentiator | The 2026-09-13 refresh retracted this claim with sources | Claim 4 qualified; provenance paragraph added |
| 7 | "Enforces" versioned project memory | Bootstrap installs the files; `WORKFLOW.md` itself says compliance is not automatic | Matrix wording softened |
| 8 | Cloud sandboxes cost $0.14 to $1.12 per hour; one subpage indexed; a few hours a month to maintain | No source for any of the three; the September evidence standard omits unsourced numbers | Price range removed, SEO claim marked unverified, effort estimate withdrawn |
| 9 | Daytona closed its open source in mid-2026 | Confirmed: archived June 2026, last AGPL release v0.190.0, community fork Nightona ([README](https://cdn.jsdelivr.net/gh/nightona-co/nightona@main/README.md)) | Sourced and the fork added as the counterpoint |
| 10 | Capability matrix rot is an unaddressed maintenance tax | `docs/updates/component-freshness.md` and `component-upgrades.md`: daily compatibility feed, version sets, `project versions rollback` | Section 5 names the shipped machinery and the remaining manual part |
| 11 | A checkpoint/rollback command is missing | "Git is your undo" for the project; `project versions rollback` for the environment; nothing for the capsule home | Rec 3.2 scoped to the uncovered part |
| 12 | `docker sandbox run claude` | Docker's reference documents it; the Docker Desktop integration is deprecated in favour of the standalone `sbx` CLI ([reference](https://docs.docker.com/reference/cli/docker/sandbox/run.md)) | Left as written; note the CLI is moving |
| 13 | Secret-injecting proxies at Upstash Box and Arcade | Upstash Box *attach headers* confirmed ([security docs](https://upstash.com/docs/box/overall/security)); Modal documents the same ([guide](https://modal.com/docs/guide/sandbox-secret-injection)); Arcade not verified | Upstash and Modal cited; Arcade dropped |

Not changed, for the owner's judgment: the matrix's characterizations of
DevPod, Nix, Devbox, and devenv rest on general knowledge rather than
documentation read for this revision; the September note's workflow-framework
comparison is referenced rather than restored; and the web console shipping in
`0.2.16` (the capsule as a token-gated page) is not yet in the matrix because
it is unreleased.
