# Help new projects start with an installed workflow

Requested by the owner on 2026-09-24 during 0.2.14 RC0 website validation.
**Non-blocking for 0.2.14.** Proposed owner: workflow-improvements; sequencing
and acceptance belong to that workstream and project-management.

The website has `.devcapsule/devcapsule.toml` declaring single-stream, but
no WORKFLOW.md. The owner reports that its initialization was performed by
an agent outside the normal tooling path and wants a batteries-included
experience that helps users start with workflow files already installed.
This investigation did not reconstruct that historical initialization.
Do not infer that ordinary initialization was tested or caused the omission.

Define and implement an onboarding path that offers or installs the selected
workflow through supported tooling. Decide when it runs (project init versus
first launch), how mode/definition choices are expressed for interactive and
unattended use, and how the user deliberately declines if appropriate. Existing
workflow files, declared versions and user work must survive unchanged; no
silent workflow refresh. Repeated initialization must be predictable.

Acceptance should exercise a genuinely new project through normal tooling,
verify the declared workflow and its required files are consistent, and show
that the documented workflow command works from the IDE terminal. Cover
noninteractive choices, repeat invocation and a pre-existing workflow.

The [missing runtime command](../bugs/devcapsule/2026-09-24-runtime-cli-not-on-path.md)
is a separate release blocker: even manual installation cannot be discovered
or run normally while `devcapsule` is unavailable on PATH. Fixing its public
entrypoint does not by itself implement this onboarding improvement.
