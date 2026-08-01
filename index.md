# Documentation Index

Status: maintained index of repository markdown documentation.

When adding, deleting, or renaming any `.md` file, update this index in the
same change.

## Start Here

- [Developer overview](README.md)
- [Current status and handoff](CURRENT-STATUS.md)
- [Documentation index](index.md)
- [Agent instructions](AGENTS.md)
- [Requirements overview and index](REQUIREMENTS.md)
- [Human / agent workflow](WORKFLOW.md)

## Root Requirement Records

- [R-PRODUCT-001 Batteries-Included IDE Environments](docs/requirements/r-product-001-batteries-included-ide-environments.md)
- [R-PRODUCT-002 Explicit Host Boundaries](docs/requirements/r-product-002-explicit-host-boundaries.md)
- [R-PRODUCT-003 Durable Human/Agent Project Memory](docs/requirements/r-product-003-durable-human-agent-project-memory.md)
- [R-PRODUCT-004 Reusable Human/Agent Workflow](docs/requirements/r-product-004-reusable-human-agent-workflow.md)
- [R-PRODUCT-005 Incremental Human/Agent Execution Loop](docs/requirements/r-product-005-incremental-human-agent-execution-loop.md)
- [R-DOCS-001 Root Documentation Stays Implementation-Agnostic](docs/requirements/r-docs-001-root-documentation-stays-implementation-agnostic.md)
- [R-DOCS-002 Current User Docs Show Current Interfaces](docs/requirements/r-docs-002-current-user-docs-show-current-interfaces.md)
- [R-GTM-001 Compelling V1 Announcement For Adopters](docs/requirements/r-gtm-001-compelling-v1-announcement-for-adopters.md)

## Design Decisions

- [Decision record template](docs/decisions/_template.md)
- [D-0001 Capability-First CLI Model](docs/decisions/d-0001-capability-first-cli-model.md)
- [D-0004 Configuration Resolution And Guided Run Experience](docs/decisions/d-0004-configuration-resolution-and-guided-run.md)

## Specifications

- [DevCapsule V1 state and persistence](docs/specifications/state-and-persistence.md)

## Active DevCapsule Development

- [DevCapsule Python CLI](devcapsule/README.md)
- [DevCapsule V1 user experience design draft](devcapsule/docs/v1-user-experience.md)
- [DevCapsule test suites](devcapsule/tests/README.md)
- [DevCapsule implementation requirements overview](devcapsule/REQUIREMENTS.md)
- [R-ENV-001 Dockerized PyCharm Runtime](devcapsule/docs/requirements/r-env-001-dockerized-pycharm-runtime.md)
- [R-STATE-001 Persistent IDE State And Plugins](devcapsule/docs/requirements/r-state-001-persistent-ide-state-and-plugins.md)
- [R-SETTINGS-001 Per-IDE Settings Profile Seed](devcapsule/docs/requirements/r-settings-001-per-ide-settings-profile-seed.md)
- [R-SCOPE-001 Explicit Host Filesystem Exposure](devcapsule/docs/requirements/r-scope-001-explicit-host-filesystem-exposure.md)
- [R-DEV-001 Useful Development Tooling Baseline](devcapsule/docs/requirements/r-dev-001-useful-development-tooling-baseline.md)
- [R-GIT-001 Git Identity And Credentials Without Host Credential Mounts](devcapsule/docs/requirements/r-git-001-git-identity-and-credentials-without-host-credential-mounts.md)
- [R-DOCKER-001 Explicit Docker Capability Profiles](devcapsule/docs/requirements/r-docker-001-explicit-docker-capability-profiles.md)
- [R-PROJECT-001 Per-Project IDE Runtime State](devcapsule/docs/requirements/r-project-001-per-project-ide-runtime-state.md)
- [R-CONC-001 Concurrent Project Sessions](devcapsule/docs/requirements/r-conc-001-concurrent-project-sessions.md)
- [R-PROC-001 Durable Human/Agent Project Memory](devcapsule/docs/requirements/r-proc-001-durable-human-agent-project-memory.md)
- [R-DOCS-001 Generated Documentation Index](devcapsule/docs/requirements/r-docs-001-generated-documentation-index.md)
- [R-DOCS-002 User-Level Documentation Coevolves With User-Visible Behavior](devcapsule/docs/requirements/r-docs-002-user-level-documentation-coevolves-with-user-visible-behavior.md)
- [R-IDE-CONFIG-001 Configuration-First End-User CLI Model](devcapsule/docs/requirements/r-ide-config-001-configuration-first-end-user-cli-model.md)
- [R-PYTHON-MVP-001 Source Checkout Install And Run](devcapsule/docs/requirements/r-python-mvp-001-source-checkout-install-and-run.md)
- [R-PYTHON-MVP-002 Single-File Python CLI Artifact](devcapsule/docs/requirements/r-python-mvp-002-single-file-python-cli-artifact.md)
- [R-PYTHON-MVP-003 Python MVP Feature Scope](devcapsule/docs/requirements/r-python-mvp-003-python-mvp-feature-scope.md)
- [R-IMAGE-BUILD-001 Python-Native Composable Image Building](devcapsule/docs/requirements/r-image-build-001-python-native-composable-image-building.md)
- [R-FRAMEWORK-001 Shared Python DevCapsule Orchestration](devcapsule/docs/requirements/r-framework-001-shared-python-docker4ide-orchestration.md)
- [Click-based CLI parsing brief](devcapsule/implementation-notes/click_based_cli_parsing_brief.md)
- [PyCharm image vibe-coding bootstrap template](devcapsule/devcapsule/assets/pycharm/image-assets/vibe-coding-process.md)
- [TypeScript five-in-a-row sample project](devcapsule/tests/resources/sample_projects/typescript_tictactoe_5inrow/README.md)

## Product And Positioning

- [Draft pitch: batteries included, boundaries explicit](docs/draft-pitch.md)
- [LinkedIn announcement draft](docs/linkedin-announcement.md)
- [V1 announcement draft](docs/v1-announcement.md)
- [Working backwards press release](docs/working-backwards-press-release.md)

## Docker4PyCharm Historical Reference

- [Docker PyCharm isolation README](docker4pycharm/README.md)
- [Historical root project brief](docker4pycharm/historical-root-README.md)
- [Post-MVP refactoring strategy](docker4pycharm/FUTURE_AGENT_REFACTORING_BRIEF.md)
- [PyCharm AI plugin and ChatGPT subscription setup](docker4pycharm/user.md)
- [Debugging notes](docker4pycharm/debugging.md)
- [Vibe-coding process bootstrap template](docker4pycharm/image-assets/vibe-coding-process.md)

## Implementation Notes And Decisions

- [User-requested session-record policy](devcapsule/implementation-notes/session-records/README.md)
- [D-0004 configuration and images CLI session record](devcapsule/implementation-notes/session-records/2026-08-01-d-0004-configuration-and-images-cli.md)
- [Per-project IDE state split](docker4pycharm/implementation-notes/2026-06-21-per-project-ide-state-split.md)
- [Git identity and remote credential transport](docker4pycharm/implementation-notes/2026-06-22-git-identity-and-credentials.md)
- [Default JetBrains GL to Mesa software rendering](docker4pycharm/implementation-notes/2026-06-22-mesa-software-gl-default.md)
- [Development sudo profile](docker4pycharm/implementation-notes/2026-06-24-development-sudo-profile.md)
- [Python project UX defaults](docker4pycharm/implementation-notes/2026-06-24-python-project-ux-defaults.md)
- [Docker-in-Docker implementation choice](docker4pycharm/implementation-notes/docker-in-docker-immplementation-choice.md)
- [Docker in containerized development environments TLDR](docker4pycharm/implementation-notes/docker_in_devcontainer_tldr.md)
- [Using PyCharm v0 for real Python projects](docker4pycharm/implementation-notes/using-v0-for-real-python-projects.md)
- [Docker Hub namespace and publication plan](devcapsule/implementation-notes/2026-07-15-docker-hub-namespace-and-publication-plan.md)
- [Capability-first PyCharm dogfood manual test](devcapsule/implementation-notes/2026-07-24-capability-first-dogfood-manual-test.md)
- [Local PyCharm materialization and Python entrypoint](devcapsule/implementation-notes/2026-07-29-local-pycharm-materialization-and-python-entrypoint.md)
- [NVIDIA CUDA base recipe specialized validation](devcapsule/implementation-notes/2026-08-01-nvidia-cuda-base-recipe-validation.md)

## Bugs

- [PyCharm run-image network and Docker-option parity](devcapsule/implementation-notes/bugs/2026-07-23-pycharm-ambient-host-network.md)
- [Codium grants ambient passwordless sudo by default](devcapsule/implementation-notes/bugs/2026-07-16-codium-ambient-sudo-default.md)
- [PyCharm build emits fragile multiline RUN shell quoting](devcapsule/implementation-notes/bugs/2026-07-16-pycharm-build-multiline-exec-rendering.md)
- [Codium run lacks shared developer runtime options](devcapsule/implementation-notes/bugs/2026-07-13-codium-run-option-parity.md)
- [Bug template](docker4pycharm/implementation-notes/bugs/_template.md)
- [Concurrent projects sharing global settings lock](docker4pycharm/implementation-notes/bugs/2026-06-24-concurrent-projects-shared-global-settings-lock.md)

## Completed, Retired, And Deferred Tasks

- [VSCodium sandbox and foreground launch](devcapsule/implementation-notes/completed-tasks/2026-07-13-vscodium-sandbox-and-foreground-launch.md)
- [Completed task archive README](docker4pycharm/implementation-notes/completed-tasks/README.md)
- [Bootstrap process template V004 validation](docker4pycharm/implementation-notes/completed-tasks/2026-06-20-bootstrap-process-template-v004-validation.md)
- [Default host Docker passthrough validation retired](docker4pycharm/implementation-notes/completed-tasks/2026-06-20-default-host-docker-passthrough-validation-retired.md)
- [Explicit Docker-in-Docker validation](docker4pycharm/implementation-notes/completed-tasks/2026-06-20-explicit-docker-in-docker-validation.md)
- [Markdown preview Skiko/OpenGL hang retired](docker4pycharm/implementation-notes/completed-tasks/2026-06-20-markdown-preview-skiko-opengl-hang-retired.md)
- [Mesa/Skiko Markdown preview validation](docker4pycharm/implementation-notes/completed-tasks/2026-06-22-mesa-skiko-markdown-validation.md)
- [Development sudo account validation failure](docker4pycharm/implementation-notes/completed-tasks/2026-06-28-dev-sudo-account-validation.md)
- [Git remote credential manual validation deferred](docker4pycharm/implementation-notes/completed-tasks/2026-06-28-git-remote-validation-deferred.md)
- [Local Git identity edge-case validation](docker4pycharm/implementation-notes/completed-tasks/2026-06-30-local-git-identity-edge-validation.md)
- [PyCharm v0 MVP checkpoint](docker4pycharm/implementation-notes/completed-tasks/2026-06-30-pycharm-v0-mvp-checkpoint.md)
