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
the **session surface**, the component that opens the project and shows
its structure, today called the IDE. Nothing else is a kind.

The reader of the manifest, the checkout record, `config show` and the
documentation meets these words and no others: capability, component,
required, offered, recommended, resolution, surface.

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
   surface is the standing example.
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
   capability that has several; choose the surface capability itself when
   the project recommends none. Each is one command and then `run`. These
   are the checkout's, never the repository's, as the previous order ruled.
5. **Cardinality is a property of the capability.** The surface admits one
   provider per launch. A capability such as a coding agent may admit
   several at once. The project's own capability, `cpp-compiler`, is the
   project's call. Today the code knows only "one IDE, a set of agents",
   by a name suffix; the model knows a declared cardinality.
6. **The surface is the one special role.** It owns the display, the
   entry point and the container's runtime template. It is a role a
   capability has, not a type a component is. The user-facing word stays
   "IDE"; the owner finds it defensible, not ideal, and no better word was
   offered.
7. **Components own their own concerns.** Channel, terms, consent,
   sign-in, seeds, managed directories, the materialization recipe. None
   of these is a property of a kind. Codex's `config.toml`, Claude Code's
   settings, PyCharm's directories and Playwright's browsers are all
   component declarations, and remain so.
8. **"No implicit coding agent" is preserved by the model, not by a
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
  behind the split beyond cardinality.
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
  spellings of "this checkout selects or deselects a capability", with
  the surface's cardinality the only real difference. `run --ide` and
  `run --agent` repeat the split on the launch flags.
- **`recommend ide frontend-ide` is two statements folded into one.** It
  recommends the surface capability; it cannot recommend the provider.
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

- **The checkout record is already flat.** It stores `selected =
  ["claude-code-agent", "codex-agent", "frontend-ide"]` and `without = []`
  with no kinds; the embedded lock names the surface as
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
devcapsule project config require python=3
devcapsule project config offer browser-automation --because "npm run test:ui"
devcapsule project config offer codex-agent --because "the project's agent instructions assume it"
devcapsule project config recommend ide frontend-ide
devcapsule project config recommend frontend-ide codium            # the resolution, optional
devcapsule project config recommend cpp-compiler clang --because "the sanitizer flags in CMakeLists"
devcapsule project config drop browser-automation
```

`require`, `offer` and `drop` take capabilities; `tool` and `env` as
sub-words go, `env` becoming `require env NAME` only where Part 5 keeps
the word. `recommend` takes either a recommendation name (`ide`, `memory`,
`cpus`, a host access) or a capability followed by a provider; a provider
the catalog does not list for that capability is refused before anything
is written. The manifest gains one table and loses none:

```toml
[capabilities]
required = ["cpp-compiler", "python"]
optional = ["browser-automation", "codex-agent"]

[capabilities.sdk-major]
python = 3

[recommendations]
ide = "frontend-ide"

[recommendations.resolution]
frontend-ide = "codium"
cpp-compiler = "clang"
```

### 3.2 For developers

```sh
devcapsule project config ide frontend-ide                 # the surface capability; unchanged
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

- Derivation selects, for every capability in play, one provider or the
  declared number: the checkout's choice, else the project's recommended
  resolution, else the catalog's only or first provider. The surface is
  the capability with the surface role; exactly one is selected, as now.
- The lock pins, per platform, the components of the project's required
  and offered capabilities, resolved by the project's recommendation
  where it has one, so a fresh clone resolves offline. A developer's
  different provider is pinned in the checkout record, as the IDE is
  today. Whether the lock also pins the alternatives is Part 5 item 5.
- Trust and consent are asked per component, exactly as now; a provider
  change to a vendor component asks like any other first acquisition.

## Part 4: What goes away

- The `-agent` suffix as a test anywhere in the code; `local_capabilities`
  as a list of refused names; the `surface_capabilities` and
  `ancillary_capabilities` split in the catalog, replaced by one table of
  capabilities, each with its providers, its cardinality and whether it
  is the surface.
- `config agent add|remove`, `config tool omit|restore`, `run --agent`,
  and the `tool` sub-word of `require|offer|drop`. Each retired spelling
  prints its replacement for one release, by the rc4 rule, unless Part 5
  item 6 deletes the aliases outright.
- The matrix's refusal of an agent in `require` and `offer`, and the
  grandfathering code that let schema-1 manifests keep one.
- `recommend ide` as the only recommendation of a capability; it remains
  as the recommendation of the surface, one case of the general form.
- In the documentation, the three-way vocabulary "IDE, agents, tools":
  the capabilities page, the project-versus-personal page, the command
  reference and the candidate changelog say capability, component,
  surface. The work on the documentation's language, booked with
  project-management the same day, is best done once, after this.

## Part 5: Decisions required from the owner

Items marked *proposal* are the agent's, with the motivation, awaiting the
owner's word; an answer the owner changes replaces the proposal.

1. **The developer's command words.** *Proposal:* `add`, `omit`,
   `restore` for capabilities and `use CAPABILITY COMPONENT|default` for
   the provider, `config ide` kept for the surface. `select` and
   `resolve` are avoided: the first reads as the surface, the second was
   the retired step. Alternatives: `config capability add|omit`, or
   `config with|without`.
2. **The run flags.** *Proposal:* `--with CAPABILITY` repeatable in place
   of `--agent`, `--use CAPABILITY=COMPONENT` repeatable, `--ide` kept.
3. **One coding-agent capability or three.** *Proposal:* keep three,
   `codex-agent`, `claude-code-agent`, `antigravity-agent`, each with one
   provider and no cardinality limit between them, because the three are
   not substitutes for one another the way `clang` and `g++` are: a
   project's agent instructions name one. A single `coding-agent` with
   three providers would make "both Codex and Claude Code" a cardinality
   exception on day one.
4. **Where the resolution lives in the manifest.** *Proposal:*
   `[recommendations.resolution]`, a table from capability to component,
   beside the existing `[recommendations]`; readable by the rc4 launcher
   as an unknown recommendation it warns about and ignores, which keeps
   schema 2 (R-CONFIG-001, tolerant readers). Alternative: schema 3 with
   the minimum-DevCapsule declaration the 2026-10-22 requirement asks
   for, if project-management sequences that requirement here.
5. **What the lock pins for a capability with several providers.**
   *Proposal:* the resolved provider only; a developer who chooses another
   gets it pinned in the checkout record and the version commands, as the
   IDE works today. Pinning every alternative makes the lock grow with the
   catalog and change when a provider the project never uses is updated.
6. **The rc4 compatibility aliases.** The redesign kept `config
   capabilities --local`, `config need` and the rest as hidden aliases
   because deleting them meant rewriting a hundred tests. This order
   rewrites those tests anyway. *Proposal:* delete the rc4 aliases and the
   new ones this order retires in the same slice, leaving one-line
   refusals that name the replacement, and say so in the changelog.
7. **Target.** *Proposal:* before the final 0.3.0 tag, as the next
   candidate's content ahead of the diagnostics snapshot, image cleanup
   and C20. rc4's vocabulary has been public for an evening; a final
   release that ships `config agent add` and retires it in 0.3.1 costs
   every adopter a rename and the documentation two rewrites. The owner
   rules whether the cycle tolerates it.
8. **SDK majors beyond Python.** The dry run refused `node=22` because
   the base declares a major for Python only. Not this order's subject,
   but the capability table this order builds is where a base's majors
   would be declared per capability. *Proposal:* leave it to the
   sample-projects item of 2026-10-22 and shape the table so it can hold
   the answer.
9. **Who implements.** *Proposal:* maintenance, stacked slices with the
   Codex and gpt-6-astra reviewer loop as for the redesign; project-
   management records the model as a decision superseding the
   kind-based wording in D-0004's revision and the redesign's Part 3.

## Part 6: The care the owner asked for

The change deletes code and cases, and every deletion is a place where a
written file, a launch or a consent could silently change meaning.

- **Files written by rc4 stay readable and keep their meaning.** Checkout
  records with `selected` lists naming `*-agent` capabilities; schema-2
  manifests with `optional` tools and `recommendations.ide`; locks with
  `capability-providers`; the trust record. A test fixture of each,
  taken from the dry run, is read by the new code and derives the same
  launch, provider for provider.
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

The documentation's language, booked with project-management; the
minimum-DevCapsule declaration in configuration files; Node and other SDK
majors; `init --regenerate` asking per-checkout consent despite
workstation trust, recorded with the redesign; the console's confirmation
boundary.
