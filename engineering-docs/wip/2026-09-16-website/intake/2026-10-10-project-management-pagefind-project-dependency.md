# Website handoff: Pagefind is a project dependency, not a DevCapsule component

From: project-management. To: website. Date: 2026-10-10.
Authority: product-owner direction in the project-management decision session.

## Decision and requested action

Drop the proposal to make Pagefind a DevCapsule catalog component. The known
need is this static website's search feature. Keep Pagefind in the website's
own dependency and build system if W10 adopts it. Its installation under
/opt/xtras was temporary expedience for an experiment, not a portable project
prerequisite. The owner explicitly requests this handoff so that removing the
catalog proposal does not leave the website depending on that installation.

Record this constraint under the website repository's W10/search work and
current status when you take this item. This handoff does not select a new
search delivery date, start search implementation, or require a catalog entry.
The Playwright component already delivered by component-catalog is separate.

## Evidence and limits

Read-only inspection of the currently pinned website found no Pagefind entry
in package.json and no indexing invocation in scripts/build.mjs. No existing
production build dependency on /opt/xtras is alleged. The 2026-09-30 experiment
is recorded in the parent's file:
engineering-docs/wip/2026-09-16-website/2026-09-30-design-site-search-pagefind.md.
That design already proposes adding Pagefind to npm and invoking it after
Eleventy. Its /opt/xtras copy indexed a built site experimentally.

The original catalog request is recoverable at parent revision
967e9f9a3622d3b84c42eec6df004267a1abf143:
engineering-docs/wip/2026-08-09-project-management/intake/2026-09-30-website-pagefind-and-playwright-as-components.md.
This decision supersedes the Pagefind half of that request.

## Implementation contract when search is picked up

1. Declare Pagefind as a pinned build-time development dependency in the
   website's package.json and commit the matching package-lock.json. npm ci
   must acquire the version the project declares, including its platform binary.
2. Invoke the project-local Pagefind through an npm script or its Node API
   after rendering HTML. Integrate indexing before the current atomic output
   promotion, so a failed indexing step cannot publish a half-built search site.
3. Do not require a global Pagefind executable, /opt/xtras path, shell-profile
   setting, developer-specific symlink or manually prepared node_modules.
4. Publish the generated index and browser search assets with the static site.
   The deployed site needs no Pagefind process or Node server for search; the
   browser consumes the shipped static assets.
5. Document the ordinary npm installation/build path for standalone clones and
   CI. Any temporary experimental install must not become a hidden dependency.

## Acceptance

From a fresh website checkout with its documented Node/npm/Git prerequisites
and the required content refs, run npm ci and the ordinary build with no
Pagefind installed globally and no /opt/xtras available through PATH or other
configuration. Prove the resulting search assets are in the publication output
and a representative browser query works when serving only that output.
Check that failed indexing leaves the prior complete output intact, consistent
with the existing build's behavior. Record versions and evidence in the website
project. Do not uninstall anyone's current /opt/xtras tools to run this check;
use an isolated environment when implementing the work.

Upstream installation contract: https://pagefind.app/docs/installation/

## Routing

The parent website workstream owns this handoff to its independent presentation
project. Add it to that project's existing W10 work through its normal workflow;
do not create an unowned duplicate issue or re-route it to component-catalog.
Project-management retains the catalog-request disposition and this delivery
reference. Nothing here authorizes a production deployment.
