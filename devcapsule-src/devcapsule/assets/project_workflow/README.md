# Packaged Project Workflow Assets

These assets deliberately separate two layers that coexist in the DevCapsule
repository but have different ownership:

- `definition/` contains reusable protocol files. DevCapsule distributes these
  bytes and `devcapsule bootstrap project` installs them as `AGENTS.md` and
  `WORKFLOW.md` in adopter repositories.
- `templates/` contains initial project-memory instances. Bootstrap renders
  these into files such as `CURRENT-STATUS.md`, `REQUIREMENTS.md`, `index.md`,
  and, for multiple-stream projects, the reserved `project-management`
  workstream records.

Definition files describe how work is performed. Instantiated files describe
one project's purpose, accepted requirements, live state, branches, evidence,
and next step. Updating a reusable definition must not overwrite project state.
Bootstrap therefore installs missing definitions by default and refreshes
existing definitions only with `--refresh-workflow-definition`.

The root DevCapsule repository is itself an instance of this workflow, but its
`WORKFLOW.md` serves the needs of developing DevCapsule and need not be
byte-identical to the general-purpose definition shipped to adopters. Packaging
coverage verifies that a built PEX installs the definition selected from this
asset directory. The root `CURRENT-STATUS.md`, `.devcapsule/` declaration, and
`engineering-docs/wip/` records are also DevCapsule-specific instance state.
