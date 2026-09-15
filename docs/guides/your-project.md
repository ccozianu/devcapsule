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

`init` uses the project's declared tools and asks for any local authorizations
it still needs. Read those prompts: another project's host-access choices may
be broader than the first exercise's. If this checkout is already initialized,
skip directly to `project run`.

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

From your computer's terminal in the project folder:

```bash
~/.local/bin/devcapsule project config list
```

The first exercise uses ordinary container networking and the contained
desktop. A project may request host Docker, host networking, administrative
tools, or host-browser integration; grant each only when your work needs it.
Changing an authorization does not reconfigure a running container. Stop it,
change the setting, resolve the configuration, and launch again.

For example, to return from explicit host X11 access to the contained desktop:

```bash
~/.local/bin/devcapsule project config authorize host-x11 false
~/.local/bin/devcapsule project config resolve
~/.local/bin/devcapsule project run
```

Granting `host-x11 true` exposes the host's display session to capsule programs;
it is not needed for the normal browser desktop.
