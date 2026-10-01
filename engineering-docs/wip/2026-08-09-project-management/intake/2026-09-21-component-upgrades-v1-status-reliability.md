# V1 component status operational objectives

Sender: component-upgrades
Recipient: project-management
Date: 2026-09-21

The owner asked to publish the current component-discovery/status-service slice
now and work toward operational excellence by V1. Please include the accepted
R-UPGRADE-002 follow-up in the V1 scope/sequence discussion. Acceptance means
recording its place in the portfolio and resolving sequencing with the owner;
implementation stays with component-upgrades. This is not a request to make the
current checkpoint wait for the operational work or to impose a new release gate.

Canonical record on ws-component-upgrades/v1:
engineering-docs/requirements/product/r-upgrade-002-status-operational-reliability.md
User/developer explanation: docs/guides/component-freshness.md

Objectives: public component observations no older than 48 hours; explicit
inconclusive results and persistent-vendor-failure notification; independent
monitoring of the public feed outside its publisher/scheduler; verified owner
and fallback alert delivery; incident/recovery drills. Current service has daily
probes and 72-hour expiry, but failed probes do not fail the job and no independent
monitor or verified notification route exists. Provider, routes, thresholds,
operational owner and supported older-adapter window remain owner decisions.

The current checkpoint awaits owner PR opening/merge through the GitHub UI.
WORKFLOW-LOCAL.md now reiterates owner-only GitHub integration beyond agents'
ordinary Git operations over SSH; do not probe gh or use connectors for delivery.
