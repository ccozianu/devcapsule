# Local Workflow: The Reasons

*For humans.* This file explains [`WORKFLOW-LOCAL.md`](WORKFLOW-LOCAL.md). It
carries no rule. For each section it repeats the rule, states its intended
effect, and gives the motivation, most of which is an owner direction with a
date.

## The Two Halves

**Rule.** `WORKFLOW.md` binds where it speaks; this file binds where it is
silent; the root `WORKFLOW.md` is the source of the packaged definition.

**Intended effect.** Contributors can rely on the generic half being the same
everywhere and find the project's own facts in one place.

**Motivation.** DevCapsule is also the project that develops the generic
definition, so its root `WORKFLOW.md` is the source rather than an installed
copy. That is an exception by the definition's own rule and is recorded as
one. Everything else in the local file is what any adopting project would
record.

## Version Scheme

**Rule.** PEP 440; `X.Y.Z.dev0` between releases; the release branch's first
commit sets or confirms `X.Y.Z`; `main` reopens at the next patch; candidate
and local markers are never authored; one authored copy, mirrored by two
frontmatters, set by one command.

**Intended effect.** The source always orders correctly against the release it
works toward, and the three copies of the version never disagree.

**Motivation.** The `dev0` form is what pip and NumPy carry on their main
branches; the suffix stays `dev0` because the commit identifies the build.
Candidate builds are stamped from their tags and local builds from their
environment, so authoring either in the source would make the source lie about
what it is. One command sets all three copies and the gate checks they agree,
because a mismatch between the declaration and the definition's frontmatter is
reported as a defect by the tooling.

## Release Policy And Documentation Refs

**Rule.** The operator guide is the policy; default ref spelling; GitHub
Actions builds candidates; a resolved main disposition gates each candidate;
downloaded-artifact smoke evidence is required; a release includes its
documentation; `docs-<version>` branches carry post-release documentation
corrections and are never merged or rebased.

**Intended effect.** A release is reproducible from its tag, its documentation
is published for its version, and a released version's guides can be corrected
after the fact without touching its source.

**Motivation.** The documentation obligations date from 2026-09-28, when the
owner found the website unpublished since 2026-09-21 and the guides pinned to
an old version. The `docs-<version>` ref exists because the definition closes a
release branch after its final tag while the website publishes each version's
documentation from that version's own source; the branch is where a released
version's guides are corrected. It is never merged because it is not source
and never rebased because the website reads it. The candidate gate does not
apply because nothing executable changes; the website's build check does
because that is what the branch feeds.

## Blog Entries

**Rule.** On request, write a dated entry under `engineering-docs/blog/` with
the blog front matter, attribute quotations, link evidence by mainline SHA, and
index it.

**Intended effect.** The human's request supplies the topic and occasion, and
the website picks the entry up without further ceremony.

**Motivation.** The website reads the date from the filename and the draft flag
from the front matter, so those two facts are the only website-specific
requirements. Mainline SHAs keep evidence links stable when branches are
deleted. There is no proposal, schedule, or approval procedure because the blog
is the owner's voice, released by the owner.

## Validation Commands

**Rule.** Every command runs from `devcapsule-src` in its `.venv`; the kinds
are the definition's; each has a command runnable as written; the gate is
`nox -s build`.

**Intended effect.** Any agent on any machine can build and test the project
without guessing, and "the tool is missing" is a finding only after following
the section.

**Motivation.** The definition makes this section required because it is what
lets a contributor act without asking. The `.venv` is the only place the tools
live so that a check never depends on what else is installed. The `/tmp`
remark exists because a capsule's `/tmp` is a 2 GB tmpfs that the gate's
scratch overflows, which cost a resumed session a failed gate before the cause
was found.

## Reasoning And Code Navigation

**Rule.** Start from the contract, state the uncertainty, navigate from the
entry point, search by pattern only as a last resort and say why, and never
treat a match as proof.

**Intended effect.** An agent reads the code that answers the question rather
than the code that matches a word.

**Motivation.** Pattern searches are cheap and feel productive, and they are
the most common way an agent convinces itself that a contract holds when it
has only found a name. Reasoning from the contract first makes the code read
targeted, which is both cheaper and more reliable.

## Component Status Publication Ref

**Rule.** `component-status` is a generated branch the action advances by
fast-forward; never a workstream, never merged, never force-pushed.

**Intended effect.** The compatibility feed and status page publish without a
human and without touching `main`.

**Motivation.** A generated branch that anyone could select as a workstream
would eventually receive authored commits; keeping it out of the workflow's
vocabulary keeps the action the only writer.

## Host Capabilities

**Rule.** The `[host.*]` tables declare what the checkout needs with
justifications; the coordination baseline records the hosting facts.

**Intended effect.** Every host access this project takes is declared and
justified in one place.

**Motivation.** The product's own containment model asks adopters to declare
host access; the project holds itself to the same rule.

### Dogfooding CLI Selection

**Rule.** The configuration recommends `devcapsule0`; the shipped runtime is
`devcapsule0` and the development installation is `devcapsule`; use each
deliberately; never fall back silently.

**Intended effect.** A test against released behavior and a test against
current work are never confused.

**Motivation.** Owner direction of 2026-09-24. A development capsule that runs
inside DevCapsule has two launchers available, and a silent fallback from one
to the other is how a passing check stops meaning anything.

### Keep The Development Checkout Launchable

**Rule.** Commands are the only writers of configuration; validate with the
running `devcapsule0` before and after any change; an inspection is not a
validation; self-hosting is a managed exception with an identifiable baseline
and an independent recovery path; 0.3 distinguishes mandatory from optional
needs.

**Intended effect.** The shared checkout can always be launched by a known
launcher, and a contribution from a newer launcher degrades gracefully rather
than breaking older ones.

**Motivation.** On 2026-10-04 a component commit changed the shared need and
lock and made the checkout depend on a launcher that had not shipped; the
owner recovered by hand with an incidental build. The 2026-10-05 correction,
"be liberal in what we accept and conservative in what we produce", reframed
compatibility as a contract between contributors with different launchers
rather than a frozen vocabulary. Command-only writes exist because a hand edit
can produce a document no command would have written and no reader can
explain. The validation steps exist because the running instance is the only
launcher known to work. The inspection remark exists because `config list` was
mistaken for a validator. Rule 9 is R-CONFIG-001, now implemented on `main`.

### Local Launch Networking

**Rule.** Host networking for local development and release-validation
launches, as standing authorization; declared network modes in tests stay;
record any fallback.

**Intended effect.** Local launches reach host-bound development services
without a permission dialogue every time.

**Motivation.** Owner direction of 2026-09-24. The authorization is standing
because asking for it on every launch is ceremony without information; it is
local because the product's defaults for other projects are a separate
decision.

## GitHub Integration: Owner Through The UI

**Rule.** Agents fetch and push over SSH; the owner operates GitHub through the
UI; `gh` is not an integration tool; no probing of connectors; concise UI
handoffs.

**Intended effect.** Pull-request integration stays an explicit owner act, and
agents never discover a credential and use it.

**Motivation.** Owner direction of 2026-09-21, when no `gh` installation
existed and probing for one wasted sessions. Note for the owner: on 2026-10-08
the owner installed `gh` in this environment and directed agents to use it to
open pull requests and comment on reviews. The rule text above is kept as
written because this edition changes no rule's meaning; the section is due for
an owner update, and project-management has recorded that.

## Commit Authorship

**Rule.** The human's author identity with a `Co-authored-by` trailer per
contributing agent, naming the actual model; verify before pushing; no
rewriting of merged history.

**Intended effect.** Authorship reflects who directed the work and which agent
contributed, and attribution is honest about the model.

**Motivation.** Owner direction of 2026-09-22. Pushing credentials and the
person who clicks merge are not authorship. The model name is read from the
active session because configured defaults and prior sessions have produced
wrong attributions.

## Workflow Definition Changes

**Rule.** Every change to the definition or the local file is written in the
controlled style, in the topic it belongs to, with its reason in the humane
companion in the same commit, a *Changes* entry for every change of meaning,
the parsed headings kept, and the packaged copy regenerated at the release.

**Intended effect.** The rule files stay short and uniform for agents, the
reasons stay complete for humans, and the two never drift apart.

**Motivation.** Owner direction of 2026-10-09, taken the day the
controlled-language edition merged to `main`. The same-commit rule is the
hand-operated form of the dependency that topic 12.12 of `WORKFLOW.md`
describes; when the web console's view registry tracks a paragraph's
dependency on its rule and marks it stale, the rule relaxes to keeping that
dependency fresh. The edition cut the agent's
required session-start reading by about a quarter and the share of sentences
over twenty words from a third to a tenth, while a fidelity quiz answered from
the new text alone came back complete. Those gains last only if every later
change keeps the split; a single reason written into the rule file is the
first step back to the mixed prose the edition replaced. The same-commit rule
exists because a companion paragraph added later is a paragraph never added.
Regeneration at the release matches the definition's own rule that the version
is the release: adopters receive the edition that shipped. The owner took this
decision in project-management, low ceremony, although the subject is
`workflow-improvements`' business, because the rule had to exist before the
next definition change rather than after it.

## Integration Method And Exceptions

**Rule.** Merge commits since 2026-10-03; four recorded exceptions:
release-fix propagation by judgment, the root definition as source, two
adoption exceptions, and pre-`ws-` branch names.

**Intended effect.** Every departure from the generic rules is visible, dated,
reasoned, and has an end condition.

**Motivation.** The release-fix exception exists because the generic rule's
blanket merge-only policy would hold unrelated work back or leave `main`
without a fix; the owner ruled on 2026-09-22 that engineering judgment chooses
merge, cherry-pick, or evidence that `main` lacks the bug, with the disposition
recorded on the bug. The adoption exceptions record history rather than
rewriting it. The branch-name exception records a migration the owner deferred
past 0.2.14 so that candidates were not held for a rename.
