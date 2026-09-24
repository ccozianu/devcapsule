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
listed, and from which any project they still hold the inputs for can be
materialized, built and run decades later.

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

## 2. The defining scenario

Twenty years from now, the owner opens the namespace, finds a Java 1.6
project from 2008, materializes it, compiles it, and runs it. This is the
acceptance scenario for the whole design; every requirement below either
serves it or serves the small-company extension of it.

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

- **Toolchain availability.** Oracle's JDK 6 already sits behind a login;
  OpenJDK 6 builds from other vendors exist today and may not tomorrow. The
  archive must hold the binary at `keep` time, not a link to it.
- **Very old userland on new kernels.** The Linux kernel's userspace ABI is
  the strongest longevity guarantee available, and images from the early
  2010s still run, with known caveats such as the `vsyscall` setting for
  very old glibc. This is a risk to record per project, not a blocker.
- **Architecture drift.** x86-64 may become an emulated target. Emulation
  is slow but acceptable for "compile and run it once in 2046".
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

## 8. Relationship to existing records

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

## 10. Suggested first slice, inside the envelope

1. The record format and a catalog with the owner's current projects as
   records, including at least one `lost` record from a former employer.
2. `keep` for a git project: bundle the mirror, snapshot the dependency
   cache, save the base image as an OCI layout, verify offline.
3. `materialize` for the same project into a capsule with third-party
   network disabled, and a passing build.
4. A Java 6 sample project added to the sample projects as the standing
   acceptance fixture for the defining scenario, exercised by MC-ARC-6.

Each step is a few days of one human and agents; none needs a service.
