# Work Order: Base Images As A Contract (Design Experiment)

Prepared 2026-09-26 by the product owner, Costin Cozianu, with the agent that
did the first implementation. This is the task contract for an independent
human/agent pair, or several agents coordinated, to accomplish the same work
autonomously under different settings: effort level, coordination scheme,
model. It is an experiment in how to use LLM agents well; it does not feed
the main development line. The pair starting from this document does not
need, and must not consult, the conversation or the branch that produced
the first implementation.

## Starting point

- Clone `https://github.com/ccozianu/devcapsule` and check out the tag
  `v0.2.14` (commit `abb785d`). That is the clean state.
- Read `AGENTS.md`, `README.md`, `DEVELOPING.md`, `WORKFLOW.md`,
  `WORKFLOW-LOCAL.md` as the repository instructs. The required gate is
  `nox -s build` from `devcapsule-src` (see *Validation* below for the
  scratch-space caveat).
- Work on a branch named `experiment/<your-setting>/base-contract`, from
  the tag. Do not publish workstream state to the `coordination` branch and
  do not send workflow mail: the experiment must leave the project's live
  coordination untouched. Record this as the experiment's declared
  exception in your own status notes on the branch.
- Deliver a pull request against `main` from that branch. The owner
  reviews; the pull request is not merged.

## The problem, in the owner's words

While dogfooding 0.2.14 on a second checkout of this repository, the owner
ran `devcapsule project config authorize base-image default` and observed
that it "sent the base image back to 0.2.12-rc5". The owner asked: how does
a user upgrade the base image to the one supported or recommended by the
tooling, as opposed to the one recommended by the project's `.toml`?

Investigation established that the recommended base is the same image for
both, and that the name shown, `v0.2.12-rc5`, is the release candidate that
built it, while Docker Hub also tags that image `v0.2.12`. The owner:

> At the very least we should have it as 0.2.12 not 0.2.12-rc5, that's a
> miss on our part.

Then, redirecting a discussion of renaming options to the question
underneath:

> So what is a BaseImage? A class which we don't have in `base_image.py`,
> mind you! It is a pre-built docker image that we can utilize in a `FROM`
> clause as the main base to build the end docker image that the devcapsule
> runs with! As simple as that. How is it built? It is built once, from
> `devcapsule.pex` with the corresponding CLI option `devcapsule images
> build ...`; the recipe for building the base image is inside
> `base_image.py`, so on one hand it makes sense to label it from the
> version of the tool, but on the other hand not so much!
>
> From the perspective of the software contract, we are interested in what
> services the base image provides and when the contract changes, in an
> incompatible way!

And the standard the work is held to:

> Take the above as a challenge and run with it. I want to see how good you
> are in writing "beauty is our business" (Dijkstra) and "obviously no
> deficiencies" (Hoare) kind of software. The goal is to write something
> that can be shown as an example of good software design: simple,
> effective and getting to the core of solving a user need, while utilizing
> the power of abstraction.

## What must be accomplished

The owner asked for a pull request that fixes the current problems while
taking care of these issues:

1. **Make it clear to the user what they approve when they approve, and
   where it comes from.** Upon inspection, tell the user what that base
   image is; a permalink to GitHub could serve.
2. **Do not prompt the user for approval unnecessarily.**
3. **Make it clear to the user which base image is compatible or
   incompatible with which other components, and why**, without imposing
   unnecessary burdens on software maintainers. Compatibility should be
   based on contract version, following the regular API compatibility
   scheme: adding a method keeps the API compatible with components that
   relied on the smaller version; removing something does not.

A design note explaining the abstraction chosen, written for a reader who
will decide together with the owner, is part of the deliverable. Update
the user-facing documentation the change touches.

## Facts about the code at the tag, for orientation

These are observations, not instructions. Verify them.

- `devcapsule-src/devcapsule/base_image.py` holds the base recipe, versioned
  by `BASE_RECIPE_VERSION` (currently `9`), and labels every image it builds
  with, among others, `devcapsule.base.recipe`, `devcapsule.base.recipe-version`,
  `devcapsule.base.display`, `devcapsule.base.runtime`, component versions,
  and the builder's source revision and release mnemonic.
- `devcapsule-src/devcapsule/resolution_matrix.py` embeds the resolution
  matrix (`embedded-20`): base pins named by the release that built them
  (`v0.2.8`, `v0.2.10`, `v0.2.12-rc5`), each with a `base_family`, a set of
  satisfied capabilities and a lock fragment (`reference` at an immutable
  digest, `build-mnemonic`); component pins; and "verified edges" recording
  a component version validated on a base family. D-0007 in
  `engineering-docs/decisions/product/` and its 2026-09-06 amendment define
  the base family and when a new one opens.
- A project's platform lock (`.devcapsule/devcapsule.linux-amd64.lock`) copies
  the pin's lock fragment into its `[base]` table. The messages a user sees
  ("Execute DevCapsule v0.2.12-rc5 at the exact registry digest ...") read
  the lock's `build-mnemonic`.
- The checkout's base consent (`config authorize base-image`) records the
  reference and a digest of the entire lock; `devcapsule/configuration/authorization.py`
  treats any lock change as invalidating the consent. D-0004 records the
  consent design. A test in `tests/configuration/test_architecture.py`
  forbids the configuration core from importing the matrix and other
  adapters.
- `devcapsule project versions ...` implements per-checkout version sets for
  components (R-UPGRADE-001); the base is not a selectable member.
- The 0.2.14 release notes in `engineering-docs/releases/v0.2.14/README.md`
  and the bug table beside it describe the release the tag closes.

## Constraints

- Budget: one human and a small number of agents on flat-rate subscriptions;
  a workstation with a browser and Docker. No services, no paid provisioning.
- Reviewability: Python, in the repository's existing style; the owner must
  be able to hold the code to the Hoare standard on review.
- Compatibility: R-COMPAT-001 (`engineering-docs/requirements/product/`)
  applies. A change that makes an existing checkout ask its user for
  something must be justified as that requirement demands, or avoided.
- No new base image is published and no registry is written to during the
  experiment.

## Validation

- `nox -s build` from `devcapsule-src` must pass on the final tree. On a
  machine whose `/tmp` is a small tmpfs, point pytest's scratch elsewhere,
  outside the home directory and the project mount:
  `PYTEST_ADDOPTS="--basetemp=/opt/<dir>/pytest"`. Read the gate's own exit
  code; do not infer success from a wrapper's.
- Show the user-facing result: the consent prompt and the inspection output
  on a scratch copy of this repository's manifest and lock, with isolated
  `XDG_*` directories so no real checkout is touched.
- Tests that encoded behaviour you deliberately change must be rewritten to
  the new rule with the reason in a comment, never deleted.

## What the owner will compare across attempts

- Whether the three issues above are met, judged from the user's seat.
- The abstraction: does the design get to the core of the user need, and
  would the owner show it as an example.
- Size and shape of the change: modules touched, lines, tests added and
  rewritten, documentation updated.
- Cost: wall time, gate runs, tokens or agent turns, and how many decisions
  had to be escalated to the owner versus made and explained.
- Honesty of the record: what the status notes claim against what the
  branch shows.
