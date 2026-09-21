---
id: R-UPGRADE-002
title: Component Status Operational Reliability
type: requirement
kind: concrete-requirement
status: accepted
priority: wanted
source_of_truth: repo
verification: [tests, manual]
external_refs: []
---

# R-UPGRADE-002: Component Status Operational Reliability

## Authority And Scope

Owner direction, 2026-09-21: publish the implemented discovery service now and
work toward proportionate operational excellence by V1. Do not let a single
failure cause an undetected loss of service. This is accepted follow-up owned
by `component-upgrades`, not implemented behavior or a new release gate.
Project-management continues to own release sequencing.

## Required Outcomes

1. **48-hour reporting freshness.** The public endpoint is retrievable, parseable
   under its advertised schema and carries an observation no older than 48 hours
   for every component in the supported probe inventory. Measure individual
   observation age as well as publication age. A fresh failure observation is
   honest reporting, not vendor health; re-stamping old observations is not fresh
   reporting. Define measurement frequency and record breaches before claiming
   this objective is operationally met.
2. **Explicit vendor uncertainty.** Transport errors, HTTP failures, missing
   platform artifacts, malformed metadata and semantic mismatches produce
   inconclusive observations. Preserve last-success evidence. Bounded retries
   distinguish transient symptoms from persistent incidents; a timeout alone
   does not establish a broken vendor contract. Persistent failure notifies a
   responsible maintainer without requiring an end-user report.
3. **User guidance.** Maintainers diagnose affected adapters, CLI versions and
   platforms, publish actionable issue/workaround guidance, and recommend CLI
   updates only after a fixing release exists. Preserve guidance for affected
   older clients even after current probes recover. Clients expose applicable
   guidance on their next check; no adopter telemetry or unsolicited messaging
   is required.
4. **Independent observation and alerts.** Monitor the public consumer path
   outside the publishing workflow and its scheduler. Detect publication failure,
   a job that never starts, an inaccessible or invalid feed, stale component
   observations and persistent probe failures. Alert early enough to act before
   the 48-hour deadline. Verify notification delivery to a named owner and an
   independent fallback; do not count two routes with the same sole point of
   failure as independent. A timestamp in a page or a failed action alone is
   insufficient alerting.
5. **Incident operation.** Document ownership, acknowledgment and escalation,
   bounded retry/alert deduplication, recovery notification, and review of stale
   diagnoses. Keep publication freshness and vendor integration health separate
   in the runbook and measurements.

## Acceptance Evidence

Exercise vendor HTTP/shape failures, one-component failure, publication rejection,
a scheduler that stops, an invalid/stale public feed and loss of the primary
notification path. Retain sanitized evidence that detection occurred, the intended
recipient actually received an actionable alert, and recovery was observed.
Test the independent monitor without depending on the failed publisher to trigger
it. Preserve normal launch, software selection and historical timestamps while
the service is unavailable. Automated tests alone do not prove external alert
delivery or sustained freshness.

## Decisions Still Needed

Choose the external monitor and independent notification destinations, thresholds
and retry/escalation timing, named operational owner, measurement/reporting window,
and supported CLI/adapter inventory with its retirement policy. Account setup and
GitHub UI operations remain with the owner under `WORKFLOW-LOCAL.md`. No provider,
paid service or alert recipient has been selected by this requirement.

## Current Baseline

Daily probes, a 72-hour feed expiry, authored expiring diagnoses and client
fallback exist under [R-UPGRADE-001](r-upgrade-001-component-version-sets.md).
Persistent failed probes currently publish without failing the job. Independent
monitoring, verified notifications and the 48-hour objective are outstanding.
See the [user/developer explanation](../../../docs/guides/component-freshness.md)
and [operator runbook](../../../component-status/README.md).
