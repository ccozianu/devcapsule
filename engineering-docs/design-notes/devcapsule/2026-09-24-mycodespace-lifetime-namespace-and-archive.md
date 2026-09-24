# mycodespace: a lifetime namespace and archive for one programmer's projects

Design note geared toward specification and requirements. Written 2026-09-24
in the `user-docs` checkout at the product owner's explicit direction, from
a conversation that day; it belongs to `project-management` to adopt, amend
or reject. Status: proposed. Nothing here is implemented, and nothing here
authorizes implementation.

## 1. Purpose and positioning

mycodespace is the larger product DevCapsule will be part of. Its defining
function is a single person's view of all their programming activity over a
lifetime: one namespace in which every project they ever worked on is
listed, browsable from the tools they already use, and from which any
project can be materialized into a working capsule in one action.

The value has two layers, and the note is ordered by them:

1. **The everyday value is the view.** One place that answers "what have I
   worked on, where is it, what state is it in", and turns any entry into an
   open project on demand. This is what a person uses every week, and in v2
   it lives inside the IDE.
2. **The guarantee underneath is longevity.** Anything kept stays
   materializable, buildable and runnable decades after it was written,
   whatever happens to vendors, registries and forges. This is what makes
   the view trustworthy rather than a list of dead links.

Positioning, as decided by the owner:

- **A single person's view, as a matter of principle.** The owner's own
  itch, and in his judgment one of the largest unaddressed needs of the
  individual programmer: continuity across employers, machines and decades.
- **Reasonably usable by a small software company**, in lieu of a heavy-duty
  monorepo. Several people whose personal catalogs share records and an
  archive.
- **Not for organizations at the scale of a google3.** They keep their own.
- **Not a monorepo.** No atomic changes across projects, no single head, no
  one-version rule. The owner does not believe in monorepos; the product
  must not need one to work.
- **No filesystem layer.** The google3-like behavior wanted is "see
  everything, materialize only what you open", obtained from a catalog and
  an archive, not from a FUSE or virtual filesystem.

## 2. The defining scenarios

**Every week.** From the IDE, or a terminal, or a browser page, the person
opens the namespace, searches or browses to a project from any year, and
materializes it on demand. A capsule opens on the right toolchain with the
project's own state, and they work. Closing it keeps it. Nothing is checked
out that was not asked for.

**Twenty years later.** Someone writes a project today with a current
toolchain, say Java 21, and keeps it. Twenty years from now they open the namespace, find it,
materialize it, compile it, and run it, with the toolchain and dependencies
they used then, whatever has happened to the vendors, registries and forges
in between. The first scenario is the acceptance test for the view; the second for the
archive. Every requirement below serves one of them or the small-company
extension. The longevity promise is forward-looking: what is kept today
stays runnable.
Projects from before the product existed get a record (MC-CAT-3) and are
kept only where their inputs can still be gathered; the product does not
promise to resurrect what was never kept.

## 3. The budget envelope

Every requirement in this note must be implementable and operable inside
this envelope. Anything that needs more is a bonus if it arrives and is not
a requirement.

| Side | Envelope |
|---|---|
| Development | One person and three coding agents on flat-rate subscriptions, about $200 per month each, $600 in total. Additional collaborators or resources are a bonus. |
| Runtime, individual | A contemporary programmer's workstation with a graphical browser and a working Docker, or an alternative that runs Docker-compatible images. Local disk as the archive's truth. |
| Runtime, optional | One object-storage bucket as a replica, paid by the individual or the small company. No always-on service, no database, no server that must exist for the product to work. |
| Runtime, small company | The same, with a shared bucket. No central server is required for the product to function. |

A requirement that implies a hosted multi-tenant service, a custom
filesystem, a build system migration, or an operations team is out of
envelope and out of scope.

Reviewability is part of the envelope. Implementation languages are limited
to those the owner can review competently enough to push back on generated
code and direct refactoring: Python today, revisited when that changes. The
tool itself is small by design; section 8, *DevCapsule, part of a bigger
whole*, says what it depends on, what it must not depend on, and how it is
bootstrapped.

## 4. Vocabulary

- **Catalog**: a person's namespace. A git repository of plain-text records,
  one per project, owned and hosted however the person chooses.
- **Record**: one catalog entry. Names a project by path, such as
  `//java/2008/foo-app`, and says what is known about it.
- **Mirror**: a complete copy of a project's source history that the person
  owns, as a bare repository or a `git bundle`, stored in the archive.
- **Archive**: the person's content-addressed store of everything needed to
  materialize projects: mirrors, dependency snapshots, base images,
  toolchains. Disk is the truth; a bucket may replicate it.
- **Lock**: the DevCapsule per-project record of the exact environment: base
  image by digest, components by version, host authorizations.
- **Materialize**: produce a working directory and a runnable capsule for a
  record from the archive alone.
- **Keep**: bring a project's inputs into the archive so that it can be
  materialized later. A project is not kept until this has been verified.
- **Workspace view**: a set of records materialized as sibling directories
  for one human's convenience. This is what the submodules in DevCapsule's
  own repository approximate today.

## 5. Requirements

Numbered for reference; IDs are provisional until `project-management`
adopts them into `REQUIREMENTS.md`.

### MC-CAT: the catalog

- **MC-CAT-1** The catalog is a git repository of plain-text records readable
  without any tool. Its format must remain readable by a human in twenty
  years: TOML or YAML, no binary, no database.
- **MC-CAT-2** Every record has a stable path-shaped name under `//`,
  chosen by the person, and the name never changes once other records or
  notes refer to it. Renames are recorded as aliases.
- **MC-CAT-3** A record may describe a project whose sources the person no
  longer holds, such as work done for a former employer. It then carries
  what is known, when, with which tools, and an empty mirror field. A
  lifetime view must admit this honestly.
- **MC-CAT-4** A record names: origin URLs over time, the mirror's identity
  in the archive, the last known head, the lock, the project's status
  (`active`, `dormant`, `archived`, `lost`), and free-text notes.
- **MC-CAT-5** The catalog is browsable and searchable without materializing
  anything, from a terminal and from a page in the graphical browser.
- **MC-CAT-6** A catalog may include another person's catalog by reference,
  for the small-company case. Inclusion copies nothing; records resolve to
  the other person's mirrors or to a shared archive. Conflicting names
  are reported, never merged silently.

### MC-ARC: the archive

- **MC-ARC-1** The archive is owned by the person, lives on their disk as
  the truth, and may be replicated to one bucket. No third-party service is
  needed to read it.
- **MC-ARC-2** The archive is content-addressed. Every stored object is
  named by its digest and verifiable offline.
- **MC-ARC-3** The archive holds, per kept project: the mirror; a snapshot
  of the dependency cache the build actually used, such as a Maven
  repository subset or an npm cache; the base image as an OCI layout
  addressed by digest; and the toolchain binaries the lock names. Naming
  an image or a toolchain that exists somewhere else does not count.
- **MC-ARC-4** Storage formats are limited to ones with decades of
  demonstrated longevity: git objects and bundles, tar, OCI image layout,
  plain text. No format that needs the product itself to be decoded.
- **MC-ARC-5** `keep` verifies before it reports success: the mirror is
  complete, every object the lock names is present, and a materialization
  from the archive alone succeeds at least once.
- **MC-ARC-6** The archive can be exercised: a command materializes a chosen
  or random kept project from the archive with network access to third
  parties disabled, builds it, and reports. Bit rot is detected by digest
  verification. Both run within the workstation envelope; neither is a
  service.

### MC-MAT: materialization

- **MC-MAT-1** `materialize //path` produces a working directory and a
  DevCapsule capsule from the record, the mirror and the lock, using only the
  archive. It must not require the origin forge, a public registry, or a
  package mirror to exist.
- **MC-MAT-2** The capsule runs the recorded base image on the person's
  Docker-compatible runtime. Architecture drift is met by emulation when the
  runtime offers it, and the record says which architecture the image is.
- **MC-MAT-3** Materialization is sparse: only the requested records are
  materialized. Nothing is ever checked out because it is "in the tree".
- **MC-MAT-4** A workspace view materializes a named set of records as
  sibling directories. Each directory is an ordinary, self-contained
  repository; nothing in the view governs a member's checkout, branch or
  history. This replaces git submodules for the case of independent
  projects co-located for convenience.

### MC-VIEW: the namespace view

- **MC-VIEW-1** The namespace is browsable and searchable from three
  surfaces: a terminal command, a page in the graphical browser, and, in
  v2, a plugin inside the IDE the person is already using. All three read
  the same catalog; none needs a server.
- **MC-VIEW-2** From any surface, one action on a record materializes it
  and opens it: a capsule on the recorded toolchain with the project's own
  durable state, in the IDE the record or the person prefers.
- **MC-VIEW-3** The view shows each record's status, last activity, and
  whether it is kept, dormant or lost, so that a lifetime list reads as a
  map and not as a graveyard of equal-looking entries.
- **MC-VIEW-4** The IDE plugin is a thin client over the catalog files and
  the tool. It targets one IDE family first, the VS Code family that
  DevCapsule already provisions as `codium`, then JetBrains and Eclipse as
  budget allows. It must work from inside a capsule as well as from the
  host IDE, since that is where a person is when they want the next
  project.
- **MC-VIEW-5** The plugin adds no format and no state of its own; a
  person without it loses convenience, never data.

### MC-DEG: degradation to plain tools

- **MC-DEG-1** Every artifact in the catalog and the archive is usable with
  `git`, `tar` and a Docker-compatible runtime alone: a catalog is read
  with `git` and `cat`; a mirror is restored with `git clone` of a bundle;
  an image is loaded from its OCI layout; a dependency snapshot is untarred
  into place; a workspace view is materialized by a shell loop over its
  manifest.
- **MC-DEG-2** Every record carries a plain-text restore recipe naming those
  commands for that project, so that a person or an agent in 2046 with no
  `mycs` can still follow it.
- **MC-DEG-3** The exercise in MC-ARC-6 runs the by-hand path as well as
  the tool path, so the fallback is proven, not assumed.
- **MC-DEG-4** The tool keeps itself: its source and a built executable are
  kept in the archive like any project, and every record names the tool
  version that kept it.

### MC-DEV: fit with DevCapsule as it exists

- **MC-DEV-1** The existing per-project lock is the lock this note relies
  on. Its content must be sufficient for MC-ARC-3; where it is not, the gap
  is a DevCapsule requirement, not a mycodespace one.
- **MC-DEV-2** DevCapsule's own repository becomes a workspace view: the
  website and the sample projects are records with pins, materialized as
  siblings by the view command. Submodules with embedded git directories
  are the accepted interim implementation; nothing new is built on them.
- **MC-DEV-3** The website's pin on a DevCapsule content revision and
  DevCapsule's pin on a website revision are ordinary record pins, not
  gitlinks, once MC-MAT-4 exists.
- **MC-DEV-4** The lock names the DevCapsule version that wrote it, not
  only the resolution matrix it came from, so that a kept record can name
  the exact executable to materialize with. Today it records the matrix
  identifier alone; this is a DevCapsule gap.
- **MC-DEV-5** DevCapsule can start a capsule from an image loaded locally
  from an archived tar, without a registry, and with network access to
  third parties denied as an explicit authorization. This is what makes
  offline materialization a DevCapsule feature rather than a mycs trick.
- **MC-DEV-6** DevCapsule never calls mycs and never reads catalog or
  archive records. It may consume an archive artifact handed to it as a
  plain file. The dependency runs one way; see section 8.

### MC-CO: the small-company extension

- **MC-CO-1** Collaboration on a project stays where it is today, on a forge
  with pull requests. mycodespace records and archives; it does not review,
  merge or host.
- **MC-CO-2** A shared archive is the individual archive's format on shared
  storage. Content addressing deduplicates across people by construction.
- **MC-CO-3** No requirement in this section may introduce a server that
  must be running for an individual's own catalog and archive to work.

## 6. Explicit non-requirements

- Atomic changes spanning projects, a single head, or a one-version rule.
- Directory-level ownership and visibility rules; a project's governance is
  its own repository's.
- A virtual or network filesystem presenting the namespace as a tree.
- A hosted multi-tenant service as a condition for any function above.
- Large-scale automated refactoring across projects.
- Guaranteeing that a project someone else hosts stays available. The
  product guarantees only what is in the person's archive.

## 7. Risks, stated honestly

- **Toolchain availability.** Vendors delist old builds, put them behind
  logins, or disappear; registries expire tags; forges delete repositories.
  A toolchain that is one download away today may be unobtainable in ten
  years. The archive must hold the binary at `keep` time, not a link to it.
- **Very old userland on new kernels.** The Linux kernel's userspace ABI is
  the strongest longevity guarantee available, and images from the early
  2010s still run, with known caveats such as the `vsyscall` setting for
  very old glibc. This is a risk to record per project, not a blocker.
- **Architecture drift.** x86-64 may become an emulated target. Emulation
  is slow but acceptable for "compile and run it once in 2046". Recording
  the image's architecture in the record is what makes that possible.
- **Licensing of archived binaries.** Keeping a JDK or a base image for
  personal reuse differs from redistributing it in a shared company
  archive. The small-company extension must state what may be shared.
- **Secrets.** A dependency cache or an image can contain credentials.
  `keep` must scan and refuse, or the archive becomes a liability.
- **Bucket retention.** A bucket is a replica because a vendor's retention
  policy is not a twenty-year contract; the disk, copied forward, is.
- **Budget.** Three agents at $200 a month is enough to build a catalog
  format, a `keep` that bundles and snapshots, and a `materialize` that
  runs a capsule offline. It is not enough for a filesystem, a service, or
  a build-system migration, which is why those are excluded.

## 8. DevCapsule, part of a bigger whole

This section records the design discussion of 2026-09-24 on how the tool
relates to DevCapsule, what it may depend on, and how the two are
bootstrapped without a cycle.

### The four primitives

The twenty-year promise rests on exactly four runtime dependencies, each a
format with a standard behind it, several independent implementations, and
decades of use:

1. `git`, for the catalog and the mirrors, with `git bundle` as the archive
   form;
2. `tar`, for dependency snapshots;
3. a SHA-256 implementation, for content addressing and bit-rot checks;
4. a Docker-compatible runtime, for images in OCI layout and for running
   the capsule.

If any of these vanished, computing as a whole would have a larger problem
than this archive. That is the whole confidence argument, and it extends to
nothing else.

### mycs is glue, not a platform

The tool is a few hundred lines of Python over those primitives. Its main
job is to refuse to say "kept" until every input is present and an offline
materialization has succeeded. The genuinely new parts are three: the record
schema, the `keep` verification, and the IDE plugin in v2. Everything else
is a subprocess call.

Other tools are accelerators, never dependencies. A workspace view is a
manifest and `git clone` in a loop, written and owned here; exporting a
manifest for `vcstool` or `repo` is a courtesy. The archive is a directory
of digest-named files with a checksum list; git-annex or a bucket sync tool
may replicate it. Images move with `docker save` and `docker load`;
`skopeo` is optional. The absence of any accelerator changes nothing. An
adopted tool is acceptable only if its output passes MC-DEG, or if it is
confined to the replica layer where the truth on disk does not depend on it.

Reviewability constrains what is written here, not what is run. A tool
maintained in a language the owner cannot review may be used; it may not be
depended on for the promise.

### The tool is a separate project

mycs is its own repository and release, not a `devcapsule` subcommand. It
shells out to the `devcapsule` executable and depends on it; nothing depends
on mycs. The repository boundary makes the direction structural rather than
a layering discipline inside one codebase. The cost is a second small
release. It ships as a PEX scie like DevCapsule; Java with `jlink` is the
recorded path if it ever needs to stand alone from Python, and the text
formats make that rewrite cheap.

### Dependency direction

- DevCapsule depends on git, a container runtime and its base images. It
  knows nothing of a catalog or an archive. It is a record in the owner's
  workspace, which is data about it, not a dependency of it.
- mycs depends on DevCapsule at run time, to materialize, and at development
  time, because it is built inside a capsule.
- The catalog and the archive are plain files; nothing depends on mycs to
  read them (MC-DEG).
- The IDE plugin depends on mycs and DevCapsule; nothing depends on it.

Two rules keep the graph acyclic. DevCapsule may consume an archive artifact
handed to it as a plain file, such as an image tar for `docker load`, but
never calls mycs or reads its records (MC-DEV-6). And mycs stays outside
DevCapsule's codebase, so the direction cannot erode by convenience.

### Bootstrapping

1. DevCapsule exists and is released. Done.
2. Create the mycs repository and open it with DevCapsule. Development needs
   nothing from mycs.
3. Write the first catalog by hand: a git repository with TOML records for
   DevCapsule, mycs, the website and the samples. No tool is needed to
   create it; MC-DEG works in the owner's favor on day one.
4. mycs v0 implements `keep`. Its first two kept projects are DevCapsule and
   mycs itself. Self-keeping is a fixed point, not a cycle: the output is
   plain files, and the record names the mycs version that produced them.
5. Prove the fixed point: materialize mycs from its own archive using only
   DevCapsule and the four primitives, build it, run `keep` again, and
   compare digests. When that passes, the archive can regenerate the tool
   that made it, and the tool is never the only way back in.

In 2046 the chain is: `git clone` the bundle, `docker load` the image, run
the kept DevCapsule executable, open the capsule. Without the executable,
the fallback in the record's recipe is `docker run` on the kept image with
the source mounted.

### What DevCapsule must provide

MC-DEV-4 through MC-DEV-6 above: the lock names the DevCapsule version, a
capsule can start from a locally loaded image with third-party network
denied, and DevCapsule never depends on mycs. The archive keeps the
DevCapsule executable as a toolchain artifact like any other.

### Relationship to existing records

- `R-PRODUCT-001` batteries-included environments and `R-PRODUCT-002`
  explicit host boundaries define the capsule that MC-MAT materializes.
- `R-PRODUCT-003` durable human/agent project memory is the per-project
  half of continuity; this note is the across-projects, across-time half.
- `R-UPGRADE-001` component version sets are what the lock records; the
  archive keeps what they name.
- The 2026-09-23 conversion of the `website` submodule to an embedded git
  directory is the interim in MC-DEV-2, recorded in agent memory and in the
  website's `WORKFLOW-LOCAL.md` exceptions.

## 9. Open questions for the owner

1. Is the bucket replica part of the first slice, or is disk-only the first
   deliverable with replication later?
2. For third-party repositories merely referenced, does `keep` mirror the
   whole history or only the commit used? Whole history is safer and
   larger.
3. What counts as "compile and run" for the acceptance scenario: a build
   command recorded in the lock, or a person-written note per project?
4. Should the catalog be one repository per person, or one per person per
   domain of life, with inclusion joining them?

## 10. Suggested slices, inside the envelope

**v1** delivers the catalog, `keep`, `materialize`, and the terminal and
browser surfaces of the view. **v2** delivers the IDE plugin, MC-VIEW-4,
which is where the everyday value becomes obvious. The plugin waits for v1
because it must not invent state of its own (MC-VIEW-5).

### First slice

1. The record format and a hand-written catalog with the owner's current
   projects as records, including at least one `lost` record from a former
   employer, and a workspace manifest for this repository's siblings.
2. `keep` for a git project: `git bundle` the mirror, `tar` the dependency
   cache, `docker save` the base image, write the digest list, verify
   offline. First kept: DevCapsule and mycs.
3. `materialize` for the same projects into a capsule with third-party
   network denied, and a passing build. The fixed-point check of section 8.
4. A small Java 21 sample project, written and kept now, added to the
   sample projects as the standing acceptance fixture for the defining
   scenario. MC-ARC-6 exercises it from the archive at every release, so the
   evidence that "kept today stays runnable" accumulates year by year rather
   than being claimed.

Each step is a few days of one human and agents; none needs a service.
The plugin is a separate slice after these, scoped to one IDE family.
