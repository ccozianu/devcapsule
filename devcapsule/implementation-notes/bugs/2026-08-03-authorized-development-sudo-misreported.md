# Bug: Authorized Development Sudo Is Reported As Enabled But Is Unusable

Date opened: 2026-08-03

Status: closed; fixed and externally validated on 2026-08-05

Requirements: R-SCOPE-001, R-DOCKER-001, R-FRAMEWORK-001

## Symptom

`devcapsule project run` resolves `development-sudo = true`, prepares the
container with a writable root and the development-sudo supplementary group,
and prints this unconditional success-style message:

```text
DEVELOPMENT SUDO IS ENABLED FOR THIS PYCHARM CONTAINER.

The mapped IDE user can run passwordless sudo inside the container.
```

Inside that same running formation-based capsule, the claimed capability is
not available:

```bash
sudo -n true
```

exits nonzero. Interactive `sudo` prompts for a password that the mapped
developer account does not have.

The message is materially misleading: authorization and partial launch-plan
preparation succeeded, but passwordless sudo activation did not.

## Reproduction

1. Use a checkout whose fresh resolution contains:

   ```toml
   [authorization]
   development-sudo = true
   ```

2. Run `devcapsule project run` and observe the passwordless-sudo banner.
3. In the launched capsule, run `id` followed by `sudo -n true`.
4. Observe that the mapped unprivileged user has the `ide-sudo` supplementary
   group but `sudo -n true` fails.

## Confirmed Evidence

Inspection of running formation-based container
`pycharm-isolated-costin-1785788887` showed:

- user `1000:1000`;
- supplementary group `44000`;
- `ENABLE_SUDO=1`;
- a writable root filesystem;
- no privileged mode or added capabilities; and
- `sudo -n true` failing inside the container.

The v021-derived image contains the `sudo` executable but no effective
`NOPASSWD` policy for the generated development group.

## Root Cause

The launcher currently treats the authorization as activation after only
preparing part of the contract. It adds the development group, generated
account files, writable root, default Docker capability set, and the legacy
`ENABLE_SUDO=1` flag. The generic PEX runtime does not consume that flag, and
the immutable image intentionally does not grant ambient sudo. No generated
sudoers policy is mounted under `/etc/sudoers.d/`, so group membership alone
grants nothing. The banner is driven by the requested option rather than a
complete effective policy.

## Required Fix

When and only when exact development-sudo authorization is effective, the host
launcher must:

1. generate a narrowly scoped `NOPASSWD` sudoers policy for the generated
   development group;
2. validate its content and restrictive file mode;
3. mount it read-only under `/etc/sudoers.d/`;
4. keep the writable-root and supplementary-group effects required by the
   development profile;
5. remove the temporary policy after normal exit or launch failure; and
6. print the enabled banner only for a launch plan containing the complete
   policy.

Without authorization, DevCapsule must not create or mount the policy, add the
group, make the root writable for this purpose, or claim sudo is enabled. Do
not solve this by baking ambient sudo into the shared image, assigning a
password, adding `SYS_ADMIN`, using privileged mode, or weakening the outer
seccomp/AppArmor boundary.

## Implemented Fix

The launcher now creates the fixed group-scoped policy in a mode-`0700`
launcher-owned temporary directory and gives the policy mode `0440`. Because a
normal host user cannot make a file root-owned directly, it invokes the exact
selected local image once with no network, a read-only root, all capabilities
dropped except `CHOWN`, `no-new-privileges`, a 64-process limit, and only the
policy file mounted. That helper changes the policy to `0:0`; the launcher
verifies ownership before building the main Docker plan.

The main capsule receives the policy read-only at
`/etc/sudoers.d/devcapsule-development-sudo`, retains its unprivileged mapped
user, and receives the generated group and shadow files only when authorized.
The banner moved after successful ownership preparation and Docker-plan
construction. Cleanup unlinks the root-owned child through its developer-owned
temporary parent and removes that parent after normal exit or any failure.

Focused tests cover positive and negative plans, content and modes, helper
confinement and failure, banner ordering, and cleanup. A disposable container
using `devcapsule-local-pycharm:1bae0035566680103826` (the v022-derived image)
passed `sudo -n true` and returned UID `0` from `sudo -n id -u` with the policy
mounted read-only. The pre-fix running container proved the negative case. The
same policy was then installed ephemerally in that already-authorized running
container, where both positive commands pass. The full dirty-tree Nox gate
passes with 182 fast tests at 81% coverage, clean mypy, rebuilt local PEX
smokes, and all three packaging integrations.

A subsequent formation-based `project run` used a materialized image carrying
exact source revision `a33988a24a91ef382c1c5c6265ba2a34762ba115` and exercised
the implemented launcher rather than an ephemeral repair. Docker inspection
showed user `1000:1000`, supplementary group `44000`, a writable root without
privileged mode, and the generated policy mounted read-only. The mounted policy
was `root:root` mode `0440`; `sudo -n true` returned zero and
`sudo -n id -u` printed `0`. A disposable run of the same image under the
unauthorized read-only, capability-dropped, `no-new-privileges` profile had no
policy and rejected noninteractive sudo. This evidence satisfies the close
criteria together with the existing positive/negative plan and cleanup tests.

## Verification Target

- Positive Docker-plan tests prove the policy is mode-restricted, mounted
  read-only, paired with the generated group, and cleaned up.
- Negative tests prove no policy, group, writable-root relaxation, or enabled
  banner appears without authorization.
- Preparation and Docker-launch failure tests prove temporary-policy cleanup.
- A real authorized capsule passes `sudo -n true`, and `sudo -n id -u` prints
  `0`.
- A real unauthorized capsule cannot use noninteractive sudo.

## Close Criteria

Close when the banner accurately describes effective behavior, an authorized
formation-based capsule passes the positive noninteractive sudo checks, an
unauthorized capsule retains the safe defaults, all temporary-policy cleanup
paths are covered, and the full Nox gate passes.

Reopen if authorization again produces only group/environment preparation, if
the banner can be printed without an effective policy mount, or if sudo becomes
ambient in the shared image or unauthorized launch path.
