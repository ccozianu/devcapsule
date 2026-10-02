# Work Order: The Content The Visitor Is Missing, And The Producer Migration

Date: 2026-09-28. Issued by `project-management` under the owner's grant of
2026-09-28 to run this independently. Companion to
[the website work order](2026-09-28-website-visitor-experience.md), which
is executed in the `devcapsule-website` repository. This one is executed in
DevCapsule, in three workstreams, each taking its own section on the owner's
selection of that workstream: `user-docs` for the content, `website` for the
producer migration and the pin, `project-management` for the runbook and
the local workflow. Delivered to the first two by mail.

Status: open. Immediate target: the documentation of 0.2.15, the current
release, published under the contract; the ideal structure visible in full,
with "coming soon" where a page is not yet written.

## 1. The Ideal Structure Of The Product Documentation

One structure, used for the sidebar, for the roles the home page links, and
for organizing requirements and bugs, taken from the owner's functionality
areas of 2026-09-19 and phrased as the adopter's question. Each area is a
directory under `docs/`; each page carries front matter; the six roles are
marked. A page that does not exist yet is created as a stub with
`status: planned` so the structure is complete on the site from the first
versioned publication.

| Directory | Adopter's question | Pages, in sidebar order | Role | Exists today |
|---|---|---|---|---|
| `docs/README.md` | Where do I start? | The overview: what the docs cover, the three entry points, the versions link | `overview` | yes, rewrite |
| `getting-started/` | How quickly can I do something useful? | install; your first session; stop and come back | `getting-started` on the first session | yes: `guides/first-session.md`, split |
| `your-project/` | How do I bring my project here? | an existing repository; a new project; declare what it needs; services and ports | `your-project` | partly: `guides/your-project.md` |
| `working-with-ai/` | How do I get effective help? | choose an agent; sign in and defaults, 0.2.15's no-approval posture; hosted and local models; instructions for agents (`AGENTS.md`); review and change agents | `agents` | no; the 0.2.15 headline, write first |
| `everyday-development/` | Can I do my normal work? | IDEs and terminals; Git; run, debug, test; previews and ports; clipboard and browser | | no; planned |
| `configuration/` | How do I make this workspace mine? | inspect with `project info` and `config list`; project defaults versus personal choices; extra tools in `/opt/xtras`; IDE preferences and plugins; resource limits | | partly: the 0.2.15 sections of `your-project.md` |
| `containment/` | What can this workspace and its agents touch? | the boundary in one page; granting and withdrawing access; Docker, network, devices, credentials | `containment` | no; from the README's claims and R-SCOPE-001, R-DOCKER-001, write second |
| `sessions/` | Can I leave and come back? | start, stop, reconnect; what persists and where; several projects; another machine | | partly: "stop and come back" |
| `collaboration/` | Can someone else pick up the work? | work in workstreams; the workflow in plain words | | yes: `guides/working-in-workstreams.md` |
| `updates/` | How do I stay current without breaking things? | launcher updates; component freshness; try an upgrade and roll back; supported versions, the owner's notice | | yes: freshness and upgrades guides, move |
| `troubleshooting/` | When something goes wrong? | first-session troubleshooting; diagnostics and logs; cleanup and uninstall | | partly: the first-session section, extract |
| `platforms/` | Does it run on my machine? | Windows via WSL2; Linux notes; macOS: not yet | `windows` on the WSL2 page | yes: `guides/windows-wsl2.md`, move |
| `reference/` | What exactly does this command do? | CLI commands; `project info` fields; configuration nodes and authorizations | | no; planned; the CLI README is the source |

Pages that leave `docs/`: the four drafts under `docs/product/` and the
Docker4PyCharm guide move to `engineering-docs/product/` and
`engineering-docs/archive/` respectively and are no longer published. The
journal and the release notes stay unversioned, per the contract.

## 2. `user-docs`: The Content, In Order

Owner: `user-docs`. Everything below is authored on `main` with front
matter, tokens instead of typed versions, and roles on the six entry pages.
Writing order is the order a visitor needs them:

1. **Getting started for 0.2.15.** Split the first-session guide into
   install, first session, stop and come back; replace every typed version
   with `{{tag}}`, `{{version}}` and `{{download_url}}`; remove the 0.2.12
   base-prompt and interrupt notes, which describe behaviour 0.2.14 and 0.2.15
   changed; verify every command against the downloaded 0.2.15 executable.
2. **Working with AI.** New. The three agents, sign-in, the 0.2.15 defaults
   (Codex never-ask, Claude bypass, Antigravity always-proceed), what that
   means and how to change it, instructions files, reviewing results. Source:
   the 0.2.15 release overview and work order, the component READMEs.
3. **Containment.** New. One page that says what the capsule and its agents
   can touch, what they cannot, how to grant and withdraw, in the adopter's
   words. Source: README, R-SCOPE-001, R-DOCKER-001, the authorization
   grammar in the CLI README.
4. **Configuration.** Move the 0.2.15 sections, extra tools and `project
   info`, out of `your-project.md` into their own pages; add inspect and
   project-versus-personal.
5. **Overview.** Rewrite `docs/README.md` as the front door of the structure
   above, with the versions link.
6. **Release notes** for 0.2.14 and 0.2.15 as
   `engineering-docs/releases/<tag>/notes.md`, from each release overview's
   notes block, so `/releases/` is complete from its first build. This
   adopts the release-notes artifact for the content half; the gate half is
   the runbook's, section 4.
7. **Planned stubs** for every page in section 1 that does not exist, with
   `status: planned`, a description, and one sentence on what the page will
   cover. The structure is then complete.
8. **Everyday development, sessions, troubleshooting, reference**, in that
   order, as time allows; each replaces its stub.

Done for the immediate target: items 1 to 7 on `main`, building clean with
the consumer's check at the pin, and the same guides carried onto
`docs-0.2.15` (section 4) so the current version's documentation is true.

## 3. `website` Workstream: The Producer Migration And The Pin

Owner: `website`, which retains the producer-side contract tasks W08-C and
W12-C. One change, landing together with the pin that implements the
contract, as R-DOCS-003 requires:

1. Front matter on every published page under `docs/` and the journal, per
   R-DOCS-003 part 1 plus `role`; `draft: true` on the two 2026-09-19
   retrospectives until the owner releases them.
2. `docs/versions.yaml` with `contract: 1`, the owner's approved notice, and
   the bootstrap decided below: `devel` from `main`; 0.2.15 supported and
   current from `docs-0.2.15`; 0.2.14 deprecated from `v0.2.14` with the note
   "the install steps in this version refer to an earlier download; follow
   the current guide"; 0.2.12 deprecated from `a989155` with
   `source-version: 0.2.14.dev0`.
3. The README's documentation links changed to role links; the landing
   page's stable identities as W07 settles them.
4. The website submodule pin advanced to the revision implementing contract
   version 1; the parent's `website.sh` and workflow adjusted if the
   consumer's interface changed.
5. The producer's `nox` gate runs the consumer's check against `docs/` at
   the pin.

Done: `./scripts/website.sh build` passes on `main` with the versioned
output; the versions index shows the notice and three versions; every role
resolves.

## 4. `project-management`: The Runbook And The Local Workflow

Owner: `project-management`, its own next slices after this order is
delivered:

1. `WORKFLOW-LOCAL.md` declares the project ref `docs-<version>`: forked
   from a final tag, documentation-only commits, never merged, named in the
   manifest as that version's source when it exists, outside the candidate
   gate, inside the consumer's build check. Create `docs-0.2.15` from
   `v0.2.15` and carry the corrected 0.2.15 guides onto it when `user-docs`
   delivers them.
2. The release runbook gains three obligations: before the final tag, the
   release's `docs/` is true for the version and passes the consumer's check;
   after the final tag, the manifest promotes the version and demotes the
   previous; publication follows the final tag. And the *Agent Freshness
   Review* section already owed.
3. The 0.2.16 proposal gains this order as a candidate: the website
   publication that documents 0.2.15 is not gated on 0.2.16, and 0.2.16 is
   the first release whose runbook carries the documentation obligations.

## 5. Decisions Taken Under The Owner's Grant

Recorded here so nobody re-derives them; the owner may adjust any.

1. The location rule stands: `docs/` is the versioned tree; the product
   drafts and the Docker4PyCharm guide leave it and are unpublished.
2. Six roles in contract version 1: overview, getting-started, your-project,
   agents, containment, windows. The two added beyond the design's four are
   the product's headline and its boundary, which the home page must link.
3. `docs-<version>` project refs are the answer to post-release
   documentation corrections; declared in `WORKFLOW-LOCAL.md`.
4. 0.2.12 is published from its guides' commit, because the site put people
   on it.
5. 0.2.15's guides are corrected on `docs-0.2.15` before the first versioned
   publication; 0.2.14 is published as it is with a note, since it is
   deprecated and its readers are asked to move.
6. The contract gains one additive element: `status: planned`, a published
   stub labelled "coming soon", so the ideal structure is visible before it
   is written.
7. The journal route becomes `/journal/` with `/blog/` kept as an alias; the
   directory in this repository keeps its name.
8. Release notes are adopted as content now; whether they gate the final tag
   is decided with the runbook change in section 4.

## 6. Evidence

- `docs/` inventory on `main` at 0.2.16.dev0: seven guides, five product
  drafts, one historical guide; no front matter; 0.2.15 named twice.
- The owner's functionality areas of 2026-09-19, in the project-management
  design issue on V1 completeness.
- The 0.2.15 release overview and work order for the agent defaults, extra
  tools and `project info`.
- The design issue on documentation currency, P1 to P7, S1, D1.
