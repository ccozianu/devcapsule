---
description: "The day our workflow admitted it was opinionated: a preamble for adopters, an information model for people, a merge rule, and a bug we filed against ourselves."
draft: true
---
# The workflow explains itself

*October 3, 2026. Draft for the product owner's review; written by the agent
from the session's records, in the owner's voice, and quoting him where it
says so.*

For two months the workflow that runs this project grew one rule at a time,
each one earned by something going wrong. This week it crossed a line we had
not planned to cross: it started to feel opinionated. That is fine, and even
the point, but an opinionated process owes its adopters an explanation, and
ours had none. So we wrote one. This entry is about what we wrote, and about
the small, embarrassing bug that made us write it.

## The bug we filed against ourselves

It began with a sentence from my AI partner, delivered with full confidence
after a morning of good work: the unit suite could not run here, because the
capsule has no `nox` or `pytest`. Both were sitting in the project's virtual
environment, documented in the developer brief and pointed at from the local
workflow file, two documents the agent's own standing instructions tell it
to read first. My reply was not gracious: "well, hello: you cd
devcapsule-src and source .venv/bin/activate and voila, you have everything
you need."

The easy reading is that the agent slipped. It did. But we had been telling
adopters that this workflow coordinates humans and agents under a
state-of-the-art engineering process, and a state-of-the-art process has one
property above all others: any competent newcomer, human or machine, can
find out how the software is built and how its tests run without guessing.
We had made that discoverable to a careful reader and invisible to a hurried
one. That is a defect in the process, not only in the agent, and we filed it
as one, against ourselves.

The fix took an afternoon. The local workflow file's *Validation Commands*
section became the one heading the definition requires, with a fixed
structure: environment, unit tests, integration tests, end-to-end tests,
smoke test, gate, each a command runnable as written or the word `none` with
a reason. The session brief, the first thing an agent reads, now prints that
section verbatim, and names the template's untouched placeholder for what it
is. A new checkpoint trigger says that whenever the way the software is
built, tested, started or smoke-tested changes, the same commit updates that
section. And the reporting contract now says plainly that "the tool is
missing" is a finding only after the project's own instructions were
followed.

The scenario we tested the rule against was concrete: initialize an empty
repository, bootstrap the workflow, ask one agent to build a Maven
application with a REST endpoint and a single page in front of it, then exit
and let a different agent, from a different vendor, maintain it. Before this
week, whether the first agent wrote down how to run the tests depended on
its common sense. Now it is an obligation stated in three places it must
read.

## An information model, for people

The second thing the week taught us was that a bug queue holding wishes
hides both. A record filed in August as a bug, because the bug record was
the only kind of file with fields, turned out to be a feature with a design
in front of it. Nothing in the workflow said where a wanted capability lives
before it becomes a requirement. So we wrote the information model: the
kinds of thing the workflow stores, their homes and controlled fields, what
each may point at, how a thing moves from one kind to another, and a test by
field that tells a bug from a feature. A bug record needs a requirement it
threatens or a promised behavior observed wrong. Everything else is a
backlog entry, however large the gap.

Then a not-so-secret human secret intervened: large language models love
long files, and humans do not. The model came out of the two-thousand-line
rules document and into a short file of its own, with a diagram at the top
and a marker on the first line: *for humans*. An agent skips it in ordinary
work and returns to it when the question is what kind a thing is.

One detail for the reader who enjoys this sort of thing: when the question
came up of what the model itself is written in, we refused to improvise a
meta-model of our own and went looking for a known one. Codd's relational
model fits our record fields exactly, since "a question answerable from the
fields alone" is his idea, but it has no notion of a thing changing state
and it would flatten our set-valued fields into tables that no Markdown file
has. Chen's entity-relationship model is what people draw, but our relations
are often over other relations: a decision superseding a decision, a release
delivering a work order's scoping of a requirement to a workstream. So we
picked the higher-order entity-relationship model, HERM, of Bernhard
Thalheim and Klaus-Dieter Schewe, which allows exactly that, keeps
structured attributes and integrity constraints inside the schema, and
treats operations as designed together with the structure. We use it in
spirit, not in notation. The model's introduction gives a reader the five
words needed, entity, entity type, relationship, relationship type and
higher-order, and the body is written in plain sentences of a few fixed
shapes, so that nobody has to read the book to operate with the text. The
diagrams, when they come, will be drawn from the text rather than the other
way round.

## A preamble, and a merge rule

Humans need the ideology; agents do not. So the preamble is its own file
too, marked the same way, and it says three things to an adopter. That the
workflow is meant for most kinds of software project, from a tool shipped as
an executable to a website, a throwaway experiment, or a live service, because
what it governs is the records and the hand-offs, not the artifact. That it
binds where it speaks and nowhere else, with escape hatches that are named
rather than implied. And that its opinions are borrowed from a tradition we
would rather name than pretend to have invented: Wirth, Parnas, Dijkstra,
Nygaard, Liskov, and two books we recommend without requiring, *Software
Engineering at Google* and *A Philosophy of Software Design*.

One of those opinions we had been dodging for months: how work reaches
`main`. The definition used to say "whatever the repository's merge strategy
is." It now says one merge commit per reviewed deliverable, never a squash,
never a fast-forward, with `main` read by first parent so that the story is
one entry per delivery while every commit a record cites stays a real commit
in every clone. A project that prefers squash records the exception in its
local file, with the consequence spelled out. The Google-style discipline of
one squashed commit on one subject is saved as a feature for later; we agree
that `main` should not carry a task's intermediate states, and first-parent
reading is how it does not, today.

## What it cost, and what it saved

A day, mostly of conversation, and fourteen commits of Markdown with a few
dozen lines of Python and tests. What it saved is harder to count, and the
preamble ends with the only honest offer we can make: try it for one
project and judge it by what it saved you.
