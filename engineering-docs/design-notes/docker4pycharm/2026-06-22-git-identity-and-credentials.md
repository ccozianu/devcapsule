# Decision: Git Identity And Remote Credential Transport

Date: 2026-06-22

Status: implemented; local identity behavior manually validated for v0; remote validation deferred

## Context

The v0 PyCharm container needs to make commits and use Git remotes from inside
the isolated IDE/Codex environment. Earlier commits from inside the container
could fall back to an auto-generated container identity. The existing launcher
already supported SSH agent forwarding and GitHub HTTPS token secrets, but it
did not configure Git `user.name` and `user.email`.

The project should not solve this by mounting host `~/.gitconfig`, host
`~/.ssh`, credential-manager directories, or other broad host state.

## Decision

Add explicit launcher options:

```text
--git-user-name NAME
--git-user-email EMAIL
--git-identity-from-host
--no-git-identity-from-host
--git-token-env ENVVAR
--git-token-file FILE
--git-token-user USER
--git-token-host HOSTS
```

As of 2026-06-24, the default launcher behavior is equivalent to an automatic,
best-effort host identity lookup: it reads only the host global Git `user.name`
and `user.email` values when they are available and passes those strings into
the container. It does not mount the host Git config. Use
`--no-git-identity-from-host` or `PYCHARM_GIT_IDENTITY_FROM_HOST=0` to disable
that lookup for a session. Use `--git-identity-from-host` when host lookup
should be explicit and warn if values are missing.

When identity values are present, the entrypoint writes them into the isolated
IDE home Git config at `/ide-global-settings/home/.gitconfig`, which persists
with the shared global settings directory.

The HTTPS token path remains file-based. Tokens passed from host environment
variables are copied into temporary host files and mounted read-only at
`/run/secrets/git-token`. The entrypoint configures `GIT_ASKPASS` and
`GIT_TERMINAL_PROMPT=0`. The askpass helper releases the token only when Git's
prompt URL host matches the configured `GIT_TOKEN_HOSTS` list, defaulting to
`github.com`.

Legacy GitHub-specific flags remain as aliases:

```text
--github-token-env
--github-token-file
--github-user
```

## Verification

Completed static checks:

```bash
bash -n docker4pycharm/run-pycharm-container.sh docker4pycharm/entrypoint.sh
shellcheck docker4pycharm/run-pycharm-container.sh docker4pycharm/entrypoint.sh
git diff --check
./docker4pycharm/run-pycharm-container.sh --help
```

Completed isolated entrypoint smoke test:

```bash
IDE_GLOBAL_SETTINGS_PATH=<temp>/global \
IDE_PROJECT_STATE_PATH=<temp>/project \
HOME=<temp>/home \
GIT_USER_NAME='Docker Test User' \
GIT_USER_EMAIL='docker-test@example.invalid' \
./docker4pycharm/entrypoint.sh sh -c \
  'git config --global --get user.name && git config --global --get user.email'
```

Observed result:

```text
Docker Test User
docker-test@example.invalid
```

Completed askpass smoke test:

- With `GIT_TOKEN_HOSTS=github.com`, a dummy token file, and
  `GIT_TOKEN_USERNAME=x-access-token`, the generated helper returned the
  username for a `https://github.com` username prompt.
- The helper returned the dummy token for a `https://x-access-token@github.com`
  password prompt.
- The helper returned only a blank line for a
  `https://x-access-token@gitlab.com` password prompt.

Manual validation update on 2026-06-28:

- The user confirmed default host global Git `user.name` and `user.email`
  values are passed correctly from the host Git config into the launched
  container.
- The user confirmed explicit `--git-user-name` and `--git-user-email` command
  arguments work as expected, with commits showing the intended author in
  `git log`.
- The user confirmed the default identity behavior with `git config --global
  --get user.name`, `git config --global --get user.email`, and a local test
  commit whose author is correct in `git log`.
- The user deferred live GitHub SSH and HTTPS remote validation until after the
  post-MVP refactoring. This is not a v0/MVP blocker because the user can push
  from outside the isolated IDE environment. See
  `completed-tasks/2026-06-28-git-remote-validation-deferred.md`.

Manual validation closeout on 2026-06-30:

- The user confirmed launching with `--no-git-identity-from-host` disables host
  identity lookup.
- The user confirmed launching with `--git-identity-from-host` warns clearly
  when host identity values are missing.
- Local Git identity edge-case validation is complete for v0. See
  `completed-tasks/2026-06-30-local-git-identity-edge-validation.md`.

Deferred manual validation:

- After the post-MVP refactoring, validate GitHub SSH remotes with
  `--ssh-agent`.
- After the post-MVP refactoring, validate HTTPS GitHub remotes with
  `--git-token-env GITHUB_TOKEN` or `--git-token-file`, without token
  persistence in the image or broad host credential mounts.

## Reopen If

Reopen if commits fall back to an auto-generated container identity, if token
values appear in Docker inspect output or persistent files, if the askpass host
filter sends a token to an unintended host, or if Git remote credential prompts
hang rather than succeeding or failing clearly.
