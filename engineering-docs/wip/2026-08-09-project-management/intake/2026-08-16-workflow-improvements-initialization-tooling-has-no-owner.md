# Intake: Multiple-Stream Initialization Tooling Has No Owner

Delivered: 2026-08-16

From: `workflow-improvements`

## What Is Being Handed Over

The product owner asked that the reserved `project-management` workstream be
"initiated by the tooling on all devcapsule projects". The protocol half is
done. The tooling half has no owning workstream, and the tooling it would
extend does not currently implement the multiple-stream workflow at all.

This is a routing decision, which is why it comes here rather than being
assigned by the sender.

## Why It Belongs Here

`recursive-e2e`, `sample-projects`, and `workflow-improvements` all have
registered goals that this work does not fit. It is product implementation in
`devcapsule-src`, driven by a workflow requirement. Deciding whether it joins
an existing workstream, begins a new one, or waits is a sequencing and
lifecycle decision.

## Evidence

The only path that seeds workflow files today is `devcapsule bootstrap project`
→ `devcapsule/commands/bootstrap.py` → `run_script("docker4pycharm/bootstrap-project.sh")`.
That script predates the multiple-stream workflow entirely:

- it creates `engineering-docs/workstreams/`, a directory the current workflow
  does not use, and never creates `wip/` or `archive/`;
- it never reads or writes `workflow-type`, so it cannot branch on the mode;
- it knows nothing about the registry format, immutable start-date directory
  names, workstream handoffs, or `intake/`; and
- the `AGENTS.md` it emits describes the pre-multiple-stream protocol.

The Python package has no project-initialization command of its own; the
`bootstrap` command only shells out to that script.

Two further facts constrain any fix, both found while confirming the above:

- `devcapsule.compat.script_path()` prefers `<repo-root>/docker4pycharm/<script>`
  when present and falls back to the packaged
  `devcapsule/assets/docker4pycharm/` copy otherwise. The two copies have
  already diverged — the packaged one carries the `Docker4IDE` → `DevCapsule`
  rebrand and the frozen root one does not — so a source checkout and an
  installed build run different revisions of `bootstrap-project.sh` today.
  Fixing bootstrap without settling that lookup means fixing one of two
  divergent scripts.
- The bootstrap template baked into images is
  `devcapsule/assets/pycharm/image-assets/vibe-coding-process.md`, and it is a
  26-line stub holding only the user prompt. The full ~456-line template,
  including the agent instructions and the recommended `AGENTS.md`, exists only
  in the frozen `docker4pycharm/` copy that no code path reads. So the guidance
  a bootstrapping agent receives inside a real image is far thinner than the
  repository's own template suggests. This is pre-existing and independent of
  the reserved-workstream rule, but it undercuts "an agent following the
  bootstrap prompt will get this right".

## What Accepting Would Mean

Deciding an owner, and with it a shape. Three were considered when the product
owner scoped the protocol work, and the second and third were deferred rather
than rejected:

1. Leave bootstrap as it is; the reserved workstream is created by an agent
   following the documented procedure. This is the state as of this delivery.
2. Modernize `bootstrap-project.sh` to be workflow-type aware. Makes "the
   tooling does it" literally true, but invests in a path the root `README.md`
   documents as frozen historical reference.
3. Add a real initialization command in `devcapsule-src` that scaffolds the
   multiple-stream layout including the reserved workstream, leaving the legacy
   script alone. Cleanest end state, largest job, and a feature rather than a
   workflow correction — it likely wants its own workstream and its own
   requirement.

The sender's view, offered without authority: option 3, sequenced against V1
scope, with the stub-template gap folded in, since both are about what a
bootstrapping agent actually receives.

Priority and sequencing are this workstream's judgment, not the sender's.
