# Vibe-Coding Process Bootstrap

This file is a reusable bootstrap template baked into the Dockerized IDE image.
It is not the target project's source of truth. Use it to create or update the
target project's own process documentation.

Expected image path:

```text
/usr/local/share/docker4ide/vibe-coding-process.md
```

## User Prompt

When starting work in a project that does not already have this process
documented, the user can ask:

```text
Bootstrap the vibe-coding process documentation from
/usr/local/share/docker4ide/vibe-coding-process.md into this project.
Create or update AGENTS.md, README.md, CURRENT-STATUS.md, REQUIREMENTS.md,
docs/, and engineering-docs/ as appropriate. Preserve existing project docs
and adapt the process to this repository. Set workflow-type in
.devcapsule/devcapsule.toml to single-stream or multiple-streams; use
single-stream when the project does not need independently resumable efforts.
```
