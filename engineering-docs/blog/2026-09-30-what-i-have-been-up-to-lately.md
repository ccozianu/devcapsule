---
description: "One LLM writing a work order for the next, with tooling three of them built together: what a DevCapsule project looks like from the inside, and what it takes to try it."
---
# What I have been up to lately

*September 30, 2026. First posted on [LinkedIn](https://www.linkedin.com/posts/costin-cozianu-0a36a95_devcapsule-devcapsule-share-7510067200989224962-ZTA3/)
on September 28; reproduced here, lightly edited, so it can be linked from
places with shorter limits.*

```text
Ran git switch -c ws-project-management/coordination main
 │ devcapsule workflow claim 'Prepare fair smartgalati-test4 implementation work order'
 │ cat scripts/gcs/config.env codex-astra-site/README.md

 └ project-management: claim recorded for 12 h
  # ==============================================================================
  … +141 lines (ctrl + t to view transcript)
```

This is one LLM, using the tooling we developed together (me and three
LLMs) to create a work order for the next LLM. Thanks to
[DevCapsule](https://devcapsule.mycodespace.ai).

A DevCapsule project is LLM-independent: you can run LLMs in parallel on
different tasks, or switch to another LLM in the middle of an implementation
task, without losing any context. As a human, use (almost) any IDE you may
want. You don't need JIRA, you don't need UMLs in IBM Rational Rose (anyone
remember that?), as the LLMs coordinate and run project management (with
your blessing, of course). They write bug reports and document design
issues; from discussion to decisions, it all lives and breathes in the
source tree, so every bit of context about the project is available to all
the LLMs and all the humans working on it.

What's most important: the next human onboarding a DevCapsule project has
to just `git clone`, then `devcapsule project init` to review and approve
what the project asks to run on their computer, and then
`devcapsule project run`. That middle step is not ceremony, it is the whole
point: nothing runs on your machine that you haven't seen and said yes to.
Not a base image, not a vendor download, not the host access an LLM would
love to have. You don't let software you're not aware of run on your
computer, and neither does DevCapsule.

What it buys you as a developer:

- **Onboarding in minutes, not hours or days.** Clone, approve, run.
- **A reproducible development environment**, with state-of-the-art software
  engineering at your fingertips. Or go your own way!
- **Tame the LLM.** The `rm -rf $HOME` stories stop at the capsule's wall.
  Then unleash it where it belongs: writing the code, solving the problem.
- **Leave and come back.** A month later, your IDE, your agents and your
  tools are exactly as you left them.

The only dependency we want on the local machine is either Linux or Windows
(Mac maybe next month), a working Docker installation (use WSL2 on Windows)
and a working browser. A working X desktop on Linux provides a smoother UI
for the time being, but it is not necessary. I do my dogfooding mostly in
the browser, with only one full-desktop instance to make sure it doesn't
break.

DevCapsule is a proof of itself: it's been developed this way for the past
two months, with Gemini, ChatGPT and Fable 5. More options are coming very
soon (with the speed of AI development, of course).

I'll save the lessons learned for another post, because I am in the middle
of fabulous learning.

Will be grateful for anyone brave enough to [try it](https://devcapsule.mycodespace.ai/docs/current/getting-started/first-session/),
[file bugs](https://github.com/ccozianu/devcapsule/issues/new), send PRs, of
course. But more about this later.
