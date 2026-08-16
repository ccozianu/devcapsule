# Intake: Pausing A Workstream And Conversational Continuity

Delivered: 2026-08-16

From: `project-management`, recording a product-owner observation made the same
day.

## What Is Being Handed Over

The protocol defines how to select a workstream and how to resume its *state*.
It does not define what happens to the *conversation* when a workstream is
paused and the human switches to another one.

Sometimes nothing should happen: the discussion reached its end, everything
pending is already in the source tree, and clearing context for something new is
correct. Other times the human wants to return to the substance of the last
conversation held inside that workstream. Reproducing a screen is impossible and
not the point; recovering the context is.

## Why It Belongs Here

Session lifecycle, handoff formats, and record semantics are workflow protocol.

## Evidence

Observed in the `project-management` session of 2026-08-16, which produced a V1
readiness assessment, a scope ledger, two checkpoints, and this mechanism.

At the moment this item was written, four questions were open and existed only
in the conversation: the release thesis of containment versus workspace product;
whether the Java environment falls inside the V1 window; whether Case A of the
fourth-agent proposal is ratified; and whether the twelve-week release shape
stands. The handoff faithfully recorded every decision taken and had nowhere to
record any of the four. `Next Resumable Task` holds one thread and is not shaped
for "several questions await the human."

The same session lost smaller things by the same mechanism. The ledger records
that Eclipse is favored for a Java environment; it does not record that IntelliJ
IDEA was weighed and lost partly because JetBrains ceased shipping standalone
Community builds after 2025.2. Two-tier decision records capture that reasoning
for consequential decisions. Nothing captures it for the dozen small decisions
per session, which are precisely the ones a later reader reopens without knowing
they were ever closed.

## Sender's Analysis

Offered as analysis, not as constraints on this workstream's judgment.

**Three needs are easily conflated, and only the middle one is both missing and
cheap.**

1. State resumption — what is done and what is next. The handoff already serves
   this well.
2. Reasoning continuity — what was weighed, what was rejected and why, and which
   questions remain open. Not served by anything today.
3. Literal conversational resumption — re-entering a dialogue mid-thread. Likely
   a false goal: context is cleared, models change, and a replayed transcript is
   expensive to consume and mostly noise. Pursuing it tends to produce large
   artifacts nobody rereads.

**Capture intent at pause, not at resume.** Only the human knows whether a thread
is finished or suspended, and they know it when they stop. Inferring it on
return is guesswork after the information is gone. This suggests an explicit
pause action rather than a smarter resume rule, placing a cheap ceremony exactly
where the knowledge exists.

**A framing that fits this project's premise.** DevCapsule's thesis is that
project memory belongs in the repository rather than in chat history. A feature
that restores a conversation concedes that some memory lives only in the chat.
The consistent resolution is that pausing is the moment chat-only context is
promoted into the tree, which turns the question from "how is a conversation
saved" into "what does pausing require the human and agent to write down."

**Two constraints any design should respect.**

- Portability. `CLAUDE.md` requires this project to work across agents, so
  depending on a vendor's session-resumption feature or session identifiers
  would break that. Repository-level capture is the portable mechanism.
- Multiplicity. Several open workstreams imply several suspended threads, so
  whatever is stored must be per-workstream. The WIP directory already provides
  that shape.

**The cheap version.** A bounded `Open Threads` section in the handoff, written
at pause: questions awaiting the human, options weighed but unresolved, and the
reasoning that would let someone reopen a decision intelligently. Roughly ten
lines, not a transcript. Existing session records remain the escape hatch for
the rare case where the whole thing is genuinely wanted, and already support
detailed, summary, and verbatim capture modes on request.

## What Accepting Would Mean

A defined pause action in `WORKFLOW.md`, a place in the handoff for open threads
and unresolved options, and an explicit statement of what is deliberately not
preserved — or a recorded decision that the existing handoff and session records
are sufficient and why.
