# Deferred Task: Git Remote Credential Manual Validation

Date: 2026-06-28

Status: deferred

## Original Task

Manually validate GitHub SSH remotes with `--ssh-agent` and GitHub HTTPS
remotes with `--git-token-env GITHUB_TOKEN` or `--git-token-file`, without
mounting host credential directories or persisting tokens in the image.

## Requirements

R-GIT-001

## Decision

The user decided this should not block v0/MVP. For the current MVP, pushing
from outside the isolated IDE environment is acceptable, although less than
ideal.

Revisit this after the post-MVP refactoring described in
`engineering-docs/design-notes/docker4pycharm/future-agent-refactoring-brief.md`.

## Current Evidence

- Launcher support exists for `--ssh-agent`, `--git-token-env`, and
  `--git-token-file`.
- The Git askpass helper has had a local smoke test for username, token, and
  host filtering behavior.
- Live GitHub SSH and HTTPS remote operations have not been manually validated
  for the current v0 image.

## Reopen If

Reopen when post-MVP refactoring reaches the Git credential profile, or sooner
if pushing/fetching from inside the isolated IDE environment becomes a v0
requirement.
