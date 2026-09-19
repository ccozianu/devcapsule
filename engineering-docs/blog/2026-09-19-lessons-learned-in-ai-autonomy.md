# Lessons learned in AI autonomy over a simple, straightforward task

*September 19, 2026. This was written by either Costin Cozianu or by
Gpt-6-Astra, reflecting the perspective of the "human" on a short software
development exercise.*

After our earlier arguments about AI autonomy, I wanted to try something
smaller. Give the agent a straightforward task, let it get on with the work,
and allow enough budget that running out would not be the interesting part.
Then see what happened.

A website for DevCapsule seemed a reasonable choice: a landing page,
documentation, and a development blog. It should look professional, be
pleasant to read, and present the project better than GitHub's Markdown
view. No comment database, no grand application hiding behind the word
website.

We wrote a [work order](https://github.com/ccozianu/devcapsule/blob/80321ecc14093ab5585b3eeee7e4fe78a9097b4c/engineering-docs/work-orders/2026-09-16-website-autonomy.md).
The content would stay in the DevCapsule repository; the website machinery
would have its own repository, included as a submodule. Framework,
appearance, navigation, publishing approach: the agent could choose.
It was to gather its human setup needs at the beginning, then work
independently until it had a preview for me to review.

This time, choosing the design without asking me about every detail was
the assignment.

I allowed up to the subscription month's allowance and the three usage
resets reported available. A generous ceiling, with no obligation to hit it.
We had no reliable expenditure telemetry, so I cannot tell you exactly what
we spent, or what fraction of the budget it represented. We did not stop
because the budget ran out.

And the agent produced a website I liked.

It looked good on localhost. The documentation was readable, the links
worked, and the blog had a home. Mobile layouts and accessibility received
useful checks. Eventually we had a test site, production, and a way to
promote the tested files without rebuilding something different at the last
moment.

I gave the experiment an A−. Generously, as I told the agent, and partly
for encouragement. I particularly appreciated its willingness to point out
shortcomings in its own work.

Then we started finding more of them.

The first distinction was between a good-looking preview and a website
I could confidently operate. We had originally agreed to stop at the
preview. I then asked to take it live before finishing the review, which
expanded the job. It would be unfair to count every production concern
as an explicit requirement from the outset. Going live did, however, give
us an excellent way to find out what the design had assumed.

Publishing involved two repositories and GitHub Actions. An early approach
asked me to create a personal access token, with an expiration date,
to read build artifacts from my public project. I objected. Why acquire
a credential-renewal chore just to publish public material? We changed
the mechanism to use public release assets.

The original approach could have worked. The objection came from the
person who would have to keep it working.

The workflow controls took some deciphering too. To deploy the test site,
I had to select a mode called production. The default, preview, built an
artifact and deployed nothing. A run could finish successfully with both
the deployment and candidate jobs skipped. Other accepted combinations
of inputs could deploy a test build that I could not promote.

A green workflow was answering a narrower question than I thought I had asked.

I also had to ask for a visible build timestamp. Until then, a visitor
had no obvious way to tell when the site had last been built. None of
this required an exotic failure. I was trying to publish my website and
understand what I was looking at.

Then I searched Google for a word on the production site. Nothing.
Bing did not find it either.

The pages were accessible, their production canonical URLs looked right,
and crawling was allowed. There was no sitemap. The empty search results
did not tell us that GitHub Pages was broken or that our implementation
was blocking search engines. They did tell us that we had checked whether
the site could be read without establishing whether people could find it
through search.

Discovery improvements were somewhere in the agent's follow-up list.
I promoted search discoverability to W00. Sometimes prioritization requires
adding a number smaller than the numbers already assigned.

Google's ownership verification found another assumption for us. It wanted
a small HTML file at the website root containing a verification response.
Our checker expected every HTML file to have the structure of a normal
page; promotion expected every HTML file to have a canonical URL.
An ordinary ownership file satisfied neither expectation.

We added the file and a narrow exception to validate its contents and
preserve it through publication. Verification worked. Search Console
then said it was processing the indexing data. At the time of writing,
we were still waiting to establish whether the site was indexed, so W00
remained open.

A less visible problem bothered me more. What, exactly, was the contract
between the content producer and the website builder?

We had documentation listing the files the builder consumed. We also
had code relying on particular README headings and paragraph positions.
We lacked a sufficient, agreed interface specification. Which structures
could an author rely on? What happened to drafts? How was navigation
determined? Which changes were compatible, and how would an author learn
that something was wrong?

If I disappeared tomorrow, my replacement should not need to commission
another AI to reverse-engineer those decisions.

Writing down what the code did would help. We would still have to agree
whether that behavior was the contract we wanted, and talk through the
responsibilities on each side.

During the review, we clarified those responsibilities. DevCapsule owns
the content. The website project owns appearance, website functionality,
and publishing. Work items belong with their owners, even though the
experiment began in the parent repository. Where a task spans the two,
it needs a clear dependency; keeping two copies of a vague task helps
neither project.

What about visitors? Could I see how many people came, where they came
from, which guides they read, whether the experience worked for them?
There was no analytics implementation.

We initially treated that as another omission to examine. Then I recalled
that we may have intended to add it in a second step. I explicitly said
we would not count it against the initial implementation, and we put it
in the backlog.

A defect, a decision we had not discussed enough, and a useful next feature
deserve different treatment in a review. Wanting something now does not
prove the agent failed to deliver what we agreed then.

Meanwhile, merely recording the problems gave us another one.

I asked the agent to make search discoverability the first backlog item.
It edited the Markdown. It also ran the parent project's full build gate:
hundreds of tests, executable construction, packaging integration checks.
There were branch operations, bookkeeping, repeated progress polls.

All to write down that people should be able to find the website.

Our repository rules required the full gate before a checkpoint. The agent
treated this small update as a checkpoint and followed the rule literally.
The instruction was blunt, and the agent gave too little thought to what
all this evidence was worth. Running the build again told us nothing
about whether the new backlog sentence was useful or correct.

I want local rules that connect changes in the source tree to the software
contracts they affect, so we run the relevant checks when they matter.
Some belong on every commit; others belong before a pull request reaches
main. Content changes deserve content checks, publishing changes publishing
checks. Before running a check, we should be able to say what it might catch.

I had noticed a difference between the earlier Sol model and the current
Astra model. Whether the model caused it, I cannot say: the context,
instructions, and task history were not held constant in this experiment.
But our instructions need to work across agents. Changing the model
deserves attention even when the workflow files stay the same.

The waste bothers me beyond the time it takes. Subscription pricing may
hide the marginal cost of another command or another thousand tokens;
the computing resources, electricity, and human attention still cost
something. We did not measure energy use here. We do not need a dramatic
carbon calculation to ask what useful question a repeated test answers.

I can see the apparent contradiction: I gave the agent autonomy, then
criticized decisions it made on its own. Finding out where that arrangement
worked was the point of the experiment. The visual implementation succeeded.
The operational assumptions, interface contract, and validation habits
needed more involvement from me.

I would rather write the website myself than spend the afternoon authorizing
commas. I want the important assumptions brought into view, an honest
account of what is missing, and an agent that can stop executing when
we need to think together. Making me approve every command would not
get us there.

The A− stands. I have a website I like, a publishing mechanism that works,
and a more useful backlog than we had at the first review. We also have
concrete changes to make in how we collaborate.

Sometimes I want the agent to take the task and run with it. Sometimes
I want to hold the steering wheel while we decide where to go next.
Learning the difference was part of this simple, straightforward task.
