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

## What We Believe

A workflow is a set of habits, and habits come from somewhere. Ours come
from a tradition that is older than most of the tools we use, and we would
rather name it than pretend to have invented it.

We believe in the generation that taught the field to think: Wirth, Parnas,
Dijkstra, Nygaard, Liskov. From them we take four convictions that every
rule in this workflow is quietly trying to serve. That software is made of
modules, and that a module is a unit of understanding before it is a unit of
code. That the best interface hides the decision most likely to change, which
is what information hiding has meant since Parnas said it. That concerns
kept separate stay understandable, and concerns allowed to mingle do not.
And that abstraction is not a luxury of the theorist but the working
engineer's only real defense against complexity: the power to say less and
mean exactly as much.

We believe those convictions have found their modern, practical form in two
books, and we recommend them to anyone who adopts this workflow. Not as a
requirement, since nothing here depends on having read them, but as a
courtesy to yourself: with them in hand, the shape of what follows will feel
less like our opinion and more like common sense written down.

*Software Engineering at Google*, by Winters, Manshreck and Wright, gives the
discipline its most useful one-line definition, programming integrated over
time, and shows what changes when a codebase must outlive the people, the
tools and the assumptions it started with. Nearly everything this workflow
asks of you about records, decisions and hand-offs is an answer to that
sentence, applied to a team in which some of the programmers are machines.

*A Philosophy of Software Design*, by John Ousterhout, is the clearest
account we know of why complexity accumulates and how a designer pushes
back: deep modules, interfaces simpler than their implementations, and the
patient removal of the small complexities that nobody meant to add. We ask
the same of the software you build with this workflow, and of the workflow
itself, which is why it tries to stay small.

If you already hold these beliefs, you will find this workflow familiar and,
we hope, a relief. If you do not, we ask only that you try it for one
project and judge it by what it saved you.
