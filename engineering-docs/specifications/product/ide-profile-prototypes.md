# IDE Profile Prototype Specification

Status: accepted product specification; release target undecided.

Requirements: `R-SETTINGS-001`, `R-PRODUCT-001`, `R-PRODUCT-002`,
`R-STATE-001`, `R-CONC-001`

## Purpose

DevCapsule should give a developer the familiar IDE starting point they would
normally carry across related projects without mounting one live, writable IDE
profile into several capsules. It does this by maintaining one default
prototype for each compatible IDE identity and copying that prototype into the
independent state of each new project.

This specification covers IDE configuration and installed plugins. It does not
define general container-home sharing, agent-state sharing, project indexes,
cache reuse, or IDE installation. IDE and agent installations remain immutable
environment inputs and may already benefit from image and artifact caching.

## Terms

- **IDE profile prototype:** a developer-owned, read-only-as-a-source snapshot
  used to initialize later projects for one compatible IDE identity.
- **Project IDE profile:** the independent writable configuration and plugin
  directories used by one project checkout.
- **Eligible state:** the IDE-declared configuration and plugin state allowed
  into a prototype.
- **Clean start:** initialization with empty project IDE profile directories,
  bypassing the prototype.
- **Promotion:** explicit replacement of a prototype with a validated snapshot
  copied from one project's eligible state.

The prototype is not a shared runtime binding. A running capsule never mounts
the prototype itself read-write, and two projects never receive the same
writable project IDE profile.

## Prototype Identity And Compatibility

DevCapsule maintains at most one default prototype for each compatible IDE
identity. The identity includes the curated IDE component or family and enough
version, edition, platform, and state-format information to prevent silent use
of incompatible settings or plugins.

An implementation may allow an IDE's own supported migration path to consume
an older prototype, but it must make that migration visible and must not
overwrite the older prototype merely because a project was launched. If
compatibility cannot be established, the launch behaves as though no suitable
prototype exists or requires an explicit developer choice.

## Eligible And Excluded State

The curated IDE component declares which state is prototype-eligible. For the
PyCharm slice, the intended eligible categories are:

- IDE configuration and preferences; and
- installed IDE plugins.

The prototype excludes:

- project indexes and IDE system directories;
- logs, caches, downloaded-package caches, and other reconstructable state;
- the general persistent container home;
- source checkouts and project-local runtime data;
- agent homes, agent conversations, and agent credentials;
- host-access authorizations and developer-owned checkout resolution;
- active locks, temporary files, crash remnants, and other volatile IDE state;
  and
- any component state not explicitly declared eligible.

Prototype storage is personal developer state. It remains outside repositories
and images, uses restrictive workstation permissions, and follows the same
inspection and deletion principles as other durable DevCapsule state.

## Establishing The First Prototype

When no compatible prototype exists, the first normal project launch uses
empty project-local configuration and plugin directories. The launcher does
not capture them while the IDE is running.

After the first successful foreground IDE session exits, DevCapsule validates
the eligible directories. If validation succeeds, it copies them into a new
prototype transactionally. The prototype becomes visible only after the copy
and final verification complete. An incomplete copy is removed or retained as
diagnostic temporary state but is never selected as the default.

Minimum validity checks establish that:

- the foreground IDE process exited normally;
- no recognized IDE lock or writer remains active;
- every source is the expected managed project state rather than an arbitrary
  path discovered from IDE content;
- required eligible directories exist, are readable, and have acceptable
  ownership and permissions;
- volatile and excluded content is not selected; and
- the captured IDE identity and compatibility metadata are complete.

A crash, signal interruption, failed validity check, or failed copy does not
create a prototype. The launcher reports that automatic capture was skipped
and may show a recovery or explicit promotion command.

A clean-start request never replaces an existing prototype implicitly. If it
is used before any prototype exists, the first-successful-session rule still
applies and may establish the initial prototype after exit and validation.

## Seeding A New Project

Before the first normal IDE launch for a project with no project IDE profile,
DevCapsule selects the compatible prototype and performs an ordinary recursive
copy of each eligible directory into newly allocated project state.

The copy has these invariants:

- destination directories are independent and writable only as that project's
  state;
- no prototype file is hard-linked into the destination;
- no live directory is bind-shared between the prototype and the project;
- a partial or failed copy never becomes the project's selected IDE profile;
- failure leaves the prototype unchanged; and
- the launcher validates the completed destination before starting the IDE.

The accepted baseline is a physical copy even when the filesystem offers
copy-on-write cloning. Detecting or exploiting special filesystem behavior is
out of scope. The storage tradeoff is deliberate because typical IDE
configuration and plugin state is small enough relative to the saved setup
time and the isolation gained.

## Explicit Clean Start

The user-facing initialization or launch interface provides an explicit clean
choice. It creates empty, valid project-local configuration and plugin
directories, does not copy from the prototype, and does not modify or delete
an existing prototype. With no compatible prototype yet, the first successful
clean-start session may establish one through the normal initial-capture rule.

The effective choice must be visible in inspection output. A committed project
may recommend a clean start only through the normal configuration model; it
cannot erase or replace developer-owned prototype state.

## Detecting Interesting Changes

After every later successful foreground IDE exit, the launcher compares the
project's eligible state with the compatible prototype. Detection is advisory:
it never changes the prototype.

The comparison should report developer-meaningful categories where practical,
including:

- plugins added, removed, or changed in version; and
- persistent IDE configuration files added, removed, or changed.

Volatile files, ordering noise, timestamps, caches, logs, indexes, locks, and
known session-only state do not make a difference interesting. The comparison
may use a recorded manifest or fingerprints, but the result must not depend on
filesystem-specific copy-on-write metadata.

If an interesting difference exists, the launcher writes a concise message to
standard error after the IDE exits. The message summarizes the change and
shows the exact supported command that would promote this project's eligible
state. It does not prompt, block shutdown, or interpret silence as approval.

No message is required when eligible content is equivalent, the session did
not exit normally, or comparison cannot be performed reliably. A comparison
failure may produce a diagnostic but cannot cause prototype mutation.

## Explicit Prototype Promotion

After initial creation, promotion is the only operation that replaces a
prototype. The command identifies the IDE and source project unambiguously,
shows what will be replaced, refuses while relevant state is in use, and runs
the same or stronger validity checks used for initial creation.

Replacement is transactional:

1. Copy eligible source state into a new temporary snapshot.
2. Record compatible IDE identity and content metadata.
3. Validate the completed snapshot.
4. Atomically select it as the default prototype.
5. Leave the prior prototype selected if any earlier step fails.

Promotion never changes existing projects. Only projects seeded after the
successful promotion receive the new contents.

The CLI must also provide inspection sufficient to identify the current
prototype, its IDE identity, creation or promotion source, and capture time.
Exact command names are finalized with implementation and then documented in
current user guidance.

## Concurrency And Failure Safety

Prototype copying is compatible with concurrent project sessions because each
project receives separate writable state. DevCapsule serializes operations
that create or replace the same prototype and prevents capture from state that
still has an active IDE writer.

A launch may read a stable selected prototype while another operation prepares
its replacement. Atomic selection ensures the launch sees either the complete
old prototype or the complete new prototype, never an intermediate tree.

No recovery path weakens the component state contract, mounts an arbitrary
host directory silently, or converts the prototype into shared writable state.

## Non-Goals

This specification does not require:

- copy-on-write, reflinks, deduplicating filesystems, or hard-link farms;
- live synchronization between projects and the prototype;
- automatic promotion after the first prototype exists;
- merging two project profiles;
- multiple named prototypes for one compatible IDE identity;
- cloud settings synchronization;
- sharing project indexes, caches, logs, homes, or agent state; or
- deciding which release must implement this accepted behavior.

## Verification Scenarios

Validation should cover at least:

1. First successful session: empty project state becomes a valid prototype only
   after normal IDE exit.
2. First-session crash: no prototype is selected.
3. Default seeding: two projects receive equivalent initial content at distinct
   writable paths.
4. Concurrent divergence: modifications in either project do not appear in the
   other project or prototype.
5. Clean start: explicit empty initialization bypasses an existing prototype.
6. Interesting change: a plugin or durable setting change produces a stderr
   notice with the update command.
7. Volatile change: logs, indexes, timestamps, or locks alone produce no update
   recommendation.
8. Promotion: an explicit update changes the prototype atomically and affects
   only later seeds.
9. Failed promotion: the prior prototype remains selected and intact.
10. Compatibility mismatch: an incompatible IDE never consumes the prototype
    silently.

## Related

- [State and persistence specification](state-and-persistence.md)
- `engineering-docs/requirements/product/r-settings-001-per-ide-profile-prototype.md`
- `engineering-docs/requirements/devcapsule/r-state-001-persistent-ide-state-and-plugins.md`
- `engineering-docs/requirements/devcapsule/r-conc-001-concurrent-project-sessions.md`
