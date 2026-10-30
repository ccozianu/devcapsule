---
description: Running, debugging and testing a realistic application from the IDE inside the capsule.
weight: 3
updated: 2026-10-30
---
# Run, debug, test

Inside a capsule, your editor, build tool, test runner, and interactive
debugger all execute inside the same Linux container against `/workspace/<slug>`.
You do not configure remote SSH interpreters or Docker run targets inside the
IDE: to the IDE, the capsule **is** the local machine.

## Running and debugging by stack

Language debuggers (Python `debugpy`/PyDev, Java JDWP, Node.js Inspector, and
`.NET` `vsdbg`) attach over local sockets or child processes and work under the
capsule's default unprivileged hardening (`--cap-drop ALL` and
`no-new-privileges`) without extra permissions:

- **Python in PyCharm (`python-ide`):** Create or reuse a project virtual
  environment in the IDE terminal (`python3 -m venv .venv && .venv/bin/pip
  install -e ".[dev]"`), select `.venv/bin/python` as the Python interpreter in
  PyCharm (**Settings → Project → Python Interpreter**), and click **Run** or
  **Debug** in the editor gutter on any module or `pytest` test.
- **Node.js and TypeScript in VSCodium or VS Code (`frontend-ide`,
  `vscode-ide`):** Run `npm install` in the integrated terminal, open **Run and
  Debug** (`Ctrl+Shift+D`), and choose **JavaScript Debug Terminal** or launch
  an `npm` script directly with breakpoints set in your `.ts`/`.js` files. For
  Python, Java, or C# in VSCodium/VS Code, install the language extension once;
  it persists in your checkout's `extensions` slot.
- **Java and Maven in IntelliJ IDEA (`java-ide`) or Eclipse (`eclipse-ide`):**
  Temurin Java (`JAVA_HOME`) and Maven (`MAVEN_HOME`) are on `PATH` from the
  base image. Open `pom.xml` as a project in IntelliJ—or import `/workspace/<slug>`
  in Eclipse via **File → Import → Maven → Existing Maven Projects**—set
  breakpoints, and debug JUnit tests or `main` classes directly. Dependency
  downloads under `/home/devcapsule/.m2` persist across sessions.
- **`.NET` in JetBrains Rider (`dotnet-ide`):** Open your `.sln` or `.csproj`,
  build with `dotnet build`, and launch `dotnet test` or `dotnet run` under the
  Rider debugger; NuGet packages under `/home/devcapsule/.nuget` persist per
  checkout.

## Browser and end-to-end tests

When your test suite drives a real browser, add or offer `browser-automation`:

```bash
# Shared in the project manifest:
devcapsule project config offer browser-automation --because "Playwright E2E tests"
# Or added only on your checkout:
devcapsule project config add browser-automation
```

On the next `devcapsule project run`, offline Python Playwright
(`$DEVCAPSULE_PLAYWRIGHT_PYTHON`) and its pinned Chromium build
(`$PLAYWRIGHT_BROWSERS_PATH`) are materialized into the environment image. Both
headless test runs and headed `--headed` debugging on the capsule desktop work
against servers started on `127.0.0.1` inside the capsule ([Previews and
ports](previews-and-ports.md)).

If your integration tests start sibling containers through Testcontainers or
`docker compose`, declare `docker-cli` and authorize `docker-daemon
host-socket` on your checkout; see [Services and
ports](../your-project/services-and-ports.md) for host-bridge networking
caveats.

## Native debuggers (`gdb`, `lldb`) and resource limits

- **Native C/C++/Rust binaries:** `gcc`, `g++`, `cmake`, `gdb`, `lldb`, and
  `strace` are preinstalled in the base image. Starting a program as a child of
  the debugger (`gdb ./build/my-app`) works in a default capsule; attaching to
  an already-running non-child process (`gdb -p <pid>`) requires `CAP_SYS_PTRACE`
  (`devcapsule project run -- --cap-add=SYS_PTRACE`).
- **Out-of-memory kills (`exit 137`) or slow parallel test runs:** When large
  JVM builds, Rust links, or parallel test workers exceed your container's
  memory limit, raise memory or CPU count for one launch (`devcapsule project
  run --memory 8G --cpus 4`) or save it for the checkout (`devcapsule project
  config set memory 8G`); see [Resource
  limits](../configuration/resource-limits.md).
