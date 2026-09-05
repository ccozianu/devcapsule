# Bug: Codex Was Installed As A Single Plucked Binary, So Every Sandboxed Command Failed

Date opened: 2026-09-05

Status: **fixed on the workstream branch 2026-09-05; owner smoke
pending** — Codex is now delivered as npm publishes it (see *Fix*).
Closes on the owner's next `project run` of a codex-carrying formation
with a sandboxed command succeeding.

Requirements: R-PRODUCT-001

Related: the [Antigravity delivery contract](../../wip/2026-08-30-component-catalog/CURRENT-STATUS.md)
(the `/opt/<component>` prefix convention this fix follows), and the
[upgrade-experience intake](../../wip/2026-08-09-project-management/intake/)
(the owner met this while rebuilding v0.2.9 and upgrading codex).

## Symptom

Reported by the product owner on 2026-09-05 as "upgrading codex left it
in an incomplete state" after the v0.2.9 rebuild. Reproduced inside the
formation built that morning (`devcapsule-local-pycharm:e52aa7f4934b232e7972`,
codex 0.153.0 on the v0.2.9 base):

```
$ codex sandbox linux -- /bin/echo sandbox-ok
thread 'main' panicked at linux-sandbox/src/launcher.rs:51:13:
bubblewrap is unavailable: no system bwrap was found on PATH and no bundled
codex-resources/bwrap binary was found next to the Codex executable
```

That is the path every agent turn takes the moment codex executes a
shell command under its default workspace-write sandbox. `codex --version`
and `codex login` worked, which is why the install looked complete.

## Mechanism (reproduced 2026-09-05)

The codex component declared its artifact as `tar-gz-member`: the
materialization extracted exactly one file,
`package/vendor/x86_64-unknown-linux-musl/bin/codex`, from the npm platform
tarball and copied it to `/usr/local/bin/codex`. The tarball is not a
single binary. It is a layout the vendor's launcher runs in place:

| Archive member | Installed |
|---|---|
| `bin/codex` | yes |
| `bin/codex-code-mode-host` | no |
| `codex-path/rg` | no (the base's apt `ripgrep` masked this one) |
| `codex-resources/bwrap` | no, and the base ships no bubblewrap |
| `codex-resources/zsh/bin/zsh` | no, and the base ships no zsh |
| `codex-package.json` | no |

`codex-package.json` declares `entrypoint = bin/codex`,
`resourcesDir = codex-resources`, `pathDir = codex-path`: the binary
resolves its helpers relative to its own real path. The single-member
format encoded the assumption that every agent CLI is one static
binary, which was true of Claude Code and was carried to codex without
reading the archive.

Not a regression of the 0.153.0 upgrade: the 2026-08-30 formations
carrying codex 0.145.0 panic with the same message. The sandbox path
had never been exercised inside a capsule before.

## Fix (applied on `component-catalog/antigravity-cli`)

Codex is delivered the way its vendor tests it, at the owner's
direction: a plain local `npm install` of the published packages, with
the resulting `node_modules/.bin` on `PATH`, under the `/opt` prefix
convention rather than `$HOME` (which the persistent home overlay
shadows inside a capsule).

- The lock pins two npm registry tarballs by URL and SHA-256: the
  `@openai/codex` meta package (new, at the component level — it carries
  the node launcher) and the per-platform package under the alias the
  meta package's optional dependencies name for that platform
  (`@openai/codex-linux-x64`; the artifact digest is unchanged).
- `LockedArtifactDeclaration` gains the `npm-package` artifact format.
  Every such artifact sharing a destination forms one npm project: the
  materialization copies the verified tarballs into
  `/opt/codex/<version>` beside a generated `package.json` naming each as
  a `file:` dependency, then runs one offline `npm install
  --ignore-scripts` with the base's node inside the build. Nothing is
  fetched during the build; npm only unpacks what the host checksummed.
- `/opt/codex/<version>/node_modules/.bin` joins the image `PATH`
  through the existing environment chaining.
- The formation descriptor records the npm layout, so codex-carrying
  formation identities change and rebuild.

Verified 2026-09-05 by building a scratch image on the v0.2.9 base from
the exact rendered steps: `codex` on `PATH` resolves through the
launcher to the platform binary, all six archive members are present
beside it, and a sandboxed command succeeds under Landlock both as root
and as uid 1000 with every capability dropped.

## What The Fix Does Not Cover

Codex's default sandbox is bubblewrap, which needs unprivileged user
namespaces. The capsule's hardening (seccomp filter, empty capability
set) denies them, so the bundled bwrap now fails with "no permissions
to create a new namespace" instead of "not found". Codex's Landlock
sandbox (`use_legacy_landlock = true`) works under that hardening. How
the component delivers that default — it lives in the user-owned
`~/.codex` state slot — is an open thread for the owner; relaxing the
hardening is the alternative and is not recommended.

## Reproducibility

Inside any capsule carrying codex:

```bash
codex sandbox linux -- /bin/echo sandbox-ok
```

Before the fix: the panic above. After the fix under capsule
hardening: bwrap's user-namespace refusal. With
`-c use_legacy_landlock=true`: `sandbox-ok`.

## Verification Target

The owner rebuilds a codex-carrying formation with the fixed client and
runs an agent turn that executes a shell command, with
`use_legacy_landlock = true` in the checkout's `~/.codex/config.toml`.
