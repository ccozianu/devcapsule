# Retire run-image and print the normal Docker launch

Status: owner-approved direction, simplified on 2026-09-22. Tested patch sent
to maintenance for review/application and integration. No implementation committed
on project-management; its temporary source changes were restored after delivery.

## Decision

Remove `devcapsule project run-image`. Preserve debugger convenience through a
print-only option on ordinary `project run`: render the actual Docker invocation
on stdout, with explanatory shell comments, then return without launching the
project container. The user owns redirection, editing and manual execution.

The owner explicitly chose this over editor integration and saved-script replay
support. This is diagnostic output. Generated runtime files may already have been
removed when the developer runs it manually; identify those dependencies rather
than retaining files, supervising helpers or promising a standalone replay script.
Do not add a new resource bundle, editor protocol or debugging-session lifecycle.
The earlier editor/lifetime alternatives are superseded.

## CLI And Output Contract

Implementation spelling: `devcapsule project run --print-command`.

- Use the same admitted project configuration, run-once options, image selection,
  Docker argument builder and external-daemon path translation as normal launch.
  Do not introduce a second configuration model or intercept arbitrary subprocesses.
- Print only shell-comment lines and the quoted command to stdout, suitable for
  redirection or piping to an editor. Preparation progress, warnings and errors
  go to stderr, including output from child processes. Prompts must not corrupt
  the generated text or consume a downstream editor's input.
- Describe actual arguments, including flags the ordinary launcher composes.
  Use standard shell quoting for every argument; preserve spaces, quotes, dollar
  signs, newlines and other metacharacters as data.
- Put comments on separate lines before the continued command. A `#` comment
  inserted between backslash-continued argument lines can terminate or corrupt
  the command. Prefer plain valid shell syntax over clever inline-comment tricks.
- Identify temporary identity/runtime-plan/launch-context files, display token or
  Xauthority files, optional sudo/token files, live browser-bridge sockets and
  ephemeral port choices when present. Distinguish persistent project/state
  mounts from resources DevCapsule cleans up. Explain environment-variable
  dependencies and host path translation where relevant.
- Never dump the process environment or turn secret bindings into literal secret
  values. Preserve Docker `--env NAME` references and explain that manual execution
  needs those variables. Comments must also avoid credential values.
- Generating the command is not a successful session. Do not record known-good
  configuration or version-set success, start the project container, or start a
  display-readiness watcher waiting for a container that was never launched.
  Keep normal cleanup; printed resource paths are not leases on those resources.
- Print the currently selected software. Do not offer/select an upgrade or perform
  automatic update checks merely to emit diagnostic output. Normal explicit
  configuration admission and acquisition authorization remain in force.
- Normal preparation can require image acquisition/materialization and temporary
  runtime-file setup, including existing helper operations. Document this clearly:
  it prints the final launch instead of executing it; it is not a side-effect-free
  dry run of all preparation. Do not invent mount paths or claim preparation took
  place if it failed. Fail with diagnostics rather than emit a partial usable-looking
  command when preparation fails.

An optional reusable rendering helper is appropriate. A universal command-tree
switch is unnecessary: the current framework has no shared external-command or
resource-lifetime contract. Start with the one command whose behavior is defined.

## Why This Boundary Fits The Code

At main `20336d8`, `commands/project.py:ProjectRunCommand.run` admits configuration,
materializes the selected image, and calls the shared launcher. It then records
successful configuration and version-set use for a zero return. A printed command
must take a distinct outcome/path so that a successful print is not mistaken for
successful use.

`launch/pycharm/_launcher.py:run_pycharm` owns the host-browser bridge, prepares
runtime files, calls `build_docker_args`, translates bind paths and finally invokes
Docker. Cleanup removes generated files. Rendering belongs at the final invocation
boundary, using those same arguments and reporting their dependencies honestly.

`commands/framework.py` owns parsing and dispatch. A global subprocess hook would
also intercept builds, inspections and the Docker helper that prepares sudo policy
ownership. That broad behavior is outside the chosen task.

Current scripts and Actions have no direct `run-image` invocation. Its direct CLI
test preserves the historical PyCharm state-adoption scenario and documentation
still advertises it; this is not proof that no external adopter uses it.

## Removal And Verification

Remove public command registration/help, obsolete usage documentation and dedicated
legacy tests. Update current design guidance to point debugger users to the print
option. Retain historical evidence as history. Check the remaining callers of the
shared host-network default before retiring the networking defect; command removal
alone cannot establish that the whole defect is resolved.

Verify the rendered command round-trips to the ordinary launch argv, stdout stays
valid shell text, comments accurately identify transient dependencies, and shell
syntax handles hostile-looking paths/values without evaluating them. Prove that
print mode neither launches nor certifies a project session and ordinary launch
success/failure behavior remains unchanged. Cover representative PyCharm and
VSCodium launches, contained display/host X11, secret environment bindings and
external-daemon path translation at controlled boundaries. Run the required build
gate; do not launch a new real environment merely to test text generation.

## Ownership And Next Step

Maintenance owns the existing run-image network/parity defect and receives this
bounded replacement task for 0.2.14 preparation. Under the owner's explicit
diff-handoff direction, project-management prepared and validated the patch without
committing source, delivered it as
`2026-09-22-project-management-run-image-tested-patch.md` at coordination
`93d794a41882`, and restored its checkout after verifying delivery. Maintenance
should review/apply it and own source commits and integration, without reopening
replay/editor scope. The status file records validation, checksum and the separate
workflow proposal. This is an owner-authorized recovery, not an autonomous switch
or a generic workflow rule already adopted.
