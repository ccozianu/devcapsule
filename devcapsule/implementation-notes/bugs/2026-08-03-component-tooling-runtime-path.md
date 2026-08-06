# Bug: Component Tooling Is Not Added To The Runtime Path

Date opened: 2026-08-03

Status: reproduced; accepted V1 backlog item

Requirements: R-DEV-001, R-IMAGE-BUILD-001, R-FRAMEWORK-001

## Symptom

The v021 dogfood base contains the pinned Node.js/npm tooling promised by the
current V1 development baseline, but `node`, `npm`, and `npx` are unavailable
by name in the materialized PyCharm environment.

This is not a regression from the currently running v018 dogfood environment,
where the tools are also absent from `PATH`. Earlier image iterations did make
them available. It is nevertheless a V1 gap because the active base inventory
and D-0001's worry-free add-on model promise usable, declared toolchains rather
than merely archived files under `/opt`.

## Environment

- Base: `mycodespaceai/devcapsule-base:ubuntu-24.04-v021`
- Base source revision: `5401ce3506c0a8a63bfef40f4f9ef18d2b987436`
- Materialized environment: canonical PyCharm 2026.2.0.1 image
- Node.js installation: `/opt/node/current` ->
  `/opt/node/node-v22.23.1-linux-x64`
- Effective runtime `PATH`:
  `/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin`

## Reproduction And Evidence

In the running v021-backed dogfood container:

```text
command -v node  # no result
command -v npm   # no result
/opt/node/current/bin/node --version
v22.23.1
/opt/node/current/bin/npm --version
/usr/bin/env: 'node': No such file or directory
```

The npm executable exists, but its `env node` interpreter lookup also fails
because `/opt/node/current/bin` is not in `PATH`.

Reproducibility: always in the inspected v021 materialized environment.

## Expected Behavior

A selected base tool or worry-free add-on can declare its runtime environment
contributions as trusted component metadata. For Node.js/npm, the metadata
adds `/opt/node/current/bin` to the executable search path, making `node`,
`npm`, and `npx` available to the IDE, its terminal, and child agent/build
processes.

The mechanism must be generic. Runtime launch code must not contain
Node-specific paths or a growing set of tool-specific environment branches.

## Proposed V1 Direction

Add a versioned, schema-validated runtime contribution to curated base and
add-on component metadata. The initial contract may be deliberately narrow:

- an ordered list of absolute container directories to prepend to `PATH`;
- deterministic ordering and duplicate removal when several selected
  components contribute directories;
- rejection of empty, relative, traversal-containing, or otherwise malformed
  entries; and
- no project-controlled arbitrary environment map or secret interpolation.

The selected contributions must participate in the formation descriptor and
identity, survive base-to-environment materialization, and be applied by the
generic container runtime before it launches the interactive component.
Future non-path environment settings should extend the metadata contract
explicitly rather than bypass it with launcher-specific variables.

## Verification Target

1. Schema tests accept valid generic path contributions and reject invalid
   directories, duplicates or conflicts according to the settled contract.
2. Formation tests prove that selected runtime contributions participate in
   canonical identity and metadata inspection.
3. Runtime tests prove deterministic composition with the safe system path and
   inheritance by the final IDE process.
4. Base/image checks verify `node --version`, `npm --version`, and
   `npx --version` by name, not by absolute path.
5. The external PyCharm dogfood terminal and a child build process resolve the
   same pinned Node.js/npm installation.

## Close Criteria

Close this item when v021 or its V1 successor declares the Node.js binary
directory through generic component metadata, the generic runtime applies it,
all three commands work by name in a materialized environment, invalid
metadata fails safely, and the automated plus external dogfood checks pass.

Reopen if a selected relocatable toolchain is installed but requires a
tool-specific launcher edit or an undocumented manual `PATH` change to use it.
