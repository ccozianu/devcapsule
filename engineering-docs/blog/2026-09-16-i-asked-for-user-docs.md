# I asked for user docs

*September 16, 2026. In Costin Cozianu's voice, written with Codex from
our conversation and reviewed by Costin. Quotations are lightly edited for
spelling and readability.*

We had managed to make the DevCapsule landing page look rather inviting.
It promised an isolated development environment, a proper IDE, your choice
of AI agents, and some help keeping a project's engineering knowledge in
order. I liked it. I even told the agent it might put copywriters out of
business.

Then I asked for the next fairly obvious thing: a curious visitor should
be able to go from that page to doing something useful, without a
"what the heck am I supposed to do here?" moment.

The agent got busy.

It downloaded the released executable, checked its checksum, initialized
a project, started Docker containers, inspected the IDE, ran a small
JavaScript program, stopped the environment and started it again. It
checked that files and IDE state survived. It investigated how to exit
cleanly. There were screenshots, documentation links checked, Windows
notes, and some actual runtime rough edges discovered along the way.

Eventually I had guides for v0.2.12 and three GitHub merge links to deal
with.

I also had a question. When had we decided that our adopter's first
experience should be a little JavaScript exercise in VSCodium, without
an AI?

I had asked us to work on user docs. Somewhere during the execution,
quite a few product decisions had acquired the status of facts.

This is a peculiar argument to have with an assistant. You can see that
it has worked hard. Some of the work is useful. The commands were checked
with a care I would normally welcome. Yet now you have to interrupt it
and explain why you are unhappy with this abundance of diligence.

"A little learning is a dangerous thing," I reminded it.

My experience with the earlier Sol model had been different. It had not
taken off on this sort of expedition, and neither had the other agents
I had been using. I can't turn that observation into a conclusion about
which model is better. Perhaps the new behavior is exactly what people
want in many other development situations. Here, I was still available
to discuss what we should build, and the agent had made itself very busy
before having that discussion.

So I proposed an experiment. We could open another branch, I could give
it the remaining product vision in vague terms, and it could work alone
until it considered the product finished. But before spending the effort,
what result should we expect?

I even offered to remove myself from the judging panel. We could give
the result to three developer friends and ask whether it exceeded their
expectations and whether they wanted to keep using it.

It seemed possible. I was interested in whether it was likely enough
to be worth trying. A possibility is a rather small
thing on which to base a potentially expensive project.

We left that experiment on the drawing board.

There was a budget behind this discussion, although I was already paying
$200 a month for the service. The subscription doesn't make my afternoon
longer. Every new investigation also produces something for me to read,
understand, question, or merge. And the agent has its own limits: context,
tokens, and how much of our earlier reasoning it can retain.

Borrowing the spirit of Dijkstra, I wanted both of us acutely aware of
the strictly limited size of our token budget. My attention belonged in
the same calculation.

We did wander off to discuss whether the AI had qualia. I will spare you
that part. Apparently even a conversation about staying focused can
acquire a philosophical dependency.

What I wanted to keep from the discussion was a change in our working
habits. An apology in a chat would be of little use to the next model
that opened the repository.

We added some [shared instructions for coding agents](https://github.com/ccozianu/devcapsule/blob/bfbfa5a4ce06896d1d82cb9ea0c17324e2038e0e/AGENTS.md).
Discuss consequential product choices while they are still cheap to
change. Start with the requirements and contracts. Before an expensive
investigation, know what question it will answer and how that answer
could affect the next decision. Have a stopping point. Get on with
routine work without asking me for permission at every step.

I also asked for a more careful sentence about tests. Passing existing
tests has value. Newly written tests for new functionality
deserve some caution: the agent may have put the same mistaken assumption
into both the implementation and the tests. All green, and we still
haven't agreed on what the user needed.

I think the instructions will help. I can't prove it, and we had
already given the subject quite enough of our attention. We isolated
the changes, I merged them, and we returned to the docs.

This time I asked:

> You generated user docs that are ready for v0.2.12. What do you think
> will happen when v0.2.14 comes out? How about v1?

Of course documentation needs maintenance. My concern was where we were
starting. If we patiently explain every inconvenience in today's
software, we can produce a very accurate guide to an experience we
would never have chosen.

I wanted to write the docs for the v1 experience we actually wanted.
Then, wherever the current release fell short, we would have found
something to implement next, or in a couple of iterations. Building it
would teach us something, and we could revise the docs together.

We would have to keep the intended experience clearly distinguished from
what users could do today. But now the documentation could help us
decide what to build.

For a start, I wanted the first sessions to include creating a small
project with at least one AI. Maybe two. Someone without an AI should
still be supported, but they were hardly the main audience for the
experience we had just advertised.

That led to another useful correction. I think developers should invest
in good tools, and I was quite ready to make the case for paying for an
AI subscription. But we could also offer a locally run open model.
That deserved a place in our thinking about v1.

We discussed Google's Gemma models, then OpenCode as a way to work with
local or hosted models. There was a plausible new component here, and
a setup we would eventually need to test and document. We recorded that
work for later and handed the evaluation request to project management.
No model was downloaded to settle the conversation.

The earlier guides are still on the branch. Their observations may save
us work. We haven't chosen the little project yet, or decided what a
second AI should contribute. Those are the next questions I want to
work through with my pair.

And this time, when we run a container, we should both know why.
