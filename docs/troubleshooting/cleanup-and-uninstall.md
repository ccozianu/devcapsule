---
description: How to inspect DevCapsule storage, remove unused Docker images and caches, reset one checkout's state, or uninstall DevCapsule completely.
weight: 3
updated: 2026-10-30
---
# Cleanup and uninstall

DevCapsule stores everything in standard user-owned directories and local
Docker images. It installs no system services, root files, or background
daemons, so reclaiming disk space or removing DevCapsule completely uses
ordinary file and Docker commands.

## See what DevCapsule is using

Before deleting files or images, inspect the active home, registered
checkouts, and local Docker images:

```bash
devcapsule home show
devcapsule project list
devcapsule images list --include-legacy
```

For a specific checkout, run `devcapsule project info` inside that repository
(or pass `--path <dir>`) to print the exact host paths of its checkout record,
persistent IDE/agent state slots, tool cache, and session logs; see
[Project info](../reference/project-info.md).

By default, a DevCapsule home spreads files across four XDG directories
(`~/.config/devcapsule`, `~/.local/share/devcapsule`,
`~/.local/state/devcapsule`, and `~/.cache/devcapsule`). When
`DEVCAPSULE_CONFIG_HOME` is set, configuration sits in that directory and
persistent data, state, and cache live in its `data/`, `state/`, and `cache/`
subdirectories; see [The configuration home](../configuration/home.md).

## Reclaim disk space safely

Most disk usage comes from Docker images and downloaded component archives.
You can reclaim both without losing your project files, checkout decisions, or
IDE settings.

### Unused Docker images

`devcapsule images list --include-legacy` shows every base image (`base`),
locally built IDE environment image (`materialized`, tagged
`devcapsule-local-<ide>:<hash>`), and older transitional image in your local
Docker store, along with its size and creation date.

Stop any running capsule sessions you no longer need, then remove old or
unused image tags with Docker:

```bash
docker image rm devcapsule-local-pycharm:<hash>
```

Keep the images your active checkouts currently run if you work offline or
expect to use `devcapsule project versions rollback` without rebuilding or
re-downloading; removing an image only means a later launch of that exact
component version will rebuild or pull it again.

### Downloaded component and tool caches

DevCapsule caches verified component downloads under `artifacts/` inside its
cache root (`~/.cache/devcapsule` by default, or
`$DEVCAPSULE_CONFIG_HOME/cache`), and stores per-checkout build and tool
caches under `projects/by-path/<checkout id>/` in the same cache root.

While no session is launching or running, you can delete the cache directory
to reclaim space:

```bash
rm -rf "${XDG_CACHE_HOME:-$HOME/.cache}/devcapsule"
```

If you use `DEVCAPSULE_CONFIG_HOME`, remove `"$DEVCAPSULE_CONFIG_HOME/cache"`
instead. Future launches recreate the directory and re-download or rebuild
only what active checkouts need.

### Old session logs

Session logs under `projects/by-path/<checkout id>/logs/` in state storage are
pruned automatically at each launch to fit `DEVCAPSULE_LOG_BUDGET` (`256M` per
checkout by default). To tighten retention, launch with a smaller budget (down
to `16M`), or delete ended `<session id>` subdirectories manually; see
[Diagnostics and logs](diagnostics-and-logs.md#how-much-disk-this-takes).

## Reset or remove one checkout

Every checkout keeps its configuration record separate from its persistent IDE
and agent state, and neither touches your Git working tree.

1. Run `devcapsule project info` in the checkout (before deleting the working
   tree, if you plan to remove the clone) and note:
   - the `checkout-record` path (and the companion `.resolved.toml` file in
     the same directory), and
   - the `projects/by-path/<checkout id>/` paths listed under persistent state
     and logs.
2. Stop any running session for that checkout (`Ctrl+C` in its launcher
   terminal, or `docker stop <container>`).
3. To wipe only the capsule's persistent IDE/agent state, logs, and caches for
   that checkout while keeping your recorded configuration choices, remove its
   `projects/by-path/<checkout id>` directories under data, state, and cache
   (leaving any explicitly bound external directories untouched unless you
   also want those removed).
4. To forget the checkout's configuration choices as well, delete its checkout
   record file (`devcapsule.checkout.toml` or `checkout.<name>.toml`), its
   `.resolved.toml` companion, and any matching per-checkout subdirectories
   under `docker-arguments/` and `console-requests/` in the configuration
   home.

## Uninstall DevCapsule completely

1. **Stop running capsules.** Press `Ctrl+C` in any open `devcapsule project
   run` terminal (every session runs with `docker run --rm` and removes its
   container on exit). Check `docker ps` for any stray container you want to
   stop manually.
2. **Remove DevCapsule Docker images.** List managed images with `devcapsule
   images list --include-legacy` before removing the executable, then pass the
   tags or image IDs you no longer want to `docker image rm`.
3. **Remove DevCapsule host directories.** For the default XDG home:

   ```bash
   rm -rf \
     "${XDG_CONFIG_HOME:-$HOME/.config}/devcapsule" \
     "${XDG_DATA_HOME:-$HOME/.local/share}/devcapsule" \
     "${XDG_STATE_HOME:-$HOME/.local/state}/devcapsule" \
     "${XDG_CACHE_HOME:-$HOME/.cache}/devcapsule"
   ```

   Also remove any custom homes you created with `DEVCAPSULE_CONFIG_HOME` (and
   `~/.local/share/pycharm-docker` if you used pre-`0.x` transitional builds
   that created it). Explicit host directories you bound yourself with
   `config bind` or `state adopt` stay where you put them.
4. **Remove the executable.** Delete `~/.local/bin/devcapsule` (or whichever
   path `command -v devcapsule` reports).

Committed `.devcapsule/` files inside Git repositories belong to those
repositories and stay untouched until a project removes them in Git.
