# Configuration contract ready for owner PR integration

Implemented in 99ff26a on ws-component-catalog/intellij-idea, after merging
origin/main at 1eb8e76 via 710fd04. The owner operates the GitHub PR UI.

Project required/optional capabilities, explicit SDK-major constraints, local
IDE/agent/tool pins and omissions, read-only candidate checking, preview and
recoverable CLI edits are implemented. Readers omit unsupported optional tools;
launch can omit an unavailable optional download, preserving mandatory closure
and integrity errors. Personal pins and host decisions remain local.

Guide: docs/configuration/capabilities.md. No task/workstream profiles, release
bump, launcher replacement or self-hosting manifest/lock migration. Adoption
requires a client containing this implementation and the established baseline /
candidate / independent-restart transition; existing shipped readers cannot
learn the new envelope from data alone.

Full build passed: 1,245 unit tests, 10 packaged-PEX integration tests, mypy,
syntax/version/CLI smokes and documentation contract. Changed production code
against 710fd04: 574/574 lines (100%), 199/204 branches (97.55%). No new container
launch is claimed. Published status carries the detailed test and rollout record.
