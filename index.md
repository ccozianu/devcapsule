# Documentation Index

Status: maintained index of repository markdown documentation.

When adding, deleting, or renaming permanent `.md` files, update this index in
the same change. In multiple-stream mode, this index lists each workstream
status file; internal WIP/archive documents use the local index in that status.

## Start Here

- [Developer overview](README.md)
- [Current status and handoff](CURRENT-STATUS.md)
- [Documentation index](index.md)
- [Agent instructions](AGENTS.md)
- [Claude compatibility pointer](CLAUDE.md)
- [Requirements overview and index](REQUIREMENTS.md)
- [Human / agent workflow](WORKFLOW.md)
- [Product documentation](docs/README.md)
- [Engineering documentation](engineering-docs/README.md)

## Root Requirement Records

- [R-PRODUCT-001 Batteries-Included IDE Environments](engineering-docs/requirements/product/r-product-001-batteries-included-ide-environments.md)
- [R-PRODUCT-002 Explicit Host Boundaries](engineering-docs/requirements/product/r-product-002-explicit-host-boundaries.md)
- [R-PRODUCT-003 Durable Human/Agent Project Memory](engineering-docs/requirements/product/r-product-003-durable-human-agent-project-memory.md)
- [R-PRODUCT-004 Reusable Human/Agent Workflow](engineering-docs/requirements/product/r-product-004-reusable-human-agent-workflow.md)
- [R-PRODUCT-005 Incremental Human/Agent Execution Loop](engineering-docs/requirements/product/r-product-005-incremental-human-agent-execution-loop.md)
- [R-PRODUCT-006 Multiple Human/Agent Workstream Coordination](engineering-docs/requirements/product/r-product-006-multiple-workstream-coordination.md)
- [R-DOCS-001 Root Documentation Stays Implementation-Agnostic](engineering-docs/requirements/product/r-docs-001-root-documentation-stays-implementation-agnostic.md)
- [R-DOCS-002 Current User Docs Show Current Interfaces](engineering-docs/requirements/product/r-docs-002-current-user-docs-show-current-interfaces.md)
- [R-SETTINGS-001 Per-IDE Profile Prototype](engineering-docs/requirements/product/r-settings-001-per-ide-profile-prototype.md)
- [R-GTM-001 Compelling V1 Announcement For Adopters](engineering-docs/requirements/product/r-gtm-001-compelling-v1-announcement-for-adopters.md)

## Design Decisions

- [Decision record template](engineering-docs/decisions/product/_template.md)
- [D-0001 Capability-First CLI Model](engineering-docs/decisions/product/d-0001-capability-first-cli-model.md)
- [D-0004 Configuration Resolution And Guided Run Experience](engineering-docs/decisions/product/d-0004-configuration-resolution-and-guided-run.md)
- [D-0005 Agent-Neutral Base And Optional Agent Components](engineering-docs/decisions/product/d-0005-agent-neutral-base-and-optional-agent-components.md)
- [D-0006 One Module For Host And Platform Friction (proposed)](engineering-docs/decisions/product/d-0006-host-platform-friction-module.md)
- [D-0007 Resolution Matrix As Accumulated Verified Combinations (proposed)](engineering-docs/decisions/product/d-0007-resolution-matrix-model-and-interface.md)

## Specifications

- [IDE profile prototypes](engineering-docs/specifications/product/ide-profile-prototypes.md)
- [DevCapsule V1 state and persistence](engineering-docs/specifications/product/state-and-persistence.md)
- [Project workflow bootstrap](engineering-docs/specifications/product/project-workflow-bootstrap.md)

## Workstream Status

- [Multiple-stream workflow successful archive](engineering-docs/archive/2026-08-08-multi-workflow/CURRENT-STATUS.md)
- [Recursive dogfood E2E successful archive](engineering-docs/archive/2026-08-06-recursive-e2e/CURRENT-STATUS.md)
- [Project management current status](engineering-docs/wip/2026-08-09-project-management/CURRENT-STATUS.md)
- [Workflow improvements current status](engineering-docs/wip/2026-08-09-workflow-improvements/CURRENT-STATUS.md)
- [Sample demo projects current status](engineering-docs/wip/2026-08-14-sample-projects/CURRENT-STATUS.md)
- [Contained display current status](engineering-docs/wip/2026-08-19-contained-display/CURRENT-STATUS.md)

## Engineering Design Notes

- [Multiple-stream workflow design](engineering-docs/design-notes/multiple-stream-workflow.md)
- [FastAPI web application configuration research](engineering-docs/design-notes/fastapi-webapp-configuration-research.md)
- [DevCapsule V1 user experience design draft](engineering-docs/design-notes/devcapsule/v1-user-experience.md)
- [DevCapsule V1 gap review at 0a0ff09](engineering-docs/design-notes/devcapsule/2026-08-06-v1-gap-review.md)
- [Click-based CLI parsing brief](engineering-docs/design-notes/devcapsule/click-based-cli-parsing-brief.md)
- [The VS Code-family setuid sandbox helper](engineering-docs/design-notes/devcapsule/vscode-sandbox-setuid.md)

## Active DevCapsule Development

- [DevCapsule Python CLI](devcapsule-src/README.md)
- [DevCapsule test suites](devcapsule-src/tests/README.md)
- [DevCapsule implementation requirements overview](devcapsule-src/REQUIREMENTS.md)
- [R-ENV-001 Dockerized PyCharm Runtime](engineering-docs/requirements/devcapsule/r-env-001-dockerized-pycharm-runtime.md)
- [R-STATE-001 Persistent IDE State And Plugins](engineering-docs/requirements/devcapsule/r-state-001-persistent-ide-state-and-plugins.md)
- [R-SCOPE-001 Explicit Host Filesystem Exposure](engineering-docs/requirements/devcapsule/r-scope-001-explicit-host-filesystem-exposure.md)
- [R-DEV-001 Useful Development Tooling Baseline](engineering-docs/requirements/devcapsule/r-dev-001-useful-development-tooling-baseline.md)
- [R-GIT-001 Git Identity And Credentials Without Host Credential Mounts](engineering-docs/requirements/devcapsule/r-git-001-git-identity-and-credentials-without-host-credential-mounts.md)
- [R-DOCKER-001 Explicit Docker Capability Profiles](engineering-docs/requirements/devcapsule/r-docker-001-explicit-docker-capability-profiles.md)
- [R-PROJECT-001 Per-Project IDE Runtime State](engineering-docs/requirements/devcapsule/r-project-001-per-project-ide-runtime-state.md)
- [R-CONC-001 Concurrent Project Sessions](engineering-docs/requirements/devcapsule/r-conc-001-concurrent-project-sessions.md)
- [R-PROC-001 Durable Human/Agent Project Memory](engineering-docs/requirements/devcapsule/r-proc-001-durable-human-agent-project-memory.md)
- [R-DOCS-001 Generated Documentation Index](engineering-docs/requirements/devcapsule/r-docs-001-generated-documentation-index.md)
- [R-DOCS-002 User-Level Documentation Coevolves With User-Visible Behavior](engineering-docs/requirements/devcapsule/r-docs-002-user-level-documentation-coevolves-with-user-visible-behavior.md)
- [R-IDE-CONFIG-001 Configuration-First End-User CLI Model](engineering-docs/requirements/devcapsule/r-ide-config-001-configuration-first-end-user-cli-model.md)
- [R-PYTHON-MVP-001 Source Checkout Install And Run](engineering-docs/requirements/devcapsule/r-python-mvp-001-source-checkout-install-and-run.md)
- [R-PYTHON-MVP-002 Single-File Python CLI Artifact](engineering-docs/requirements/devcapsule/r-python-mvp-002-single-file-python-cli-artifact.md)
- [R-PYTHON-MVP-003 Python MVP Feature Scope](engineering-docs/requirements/devcapsule/r-python-mvp-003-python-mvp-feature-scope.md)
- [R-IMAGE-BUILD-001 Python-Native Composable Image Building](engineering-docs/requirements/devcapsule/r-image-build-001-python-native-composable-image-building.md)
- [R-FRAMEWORK-001 Shared Python DevCapsule Orchestration](engineering-docs/requirements/devcapsule/r-framework-001-shared-python-docker4ide-orchestration.md)
- [R-COMPAT-001 Client Upgrades Require No User Action For Existing Projects](engineering-docs/requirements/devcapsule/r-compat-001-client-upgrades-require-no-user-action.md)
- [Packaged project workflow asset boundary](devcapsule-src/devcapsule/assets/project_workflow/README.md)
- [Packaged generic agent instructions](devcapsule-src/devcapsule/assets/project_workflow/definition/AGENTS.md)
- [Packaged generic workflow definition](devcapsule-src/devcapsule/assets/project_workflow/definition/WORKFLOW.md)
- [PyCharm image vibe-coding bootstrap template](devcapsule-src/devcapsule/assets/pycharm/image-assets/vibe-coding-process.md)
- [Legacy-compatible PyCharm bootstrap template copy](devcapsule-src/devcapsule/assets/docker4pycharm/image-assets/vibe-coding-process.md)
- [TypeScript five-in-a-row sample project](devcapsule-src/tests/resources/sample_projects/typescript_tictactoe_5inrow/README.md)

## Product And Positioning

- [Product documentation map](docs/README.md)
- [Draft pitch: batteries included, boundaries explicit](docs/product/draft-pitch.md)
- [LinkedIn announcement draft](docs/product/linkedin-announcement.md)
- [V1 announcement draft](docs/product/v1-announcement.md)
- [Working backwards press release](docs/product/working-backwards-press-release.md)

## Docker4PyCharm Historical Reference

The `docker4pycharm/` directory is the original shell-based PyCharm MVP this
project was bootstrapped from, frozen at that point in time. Read these for
history; record current decisions in the active documents above.

- [Docker PyCharm isolation README](docker4pycharm/README.md)
- [Historical root project brief](engineering-docs/implementation-notes/docker4pycharm/historical-root-readme.md)
- [Post-MVP refactoring strategy](engineering-docs/design-notes/docker4pycharm/future-agent-refactoring-brief.md)
- [PyCharm AI plugin and ChatGPT subscription setup](docs/guides/docker4pycharm-ai-plugin-and-chatgpt-setup.md)
- [Debugging notes](engineering-docs/implementation-notes/docker4pycharm/debugging.md)
- [Vibe-coding process bootstrap template, frozen copy](docker4pycharm/image-assets/vibe-coding-process.md)

## Implementation Notes And Decisions

- [User-requested session-record policy](engineering-docs/session-records/devcapsule/README.md)
- [Project-management resume and individual-projects framing session record](engineering-docs/session-records/devcapsule/2026-08-19-resume-verification-and-individual-projects.md)
- [Inspector hardening, samples, and workflow bootstrap session record](engineering-docs/session-records/devcapsule/2026-08-16-inspector-hardening-samples-and-workflow-bootstrap.md)
- [v021 external dogfood and V1 backlog session record](engineering-docs/session-records/devcapsule/2026-08-03-v021-external-dogfood-and-v1-backlog.md)
- [D-0004 configuration and images CLI session record](engineering-docs/session-records/devcapsule/2026-08-01-d-0004-configuration-and-images-cli.md)
- [Per-project IDE state split](engineering-docs/design-notes/docker4pycharm/2026-06-21-per-project-ide-state-split.md)
- [Git identity and remote credential transport](engineering-docs/design-notes/docker4pycharm/2026-06-22-git-identity-and-credentials.md)
- [Default JetBrains GL to Mesa software rendering](engineering-docs/design-notes/docker4pycharm/2026-06-22-mesa-software-gl-default.md)
- [Development sudo profile](engineering-docs/design-notes/docker4pycharm/2026-06-24-development-sudo-profile.md)
- [Python project UX defaults](engineering-docs/design-notes/docker4pycharm/2026-06-24-python-project-ux-defaults.md)
- [Docker-in-Docker implementation choice](engineering-docs/design-notes/docker4pycharm/docker-in-docker-implementation-choice.md)
- [Docker in containerized development environments TLDR](engineering-docs/design-notes/docker4pycharm/docker-in-containerized-development-environments.md)
- [Using PyCharm v0 for real Python projects](engineering-docs/implementation-notes/docker4pycharm/using-v0-for-real-python-projects.md)
- [Docker Hub namespace and publication plan](engineering-docs/implementation-notes/devcapsule/2026-07-15-docker-hub-namespace-and-publication-plan.md)
- [Capability-first PyCharm dogfood manual test](engineering-docs/implementation-notes/devcapsule/2026-07-24-capability-first-dogfood-manual-test.md)
- [Local PyCharm materialization and Python entrypoint](engineering-docs/implementation-notes/devcapsule/2026-07-29-local-pycharm-materialization-and-python-entrypoint.md)
- [NVIDIA CUDA base recipe specialized validation](engineering-docs/implementation-notes/devcapsule/2026-08-01-nvidia-cuda-base-recipe-validation.md)
- [Next functional dogfood stage from b5d42e8](engineering-docs/implementation-notes/devcapsule/2026-08-03-next-functional-dogfood-stage-plan.md)
- [Recursive dogfood E2E milestone plan](engineering-docs/implementation-notes/devcapsule/2026-08-06-recursive-dogfood-e2e-milestone-plan.md)
- [Recursive dogfood Stage 2 execution checklist](engineering-docs/implementation-notes/devcapsule/2026-08-06-recursive-dogfood-stage-2-execution-checklist.md)
- [DevCapsule V1 test backlog](engineering-docs/implementation-notes/devcapsule/2026-08-07-v1-test-backlog.md)
- [Host browser URL bridge TLDR](engineering-docs/implementation-notes/devcapsule/2026-08-17-host-browser-url-bridge-tldr.md)
- [V2 launcher-loss resource reconciliation](engineering-docs/implementation-notes/devcapsule/2026-08-18-v2-launch-resource-reconciliation.md)
- [Release and validation process](engineering-docs/implementation-notes/devcapsule/2026-09-01-release-and-validation-process.md)

## Bugs

- [X11 passthrough grants the container a full host session credential](engineering-docs/bugs/devcapsule/2026-08-16-x11-passthrough-grants-full-session-credential.md)
- [Detached DevCapsule containers exit and are never cleaned up](engineering-docs/bugs/devcapsule/2026-08-15-detached-successors-not-cleaned-up.md)
- [Codex ACP fails because explicit CODEX_HOME does not exist](engineering-docs/bugs/devcapsule/2026-08-03-codex-acp-missing-home.md)
- [Authorized development sudo is reported as enabled but is unusable](engineering-docs/bugs/devcapsule/2026-08-03-authorized-development-sudo-misreported.md)
- [PyCharm recommends its native launcher](engineering-docs/bugs/devcapsule/2026-08-03-jetbrains-native-launcher.md)
- [JetBrains Runtime disables alpha compositing on slow X11](engineering-docs/bugs/devcapsule/2026-08-03-jbr-slow-x11-alpha-compositing.md)
- [JetBrains embedded browser is suspended in the container](engineering-docs/bugs/devcapsule/2026-08-03-jcef-sandbox-container-preview.md)
- [Fresh clones require manual ecosystem bootstrap](engineering-docs/bugs/devcapsule/2026-08-03-ecosystem-aware-project-bootstrap.md)
- [Component tooling is not added to the runtime path](engineering-docs/bugs/devcapsule/2026-08-03-component-tooling-runtime-path.md)
- [PyCharm run-image network and Docker-option parity](engineering-docs/bugs/devcapsule/2026-07-23-pycharm-ambient-host-network.md)
- [Codium grants ambient passwordless sudo by default](engineering-docs/bugs/devcapsule/2026-07-16-codium-ambient-sudo-default.md)
- [PyCharm build emits fragile multiline RUN shell quoting](engineering-docs/bugs/devcapsule/2026-07-16-pycharm-build-multiline-exec-rendering.md)
- [Codium run lacks shared developer runtime options](engineering-docs/bugs/devcapsule/2026-07-13-codium-run-option-parity.md)
- [Bug template](engineering-docs/bugs/docker4pycharm/_template.md)
- [Concurrent projects sharing global settings lock](engineering-docs/bugs/docker4pycharm/2026-06-24-concurrent-projects-shared-global-settings-lock.md)

## Completed, Retired, And Deferred Tasks

- [VSCodium sandbox and foreground launch](engineering-docs/completed-tasks/devcapsule/2026-07-13-vscodium-sandbox-and-foreground-launch.md)
- [Completed task archive README](engineering-docs/completed-tasks/docker4pycharm/README.md)
- [Bootstrap process template V004 validation](engineering-docs/completed-tasks/docker4pycharm/2026-06-20-bootstrap-process-template-v004-validation.md)
- [Default host Docker passthrough validation retired](engineering-docs/completed-tasks/docker4pycharm/2026-06-20-default-host-docker-passthrough-validation-retired.md)
- [Explicit Docker-in-Docker validation](engineering-docs/completed-tasks/docker4pycharm/2026-06-20-explicit-docker-in-docker-validation.md)
- [Markdown preview Skiko/OpenGL hang retired](engineering-docs/completed-tasks/docker4pycharm/2026-06-20-markdown-preview-skiko-opengl-hang-retired.md)
- [Mesa/Skiko Markdown preview validation](engineering-docs/completed-tasks/docker4pycharm/2026-06-22-mesa-skiko-markdown-validation.md)
- [Development sudo account validation failure](engineering-docs/completed-tasks/docker4pycharm/2026-06-28-dev-sudo-account-validation.md)
- [Git remote credential manual validation deferred](engineering-docs/completed-tasks/docker4pycharm/2026-06-28-git-remote-validation-deferred.md)
- [Local Git identity edge-case validation](engineering-docs/completed-tasks/docker4pycharm/2026-06-30-local-git-identity-edge-validation.md)
- [PyCharm v0 MVP checkpoint](engineering-docs/completed-tasks/docker4pycharm/2026-06-30-pycharm-v0-mvp-checkpoint.md)
