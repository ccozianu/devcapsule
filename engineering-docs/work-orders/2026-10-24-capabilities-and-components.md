# Work Order Draft: One Model Of Capabilities And Components

Drafted 2026-10-24, the evening candidate 4 was published, from the
owner's review of the vocabulary the [CLI UX redesign](2026-10-24-cli-ux-redesign.md)
shipped in rc4. Status: **draft, awaiting the owner's decisions in
Part 5**. This order refactors the output of the previous one. It deletes
kinds, commands and cases; it adds one concept the previous order left
implicit, the project's recommended resolution of a capability. Nothing
here is implemented.

Evidence: source `78a9c66`, the rc4 tag, read on 2026-10-24; the dry run of
the rc4 launcher against `ccozianu/ai-learning-bootstrap@64c11f2` the same
evening, under a throwaway configuration home, no container launched.
Source references are relative to `devcapsule-src/devcapsule/`.

## Outcome

DevCapsule has one model of what goes into a capsule. A **capability** is
what a project speaks about: `cpp-compiler`, `frontend-ide`,
`browser-automation`, `postgresql-client`. A **component** is what the
catalog pins, verifies, delivers and seeds: `clang`, `g++`, `codium`,
`webstorm`, `playwright`. A capability has one or more providing
components. The project requires, offers or recommends capabilities and
may name the resolution it suggests; the developer takes or leaves what is
offered, adds what the project did not mention, and chooses among
providers where there is a choice. Exactly one capability per launch is
the **IDE**, the component the capsule starts for the user: it opens the
project, shows its structure, owns the container's lifetime and can make
use of the display. Nothing else is a kind.

The reader of the manifest, the checkout record, `config show` and the
documentation meets these words and no others: capability, component,
required, offered, recommended, resolution, IDE, and a minimum
version written on a requirement. The SDK major is gone, by the owner's
ruling; the minimum is the owner's direction, and is not the SDK major
under another name: it applies to every requirement alike and has no
table.

## Part 1: The model, as agreed with the owner on 2026-10-24

1. **Capability and component are distinct, and both are needed.** The
   project must be able to say "a C++ compiler" and let the platform, the
   catalog and the person settle whether it is `clang` or `g++`; it must
   be able to say "a frontend IDE" and let one person take VSCodium and
   another WebStorm. The capability is the project's word; the component
   is the catalog's.
2. **The project speaks in capabilities, three ways.** *Required*: every
   checkout has it, and no local choice waives it (R-CONFIG-001).
   *Offered*: present unless the developer leaves it out. *Recommended*:
   a preference for a capability the developer could also do without; the
   IDE is the standing example.
3. **The project may also recommend the resolution.** For a capability
   with several providers it may name the one it suggests, `frontend-ide`
   resolved by `codium`. A newcomer gets it without a question; a
   developer who prefers another provider says so once. This is the
   burden of choice lifted from those who do not care and left with those
   who do. A recommendation of either kind grants nothing: a recommended
   provider that comes through a vendor channel still meets trust
   (D-0011) or the per-checkout consent, as the base does today.
4. **The developer speaks in the same words.** Omit an offered capability;
   add a capability the project did not mention; choose the provider of a
   capability that has several; choose the IDE capability itself when
   the project recommends none. Each is one command and then `run`. These
   are the checkout's, never the repository's, as the previous order ruled.
5. **Every capability resolves to exactly one provider; there is no
   cardinality.** The owner struck it on 2026-10-24: nothing it would
   express is beyond the other features. "Several coding agents at once"
   is three capabilities, each present or absent. A project that wants
   both `clang` and `g++` requires both by name. "Exactly one IDE per
   launch" is the IDE role, below. Today's "one IDE, a set of agents"
   is a name-suffix split and goes with it.
6. **The IDE is the one special role.** It is the component the capsule
   starts for the user: it owns the lifetime of the container, which ends
   when it exits; it can make use of the display, and today every IDE
   does; the launcher gives it a log, the directories it persists and the
   project path on its command line in the form it understands. It does
   not own the display. It is a role a capability has, not a type a
   component is. The command-line word stays `ide` for this order;
   whether the role is renamed and generalized to the capsule's entry
   point, with the display a declaration of the component, is tabled as
   [D-0014](../decisions/product/d-0014-entry-point-generalizes-the-ide-role.md),
   in scope for V1.
7. **Components own their own concerns.** Channel, terms, consent,
   sign-in, seeds, managed directories, the materialization recipe. None
   of these is a property of a kind. Codex's `config.toml`, Claude Code's
   settings, PyCharm's directories and Playwright's browsers are all
   component declarations, and remain so.
8. **The owner's rule for this order: remove what can be removed.** Every
   concept the user does not need lessens the conceptual load on the user,
   the documentation to write, the lines of code, the special cases and
   the moving parts. Where a concept can go entirely, it goes; it is not
   replaced by a smaller one.
9. **The SDK major goes entirely, by the owner's ruling of 2026-10-24.**
   `require python=3` and `[capabilities.sdk-major]` express a constraint
   no base can fail today: every base declares Python 3 and nothing else,
   `python=4` is refused because nothing has it, and `node=22`, the one
   constraint a real project asked for, is refused because no base
   declares a Node major. The need behind it, a project wanting Node 22
   rather than 24, becomes real only when the catalog has bases to choose
   between, and it is not addressed by a replacement constraint syntax in
   this order: the owner's rule is removal, not a smaller concept. If the
   need arrives, it is designed then, against the catalog that creates it.
10. **A requirement may carry a minimum version, by the owner's direction
   of 2026-10-24.** The use case, exactly as stated: a project needs the
   Python SDK 3.14 or newer, a capability with one provider and therefore
   wearing the component's name; the Java SDK 21 or newer, a capability
   that may be provided by more than one JDK; Playwright 1.21 or newer, a
   component. All three are written the same way, in the manifest and at
   the command line, as the name followed by `>=` and the version. One
   relation, "or newer"; no upper bound, no exact pin, no range; the lock
   is the exact pin. One comparator: dotted integers left to right,
   `25.0.4+7` read as 25.0.4, `v22.23.1` as 22.23.1, prereleases
   unsupported and said so. Every requirement may take a minimum the same
   way, or none; there is no table, no SDK category and no name that is
   treated differently. This is the SDK major's need met without the
   concept.
11. **"No implicit coding agent" is preserved by the model, not by a
   rule.** A capability the project does not offer is absent until the
   developer adds it. A project that offers `codex-agent` says so in its
   manifest, where every contributor reads it, and the contributor may
   omit it. The agent's download still asks for the person's acceptance.

## Part 2: What rc4 does that the model does not justify

With source lines at `78a9c66`.

- **Agents are a name suffix.** `resolution_matrix.py:312-320`
  (`local_capabilities`) defines the developer's capabilities as the
  surfaces plus every ancillary capability whose name ends in `-agent`.
  The test `endswith("-agent")` recurs in `configuration/operations.py`
  (640, 657, 658), `configuration/derivation.py` (64, 65),
  `commands/project.py` (338, 711, 712, 1814, 1815) and
  `configuration/owner_commands.py` (305): five files, twelve lines, each
  splitting one list into "the IDE" and "the agents". No behavior sits
  behind the split.
- **The matrix refuses an agent in the shared contract.**
  `_split_tools` in `configuration/operations.py:951-964` and the owner
  commands reject `codex-agent` in `require` and `offer`, except where a
  schema-1 manifest already required it. The owner's question of
  2026-10-24, "do we derive any value from preventing a project to
  recommend or require codex", has the answer no: the download consent
  protects the contributor, not the refusal; an offered agent is already
  personal because it can be omitted; a required agent is the same
  statement as a required Docker CLI, and the owner's to make. A project
  that works with one agent cannot say so today except in `AGENTS.md`.
- **Three command families for one act.** `config ide NAME`, `config
  agent add|remove NAME` and `config tool omit|restore NAME` are three
  spellings of "this checkout selects or deselects a capability", the
  IDE role the only real difference. `run --ide` and
  `run --agent` repeat the split on the launch flags.
- **`recommend ide frontend-ide` is two statements folded into one.** It
  recommends the IDE capability; it cannot recommend the provider.
  Since every rc4 capability has exactly one provider the loss is latent,
  but the manifest is not shaped for the second statement.
- **Every capability has one provider, and the code assumes it.** The
  catalog at `resolution_matrix.py:1301-1315` maps each capability to one
  component; `providers(name)[0]` is taken in `derivation.py:64-65` and
  `commands/project.py:711-712, 1814-1815`. The inventory:

  | Capability | Provider | Kind today | Selected by |
  |---|---|---|---|
  | `python-ide`, `java-ide`, `eclipse-ide`, `dotnet-ide`, `frontend-ide` | `pycharm`, `intellij`, `eclipse`, `rider`, `codium` | surface | `config ide`, one |
  | `codex-agent`, `claude-code-agent`, `antigravity-agent` | `codex`, `claude-code`, `antigravity-cli` | ancillary, "agent" | `config agent add`, many |
  | `postgresql-client`, `browser-automation`, `dotnet` | `postgresql-client`, `playwright`, `dotnet-sdk` | ancillary, "tool" | the project; `config tool omit` |
  | `python`, `node`, `java`, `maven`, `docker-cli` | the base, no component | base-supplied | the project; SDK major for `python` only |

- **The SDK major is a table, a syntax and 32 source lines for one
  integer that cannot vary.** `sdk_major` and `sdk-major` appear in twelve
  source files (`resolution_matrix.py`, `configuration/model.py`,
  `capabilities.py`, `capability_commands.py`, `capability_selection.py`,
  `fingerprints.py`, `manifest_document.py`, `operations.py`,
  `owner_commands.py`, `storage.py`, `environment_realization.py`,
  `commands/project.py`), the `TOOL[=MAJOR]` syntax on `init --require` and
  `config require tool`, the `[capabilities.sdk-major]` table, three
  documentation passages and six test files. The capabilities digest in
  `fingerprints.py` hashes the table, so its removal changes the digest a
  regenerated lock records.
- **Nothing today lets a project say "3.14 or newer".** The only version
  syntax is `TOOL=MAJOR`, which goes. The catalog's bases declare the
  names they satisfy (`resolution_matrix.py:603, 642, 680`:
  `python`, `docker-cli`, `node`, `java`, `maven`) and not the versions,
  although the image builds them from pinned constants
  (`images/tooling.py`: Node v22.23.1, Temurin 25.0.4+7, Maven 3.9.16)
  and Ubuntu 24.04's Python 3.12. Resolution has no comparator.
  `versions follow-project` and the D-0010 version-set check test
  presence, not a minimum. `config show` and `check` have no column or
  message for a requirement the catalog cannot meet by version. Against
  today's catalog the use case resolves as: `python>=3.14` refused, since
  the Ubuntu 24.04 bases supply 3.12 and no `python` component exists;
  `java>=21` satisfied by the base's Temurin 25.0.4; `playwright>=1.21`
  satisfied by the pinned 1.63.0. The Python refusal is the honest
  outcome and shows how the need is met when real: a `python` component
  delivering 3.14 becomes a second provider of the capability, with no
  change to the manifest.
- **The checkout record is already flat.** It stores `selected =
  ["claude-code-agent", "codex-agent", "frontend-ide"]` and `without = []`
  with no kinds; the embedded lock names the IDE as
  `components.interactive-surface`. The record needs one new table for a
  chosen provider and nothing removed.
- **Consent nodes are per component and stay.** `claude-code-download`
  and `antigravity-download` in the checkout record, and the channels in
  the trust record, are component properties. They are untouched by this
  order.

## Part 3: The experience after the change

### 3.1 For project owners

```sh
devcapsule project config require cpp-compiler --because "the build"
devcapsule project config require 'python>=3.14' 'java>=21' --because "the build targets them"
devcapsule project config require 'playwright>=1.21'
devcapsule project config offer browser-automation --because "npm run test:ui"
devcapsule project config offer codex-agent --because "the project's agent instructions assume it"
devcapsule project config recommend ide frontend-ide
devcapsule project config recommend frontend-ide codium            # the resolution, optional
devcapsule project config recommend cpp-compiler clang
devcapsule project config drop browser-automation
```

A minimum is part of the name string, in the manifest and on the command
line, quoted at a shell because `>` redirects; `drop python` removes the
requirement whatever its minimum; a second `require 'python>=3.15'`
replaces the minimum. `require`, `offer` and `drop` take capabilities;
the `tool` sub-word goes; `require env NAME` and `offer env NAME` keep
the `env` word, since an environment input is not a capability. `recommend` takes either a recommendation name (`ide`, `memory`,
`cpus`, a host access) or a capability followed by a provider; a provider
the catalog does not list for that capability is refused before anything
is written. A resolution carries no reason of its own: the requirement's
reason says why the capability is needed, and the resolution is only the
default provider (reviewer's decision during slice 2, by the owner's rule
of removal; nothing reads such a reason). The manifest gains one table and loses none:

```toml
[capabilities]
required = ["cpp-compiler", "python>=3.14", "java>=21", "playwright>=1.21"]
optional = ["browser-automation", "codex-agent"]

[capabilities.resolution]
frontend-ide = "codium"
cpp-compiler = "clang"

[recommendations]
ide = "frontend-ide"
```

### 3.2 For developers

```sh
devcapsule project config ide frontend-ide                 # the IDE capability; unchanged
devcapsule project config add claude-code-agent            # a capability the project did not offer
devcapsule project config omit browser-automation          # an offered one, left out here
devcapsule project config restore browser-automation
devcapsule project config use frontend-ide webstorm        # the provider, where there is a choice
devcapsule project config use frontend-ide default         # back to the project's or the catalog's
devcapsule project run --ide frontend-ide --with codex-agent --use frontend-ide=webstorm --save
```

`config show` gains a `PROVIDER` column: the component the capability
resolves to and its source, `catalog`, `project recommends`, or
`checkout`. `config check` treats a required capability with no provider
the platform can satisfy as the contract error it is today.

### 3.3 What the launcher does with it

- Derivation selects, for every capability in play, one provider: the
  checkout's choice, else the project's recommended
  resolution, else the catalog's only or first provider. The IDE is
  the capability with the IDE role; exactly one is selected, as now.
- A minimum narrows the candidates first: of a capability's providers and
  the version the base supplies, only those at or above it remain; none
  remaining is a refusal before any write, naming the versions that exist
  ("no base supplies Python 3.14 or newer; the Ubuntu 24.04 bases supply
  3.12"). The catalog therefore declares, per base, the version of each
  capability the base supplies, from the same constants the image builds
  with. `config show` prints the minimum beside the requirement and the
  resolved version beside the provider; `check` reports an unmet minimum
  as a contract error. A checkout's own version set (D-0010) must meet
  the minimum as it must meet presence today: `run` stops with status 3
  and names `versions follow-project --apply`.
- The lock pins, per platform, the components of the project's required
  and offered capabilities, resolved by the project's recommendation
  where it has one, so a fresh clone resolves offline. A developer's
  different provider is pinned in the checkout record, as the IDE is
  today. The lock does not pin the alternatives (Part 5 item 5).
- Trust and consent are asked per component, exactly as now; a provider
  change to a vendor component asks like any other first acquisition.

## Part 4: What goes away

- The `-agent` suffix as a test anywhere in the code; `local_capabilities`
  as a list of refused names; the `surface_capabilities` and
  `ancillary_capabilities` split in the catalog, replaced by one table of
  capabilities, each with its providers and whether it is the IDE.
- `config agent add|remove`, `config tool omit|restore`, `run --agent`,
  and the `tool` sub-word of `require|offer|drop`. Each retired spelling
  prints its replacement for one release, by the rc4 rule, unless Part 5
  item 6 deletes the aliases outright.
- The matrix's refusal of an agent in `require` and `offer`, and the
  grandfathering code that let schema-1 manifests keep one.
- The SDK major: the `[capabilities.sdk-major]` table, the `TOOL[=MAJOR]`
  syntax, the base's `sdk_majors` declaration, the major in the
  capabilities digest, and every reader and writer of them. A manifest
  that carries the table stays readable: the reader ignores it with one
  note naming this change, the next owner write drops it (R-CONFIG-001,
  conservative writers), and a lock whose digest was computed with the
  table is accepted as current until the project's next shared edit.
- `recommend ide` as the only recommendation of a capability; it remains
  as the recommendation of the IDE, one case of the general form.
- In the documentation, the three-way vocabulary "IDE, agents, tools":
  the capabilities page, the project-versus-personal page, the command
  reference and the candidate changelog say capability, component,
  IDE. The work on the documentation's language, booked with
  project-management the same day, is best done once, after this.

## Part 5: Decisions taken, each reversible by the owner's word

The owner's rulings of 2026-10-24 are in Part 1 and are not repeated. The
items below are the agent's judgment within them, recorded as taken so
that the owner has nothing to answer; a word from the owner on any item
replaces it. Two change what the release carries and are marked **scope**;
the rest are implementation.

1. **Developer command words:** `add`, `omit`, `restore` for capabilities;
   `use CAPABILITY COMPONENT|default` for the provider; `config ide` kept
   for the IDE. `select` and `resolve` avoided: the first reads as the
   IDE choice, the second was the retired step.
2. **Run flags:** `--with CAPABILITY` repeatable in place of `--agent`;
   `--use CAPABILITY=COMPONENT` repeatable; `--ide` kept.
3. **Three coding-agent capabilities,** `codex-agent`, `claude-code-agent`,
   `antigravity-agent`, each with one provider, any of them present at
   once. They are not substitutes for one another as `clang` and `g++`
   are; a project's agent instructions name one. A single `coding-agent`
   with three providers could not express "both Codex and Claude Code"
   without the cardinality the owner struck.
4. **The resolution lives in `[capabilities.resolution]`,** a table from
   capability to component beside `[capabilities.reasons]`; the schema
   stays 2 (R-CONFIG-001, tolerant readers). Corrected 2026-10-24 during
   slice 2: the rc4 reader refuses an unknown key under
   `[recommendations]` ("recommendations declares resolution; known
   recommendations: ide, memory, cpus") and silently tolerates an unknown
   table under `[capabilities]`, verified with the rc4 executable; the
   earlier placement would have made every manifest with a resolution
   unreadable by rc4. rc4 ignores the table and derives the catalog's
   first provider, which is the only provider of every capability today.
   A manifest that names a minimum or a component alias is unreadable by
   rc4 regardless, as any new vocabulary is. The minimum-DevCapsule
   declaration of the 2026-10-22 requirement is not folded in here.
5. **The lock pins the resolved provider only.** A developer who chooses
   another gets it pinned in the checkout record and the version
   commands, as the IDE works today. Pinning every alternative would make
   the lock grow with the catalog and change when a provider the project
   never uses is updated.
6. **Scope. The rc4 compatibility aliases are deleted** in the same slice
   that retires this order's spellings, leaving one-line refusals that
   name the replacement, said so in the changelog. The redesign kept them
   because deleting meant rewriting a hundred tests; this order rewrites
   those tests anyway.
7. **Scope. Target: before the final 0.3.0 tag,** as the next candidate's
   content, ahead of the diagnostics snapshot, image cleanup and C20.
   rc4's vocabulary has been public for an evening; a final release that
   ships `config agent add` and retires it in 0.3.1 costs every adopter a
   rename and the documentation two rewrites.
8. **The SDK major is removed,** per Part 1 item 9; old files are read as
   Part 4 states. The sample-projects item of 2026-10-22 on Node as a
   first-class SDK is answered by the minimum of Part 1 item 10.
9. **Maintenance implements,** stacked slices with the Codex and
   gpt-6-astra reviewer loop as for the redesign; project-management
   records the model as a decision superseding the kind-based wording in
   D-0004's revision and the redesign's Part 3.
10. **A minimum is spelled `NAME>=VERSION`** in the manifest and at the
   command line, quoted at a shell, because it reads the same everywhere
   and the same as pip and npm. `NAME=VERSION` read as "or newer" would
   need no quotes but reads as equality to anyone who has used a package
   manager.

## Part 6: The care the owner asked for

The change deletes code and cases, and every deletion is a place where a
written file, a launch or a consent could silently change meaning.

- **Files written by rc4 stay readable and keep their meaning.** Checkout
  records with `selected` lists naming `*-agent` capabilities; schema-2
  manifests with `optional` tools and `recommendations.ide`; locks with
  `capability-providers`; the trust record. A test fixture of each,
  taken from the dry run, is read by the new code and derives the same
  launch, provider for provider.
- **Old locks do not go stale by this change.** The capabilities digest
  changes shape when the SDK-major table leaves it; a lock written by rc4
  must still read as current for an unchanged manifest, or every adopter's
  first `run` after upgrading would report a shared edit nobody made. A
  fixture lock from the dry run proves it.
- **A minimum refuses before it writes, and old locks still satisfy an
  unchanged manifest.** The acceptance case is the owner's use case as
  stated: `python>=3.14`, `java>=21`, `playwright>=1.21` in one manifest,
  with the refusal message for Python naming 3.12, and the lock for the
  other two pinning what the catalog supplies; a fixture proves each.
- **No kind survives by accident.** The acceptance for the matrix slice
  is a grep: no `-agent` test, no `local_capabilities`, no
  `surface_capabilities`, no `ancillary_capabilities`, no `providers(…)[0]`
  outside the one function that resolves a capability.
- **Consent never widens.** A provider change, an added capability or a
  project's new resolution recommendation reaches the same trust and
  consent questions as a first acquisition. The tests that proved "a
  recommendation grants nothing" and "a changed recommendation keeps the
  answer" in the redesign are kept and extended to resolutions.
- **Staged writes, as the redesign established.** Nothing is written
  before the last blocking decision; `--preview` on every owner command;
  the Hoare standard for the capability table, which becomes the one
  place the launcher learns what a capability is.
- **The gate is the full one.** Every slice's gate is `nox -s build`,
  including the packaging integration against the built executable; the
  unit gate alone missed a stale expectation in rc4 (`fe886ad`).
- **Stages.** Three, each a pull request into the release branch with
  its review merged forward: the catalog and derivation on the one
  capability table, with the old commands still working on top of it;
  the commands, run flags, manifest table and checkout record; the
  documentation, the aliases' disposition and the changelog.

## Out of scope here

The generalization of the IDE role to the capsule's entry point, D-0014,
tabled by the owner and in scope for V1.
The documentation's language, booked with project-management; the
minimum-DevCapsule declaration in configuration files; Node and other SDK
majors; `init --regenerate` asking per-checkout consent despite
workstation trust, recorded with the redesign; the console's confirmation
boundary.
