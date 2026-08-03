# Bug: Authorized Development Sudo Is Reported As Enabled But Is Unusable

Date opened: 2026-08-03

Status: reproduced; root cause identified; implementation pending in Stage 4

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
