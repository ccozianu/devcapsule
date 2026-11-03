# Project capabilities, settled and unsettled: an AI-workflow design for the definition

Sender: wrapped-projects
Recipient: workflow-improvements
Date: 2026-11-03

## What is handed over

The design note
`engineering-docs/wip/2026-11-02-wrapped-projects/2026-11-03-design-project-capabilities.md`,
at revision da24fb1f8a26 of `ws-wrapped-projects/wrap` (PR #333), and the owner's framing behind it.
The note proposes that a project, wrapped or not, declares the higher-level things it can be
made to do, browse, build, test, debug, manage, each settled or unsettled; that an unsettled one
is not an error but a standing task the status surfaces ("we can browse the code but cannot
build yet") and the agent takes up with the user; a record shape for a settled operation (the
recipe, the environment, the tool capabilities it needs, the date and revision it was proved
at, never a guess); the commands `operation settle`, `forget`, `list`, `run`; a discovery
dialogue for the first session of a wrapper, through the console's decision hand-off; and
answers to four questions as recommendations: one word or two for the two kinds of
capability, whether `browse` is the project's or the IDE's, whether `manage` is these records
or the workflow definition, and whether a proving run's evidence is kept.

## Why it belongs to workflow-improvements

The owner's ruling of 2026-11-03: this is an AI-workflow issue, not a launcher feature. The
AI is the one who should help the user attain engineering excellence, through the
state-of-the-art practices available as part of the workflow and through DevCapsule's
tooling. What the agent does on the first session of a project that cannot yet build, how it
proposes, how the human accepts, where the settled fact is recorded and how the status
surfaces what is not yet settled, are the workflow definition's to define; the launcher
commands that persist and run the result follow from that definition, not the other way
round. The wrapped-projects workstream keeps the launcher side, `project wrap` and the
`[sources]` declaration, and takes no further slice on operations until the definition
speaks.

## The evidence behind it

- The work order `engineering-docs/work-orders/2026-11-02-wrapped-projects.md`, amendments 6
  and 7 of 2026-11-02: the launcher infers nothing from a foreign tree; higher-level project
  capabilities are the next design.
- Slice 1's lesson: a Gradle detection that special-cased the showcase into the product was
  deleted; a fact the agent can establish with the user in a minute must not be guessed by
  the launcher and written into the manifest.
- The Socratic exchange of 2026-11-02 on the minimum and the maximum of DevCapsule: the floor
  is a reproducible room with a shell in it; the ceiling is a complete description of how
  work happens in a project, every layer above the floor optional.
- The showcase: `ccozianu/devcapsule-sample-frc-learning`, a wrapper around FRC team 6328's
  public robot code, whose build needs Java 17 and whose first session is exactly the
  dialogue the note describes.

## What accepting it would mean

Workflow-improvements takes the design as its own: decides the vocabulary, the states, where
the record lives and how the first-session dialogue runs, in the definition and its
templates; and hands the launcher side, the record's persistence, the `operation` commands
and the status surfaces, back to wrapped-projects or to another workstream as a work order
when the definition is ruled. The wrapped-projects status file lists the note as handed over
and holds its slices until then.
