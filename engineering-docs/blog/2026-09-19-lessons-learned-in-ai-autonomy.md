# Lessons learned in AI autonomy over a simple, straightforward task

*September 19, 2026. A draft in Costin Cozianu's voice, written with Codex
from the website autonomy experiment and our review. This is a retrospective,
not a transcript; the owner's editorial review is still pending.*

After our earlier arguments about AI autonomy, I decided to try a smaller,
more concrete experiment. Give the agent a straightforward task, enough
freedom to do it, and enough budget that running out should not be the
interesting part. Then see what happens.

The task was a website for DevCapsule. A landing page, documentation, and
a development blog. Something that presented the project better than
GitHub's Markdown view, looked professional, and was pleasant to read.
No comment database. No grand application hiding behind the word website.

We wrote a [work order](https://github.com/ccozianu/devcapsule/blob/80321ecc14093ab5585b3eeee7e4fe78a9097b4c/engineering-docs/work-orders/2026-09-16-website-autonomy.md).
The content would stay in the DevCapsule repository. The website machinery
would live in a separate repository, included as a submodule. The agent
could choose the framework, appearance, navigation, and publishing approach.
It was supposed to consolidate its human setup needs at the beginning,
then work independently toward a reviewable preview.

This time, choosing the design without asking me about every detail was
the assignment.

The allowance was generous: up to the subscription month's allowance and
the three usage resets reported available. That was a ceiling, not an
instruction to consume it. We did not have reliable expenditure telemetry,
so I cannot offer a precise cost or a percentage of budget used. Budget
exhaustion was not the reason we stopped.

And the agent produced a website I liked.

That deserves to be said before the criticism. It looked good on localhost.
The documentation was readable, the links worked, and the blog had a home.
There were useful checks for mobile layouts and accessibility. We eventually
had both a test site and production, with a mechanism for promoting tested
files rather than rebuilding something different at the last moment.

I gave the experiment an A−. Generously, as I told the agent, and partly
for encouragement. I particularly appreciated its willingness to identify
shortcomings in its own work.

Then we started finding more of them.

One distinction appeared immediately: a good-looking preview is a smaller
deliverable than a website an owner can confidently operate. The original
stopping point was the preview; I subsequently asked us to take it live
before finishing the review. That expanded the work, and it would be unfair
to pretend every production concern had been an explicit initial requirement.
It was still an excellent opportunity to discover what the design had assumed.

Publishing involved two repositories and GitHub Actions. An early approach
asked me to create a personal access token with an expiration date to read
build artifacts from my public project. I objected. I did not want a new
credential-renewal chore just to publish public material. We changed the
mechanism to use public release assets instead.

That was a useful correction from the person who would have to live with
the system. The original mechanism could have been made to work. Its
maintenance burden was the objection.

The workflow controls also made me work harder than necessary. A mode
called production was used to deploy the test site. The default was preview,
which built an artifact without deploying it. A run could finish successfully
while the deployment and candidate jobs were skipped. Other accepted input
combinations could deploy a test build that was not eligible for promotion.

A green workflow was answering a narrower question than I thought I had asked.

We also needed a visible build timestamp. Until I asked, a visitor had no
obvious indication of when the site had last been built. None of these
problems required an exotic failure to uncover. They appeared when the owner
tried to publish and understand his own website.

Then I searched Google for a word on the production site. Nothing.
Bing did not find it either.

We could not conclude from that alone that GitHub Pages was broken, or that
the implementation was blocking search engines. The pages were accessible,
their production canonical URLs looked right, and crawling was allowed.
There was no sitemap. We had verified that the site could be read, but we
had not established that people could discover it through search.

The agent had put discovery improvements somewhere in its follow-up list.
I promoted search discoverability to W00. Sometimes prioritization requires
adding a number smaller than the numbers already assigned.

Google's ownership verification exposed another assumption. It asked for
a small HTML file at the website root containing a verification response.
Our checker expected every HTML file to have the structure of a normal page.
Promotion expected every HTML file to have a canonical URL. A perfectly
ordinary ownership file did not fit either assumption.

We added the file and a narrow exception that validates its contents and
preserves it through publication. Verification worked; Search Console then
said it was processing the indexing data. At the time of writing, indexing
was still an open question. Fixing verification was useful progress, not
evidence that W00 was finished.

The next issue was less visible and, to me, more fundamental. What exactly
was the contract between the content producer and the website builder?

There was some documentation about which files were consumed. There was
also code that depended on particular README headings and paragraph
positions. What we lacked was a sufficient, agreed interface specification:
which structures are stable, how drafts are treated, how navigation is
determined, which changes are compatible, and how a content author learns
that something is wrong.

If I disappeared tomorrow, my replacement should not need to commission
another AI to reverse-engineer those decisions.

Writing down whatever the code currently does would be a start. It would
not settle whether those behaviors are the contract we want. That still
requires a conversation about responsibilities and intended behavior.

We clarified ownership during the review. DevCapsule owns the content.
The website project owns appearance, website functionality, and publishing.
Work items should follow that division, even though the experiment began
in the parent repository. Mixed items need a clear dependency rather than
two copies of the same vague task.

Visitor measurement came up too. Could I see how many people visited,
where they came from, which guides they read, or whether the experience
worked for them? No analytics had been implemented.

Initially we treated that as another omission to examine. Then I recalled
that the intention may have been to add it in a second step. I explicitly
said we would not count it against the initial implementation. We added
the feature to the backlog instead.

That correction matters. A review should distinguish a defect, an
insufficiently discussed decision, and a useful next feature. Discovering
that I now want something does not establish that the agent failed to
deliver what we originally agreed.

Meanwhile, we managed to demonstrate another problem while merely
recording the problems.

I asked the agent to make search discoverability the first backlog item.
It edited the Markdown, but also ran the parent project's full build gate:
hundreds of tests, executable construction, and packaging integration checks.
There were branch operations, bookkeeping, and repeated progress polls.

All to write down that people should be able to find the website.

The repository did contain a rule requiring the full gate before a
checkpoint. The agent followed it literally and treated this small update
as a checkpoint. So we had both a blunt instruction and an agent applying
it without enough regard for the value of the evidence being produced.
Repeating the build did not tell us whether the new backlog sentence was
useful or correct.

I want our local rules to connect parts of the source tree to the software
contracts they affect. Run relevant checks at relevant moments. Some checks
belong on every commit; others belong before a pull request reaches main.
A content change deserves content checks. A publishing change deserves
publishing checks. We should be able to explain what a check could catch
before spending time running it.

I had noticed different behavior with the earlier Sol model and the current
Astra model. This experiment does not isolate model choice from context,
instructions, or task history, so it cannot establish the cause. It does
show why instructions need to work across different agents, and why a
model change deserves attention even when the workflow files stay the same.

The waste concerns me beyond my own patience. Subscription pricing can
hide the marginal cost of another command or another thousand tokens.
It does not make computing resources, electricity, or human attention free.
We did not measure the energy used here; no dramatic carbon calculation
is needed to ask whether a repeated test answers a useful question.

There is an apparent contradiction in this story. I gave the agent
autonomy, then criticized some of its independent decisions. But the
experiment was supposed to teach us where that arrangement worked.
The visual implementation was a success. The operational assumptions,
interface contract, and validation habits needed more human involvement.

The answer cannot be to make me approve every command. I would rather
write the website myself than spend the afternoon authorizing commas.
I do want the important assumptions made visible, the remaining gaps
described honestly, and the agent willing to stop executing when we need
to think together.

The A− stands. We have a website I like, a publishing mechanism that works,
and a more useful backlog than we had at the first review. We also have
concrete changes to make in how we collaborate.

Sometimes I want the agent to take the task and run with it. Sometimes
I want to hold the steering wheel while we decide where to go next.
Learning the difference was part of this simple, straightforward task.
