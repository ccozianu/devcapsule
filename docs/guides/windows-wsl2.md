# Windows: read this before installing

DevCapsule v0.2.12 ships a **Linux Intel/AMD 64-bit executable**. On Windows,
run it in a Linux distribution under **WSL2**, with Docker Desktop's Linux
container integration enabled. PowerShell and Command Prompt cannot run the
executable directly; Windows on ARM is not covered by this release.

**WSL2 has sharp edges:** Docker integration, networking and opening the browser
can need attention. The project owner encountered these during Windows testing.
This page covers the confirmed setup and browser workaround; it is not yet a
complete account of that Windows troubleshooting session.

## Get Docker working in your Linux terminal

Follow [Docker's WSL2 backend instructions](https://docs.docker.com/desktop/features/wsl/),
including enabling your distribution under **Settings → Resources → WSL
Integration**. Open that distribution's terminal and check:

```bash
uname -sm
docker info
docker buildx version
```

You need `Linux x86_64`, a responding Docker server and Buildx before continuing.
If Docker works in PowerShell but not here, check the distribution's WSL
integration setting. Keep your project under your Linux home directory, such
as `~/hello-devcapsule`; Microsoft recommends the Linux filesystem for projects
worked on with Linux tools in its [filesystem guidance](https://learn.microsoft.com/en-us/windows/wsl/filesystems).

Now follow [your first session](first-session.md#1-get-devcapsule), running all
host-terminal commands in this Linux terminal.

## Open the desktop in Windows

When `project run` prints its desktop URL, paste the **whole URL** into your
Windows browser. The IDE runs inside the capsule; this path needs neither a
separate X server nor WSLg.

If you already have `wslview` available from the `wslu` package, this confirmed
workaround asks the launcher to use your Windows browser automatically:

```bash
BROWSER=wslview ~/.local/bin/devcapsule project run
```

Otherwise, opening the printed URL manually is sufficient. Keep the launcher
terminal open; closing the browser tab leaves the session running.

If the URL is unreachable, first check Docker is still running and that you
are using the URL from the current run. Other WSL2 networking remedies depend
on the host setup; do not apply an unexplained DNS or firewall change. Report
the actual error and Windows/WSL versions when [asking for help](https://github.com/ccozianu/devcapsule/issues/new),
with the private desktop URL and tokens removed.
