# Retire run-image and expose an editable normal launch

Status: owner decided to remove `project run-image`; replacement lifetime and
implementation routing remain to be settled. This is a design input, not shipped
behavior or a command already available to users.

## Owner Direction

The separate arbitrary-image command does not earn its conceptual and maintenance
cost. Remove it while preserving debugger convenience: generate the Docker run
command equivalent to an ordinary `devcapsule project run`, open it in `$EDITOR`,
and let the developer save or explicitly execute it. Consider a shared switch
only if doing so does not introduce surprising effects in other commands.

## Implementation Evidence

At main `20336d8`, `commands/project.py:ProjectRunCommand.run` admits project
configuration, applies run-once choices, offers upgrades, materializes the image,
and passes a complete `PycharmRunOptions` to the launcher. After a zero return it
records configuration and version-set success. Returning the editor's exit code
through that existing success path would incorrectly certify an unrun environment.

`launch/pycharm/_launcher.py:run_pycharm` owns a host-browser broker context,
creates runtime files, builds Docker arguments, translates bind paths for an
external daemon, starts display-readiness observation, and finally invokes Docker.
Its `finally` removes generated files. The command references generated identity,
runtime-plan, launch-context, display-token and optional sudo/Xauthority/token
files. The host-browser socket can require a live broker. Arguments alone do not
represent the lifetime of a runnable launch.

`commands/framework.py` owns argument parsing and command dispatch. It has no
universal external-command plan or preparation/cleanup contract. Intercepting all
subprocess calls would also intercept builds, inspections and the helper Docker
invocation that prepares sudo policy ownership. It is the wrong abstraction.

Current scripts and Actions contain no direct `run-image` invocation. Its direct
CLI test covers the historical PyCharm state-adoption scenario; documentation
still advertises it. This does not prove that no external adopter uses it.

## Proposed Bounded Shape

An explicit option on `project run` (working spelling: `--edit-run`) reaches the
same final Docker argument builder as normal launch. Reuse a small editor/script
helper if useful; commands must opt into a defined launch lifecycle rather than
acquire a universal subprocess-interception mode. Do not create a second runtime
configuration model to replace the removed one.

Separate preparing, editing and executing in the result contract. Opening or
closing an editor must never launch the capsule implicitly or record known-good
use. The developer explicitly executes the displayed command; edits are an expert
experiment, not validation of the original version set. The ordinary launch path
retains its existing execution and success-recording behavior.

Preparation may require normal authorized image acquisition/materialization and
runtime-file preparation. State these effects accurately; do not market this as
a pure dry run. Editor validation should precede expensive preparation. Decide
whether update prompting belongs in this debugging mode before implementation.

Render from the actual argument vector with shell-safe quoting, preserving spaces,
quotes and shell metacharacters. Invoke the configured editor as an argument
vector, with documented support for arguments and a waiting editor invocation;
do not evaluate `$EDITOR` through a shell. Preserve required process environment
semantics without dumping the whole environment or embedding secret values.
Secret environment bindings currently use Docker `--env NAME` references.

## Lifetime Decision Awaiting The Owner

Two materially different deliverables:

- **Session-scoped editing.** DevCapsule keeps generated files and helpers alive
  while the editor waits and the user executes synchronously from it. Saving is
  allowed, but the saved command is an inspection artifact, not a promise of later
  replay. Editor return, detached editor processes and background containers need
  an explicit lifetime contract; do not clean up underneath a claimed live session.
- **Later replay.** The saved script must retain or regenerate its supporting
  files and restore any required helper services. It needs a named ownership and
  cleanup model, fresh/expired credential handling and clear same-host assumptions.
  Keeping old temporary files alone does not satisfy this contract. This is larger
  than a command-printing switch; no mechanism has been selected yet.

The owner's answer is required before choosing one. Do not quietly narrow a
promise of a saved runnable script to a session-only command.

## Verification And Routing

Meaningful checks should prove the generated argv matches normal launch under
controlled inputs; hostile path/value quoting round-trips; opening/cancelling or
failing the editor never launches or certifies a session; ordinary success and
failure recording remains correct; and runtime files/helpers live for the promised
execution period and are cleaned according to their owner. Later replay, if
selected, requires exercising the saved script after the original process exits.

Removal also drops public registration/help/docs and obsolete dedicated tests.
Review remaining callers of the shared host-network default before retiring the
network bug; removing one entry point alone does not fix the shared launcher.

Implementation is proposed for `maintenance`, which owns the run-image networking
defect. This checkout remains project-management. The explicit workstream-change
rule requires an owner instruction before switching; no source implementation or
new cross-workstream assignment has been performed by this design note.
