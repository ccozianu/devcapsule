# Use your own project

Start with [your first session](first-session.md) to install DevCapsule and
check Docker. The commands here run in your computer's terminal, from the
project folder; agent commands run in the terminal **inside the IDE**.

## Open an existing checkout

Clone or open the repository as you normally would, then `cd` into its root.
Use a project you trust: its source folder will be shared read/write with the
capsule, and tools or agents can change it. Commit or back up work you care
about before experimenting.

If the project already has a `.devcapsule/devcapsule.toml` file:

```bash
~/.local/bin/devcapsule project init
~/.local/bin/devcapsule project run
```

`init` uses the project's declared tools and asks for required local values,
base-image consent, and acquisition authorizations it still needs. Repository
recommendations do not grant host access. Use `project config show` to review
them, then explicitly authorize the access you choose. If this checkout is
already initialized, skip directly to `project run`.

## Give a project its first capsule

If it has no DevCapsule configuration yet, choose **one** IDE:

| Work you want to do | Initialize with |
|---|---|
| JavaScript/TypeScript with VSCodium | `~/.local/bin/devcapsule project init --need frontend-ide --need node` |
| Python with PyCharm | `~/.local/bin/devcapsule project init --need python-ide --need python` |

The prompts follow the [first-session explanation](first-session.md#2-make-a-first-workspace).
Additional tools can require their own vendor download/terms authorization.
Then run `~/.local/bin/devcapsule project run` to open the IDE.

The capsule supplies the selected development tools. An arbitrary project's
dependencies, databases and test commands still come from that project's
README; run those setup commands in the capsule's IDE terminal. A maintained
project configuration can already provide more of that setup.

The `.devcapsule/` manifest and platform lock belong with the project in Git.
They describe its environment. Host permissions, private agent sign-ins and
IDE state live separately in your local DevCapsule storage.

## Add a coding agent

Save your work and stop the capsule first. In your computer's terminal, from
the same project folder, select the agent you use:

| Agent | Add it to the project | Start it in the IDE terminal |
|---|---|---|
| Antigravity CLI | `~/.local/bin/devcapsule project config need antigravity-agent` | `antigravity` |
| OpenAI Codex | `~/.local/bin/devcapsule project config need codex-agent` | `codex` |
| Claude Code | `~/.local/bin/devcapsule project config need claude-code-agent` | `claude` |

These commands update the project's shared tool selection and lock, then ask
for any necessary acquisition authorization. Review the vendor terms shown
before accepting. Start the capsule again with `project run`; it acquires the
selected agent on that launch.

Run the agent command **inside the IDE terminal** and follow its sign-in
instructions. Use your own provider account and access plan. DevCapsule does
not supply an AI subscription or silently import your host's sign-in. If the
agent prints a sign-in URL, open it in your host browser. Its saved sign-in
state remains in local capsule storage for later sessions.

Try a small, reviewable request: “Explain how this project runs, then suggest
one small improvement and a way to check it. Wait for me before changing files.”
Review the result and run the project's checks before committing.

## Return to work

From the project folder, `~/.local/bin/devcapsule project run` is the return
command. Save files before stopping; a new session restarts processes while
reusing stored IDE and agent state. The container is disposable; your source
folder and local state are not.

Keep normal Git history and backups. Persistent state on one computer does not
by itself provide backup, synchronization to another machine, or an agent's
memory of every design decision.

## Review permissions

### Recover after a project configuration change (0.2.14)

Installing a newer launcher keeps the project's existing lock and recorded
choices. If the project itself changed its configuration, `project run` may
ask you to resolve it again:

```bash
~/.local/bin/devcapsule project config show
~/.local/bin/devcapsule project config resolve
```

`config show` prints the configuration listing and then the review: pending
decisions together, including your recorded base, the project's current
recommendation, and commands for the available choices. `config list` prints
the listing alone.
Choose one alternative for each pending authorization; do not execute every
alternative. A recorded denial is shown as a decision you can keep.

For example, **if you choose to accept the currently recommended base**:

```bash
~/.local/bin/devcapsule project config authorize base-image default
~/.local/bin/devcapsule project config resolve
~/.local/bin/devcapsule project run
```

`default` accepts the current pin. It does not grant host access or accept
future versions. A local base override is shown separately; renewing it uses
its exact image identity and requires that image to remain available.

Workflow metadata and project display-name changes do not require a new
environment resolution. Changing several local options is a sequence of edits
followed by one `config resolve`; if an edit fails, earlier successful edits
remain. A refused resolution leaves the previous generated plan intact.

Launch explains the display choice before building the environment. Existing
explicit `host-x11` decisions survive recovery. Without one, a base supporting
the contained desktop uses the browser; an older base uses host X11. If you
explicitly deny host X11 and the base cannot provide a contained desktop,
launch stops before building and explains the choices. Any required image
build is explained before it starts; a new launcher can require a build to
install its matching runtime even when project tools stay the same.

### Change host access

From your computer's terminal in the project folder:

```bash
~/.local/bin/devcapsule project config show
```

The first exercise uses ordinary container networking and the contained
desktop. A project may request host Docker, host networking, administrative
tools, or host-browser integration; grant each only when your work needs it.
Changing an authorization does not reconfigure a running container. Stop it,
change the setting, resolve the configuration, and launch again.

Project launches use these recorded choices and explicit run-once options.
Legacy launcher environment variables do not add privileges, credential sources,
or host-directory bindings. `run --force` may use stale ordinary runtime settings,
but it cannot restore a removed permission, directory binding, or secret binding.

For example, to return from explicit host X11 access to the contained desktop:

```bash
~/.local/bin/devcapsule project config authorize host-x11 false
~/.local/bin/devcapsule project config resolve
~/.local/bin/devcapsule project run
```

Granting `host-x11 true` exposes the host's display session to capsule programs;
it is not needed for the normal browser desktop.
