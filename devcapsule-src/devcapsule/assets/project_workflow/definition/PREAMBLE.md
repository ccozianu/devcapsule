# Preamble

*For humans.* This file explains the workflow; it contains no rule. An agent
skips it in ordinary work and returns to it when it must decide something
the rules in `WORKFLOW.md` do not settle, alone or together with the human.

## To The Adopter

This workflow is opinionated, and this section says why you should let it be.

**It is meant for most software projects, not for one kind.** We run it on
a tool shipped as an executable, on a website that publishes that tool's
documentation, on throwaway experiments that may never ship, and on a
small live service that publishes a feed on a schedule. What those share
is what the workflow actually governs: a repository that is the only
memory, a human who decides, agents that do, and work that must survive the
end of every session. What differs between them, what a release is, what a
candidate is, how it is validated and where its evidence lives, the
workflow leaves to the project to declare. A website's release is a
deployment; an experiment's may never come; a live service releases
continuously and its candidate gate is a deploy gate. The rules still hold,
because they are about the records and the hand-offs, not about the
artifact.

**It binds where it speaks and nowhere else.** The escape hatches are
named, not implied. What `WORKFLOW.md` does not expressly deny is allowed,
and a pair that meets an uncovered situation decides and keeps working.
The project's own half, the local workflow file, settles everything that
depends on ecosystem, hosting or history. A rule that does not fit a
project is not broken quietly; it is recorded as an exception with its
reason, which is how we learn where we were wrong. Kinds a project does not
need stay unused. A single-stream project gets the same workflow with the
coordination removed. We ask for discipline in the records; we do not ask
for ceremony in the work.

**Its opinions are borrowed, and we say from where.** Version control as
the single durable memory, not chat. Append-only communication between
efforts, so that nothing in flight can be lost by a reset. Decisions written
down with their reasons, in the tradition of architecture decision records.
Requirements with stable identity and traceability to the work and the
evidence. Controlled vocabularies for state, so that a question is answered
by a field, not by reading everything. Release candidates accepted on
recorded evidence from the artifact a user would receive. Shared history
never rewritten. Small, frequent commits. A reference vocabulary for
process and work items taken from the Workflow Patterns initiative, and a
model of our own records in the spirit of entity-relationship modeling. To
these we add one thing the field has not had long: explicit decision rights
between a human and a coding agent, stated at each point rather than
renegotiated in every session.

Where real use has shown an opinion wrong, we change it and keep the record
of why; the *Changes* section of `WORKFLOW.md` is that history. Hold us to
it.
