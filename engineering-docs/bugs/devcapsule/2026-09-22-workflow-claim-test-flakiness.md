---
status: confirmed
severity: minor
target: none
owner: workflow-improvements
opened: 2026-09-22
requirements: [R-PRODUCT-006]
---

# Claim Lifecycle Test Depends On Wall-Clock Timing

## Evidence

The owner reported these Actions runs at the same revision:

- [Failed run 35707699970](https://github.com/ccozianu/devcapsule/actions/runs/35707699970).
- [Successful run 35723771930](https://github.com/ccozianu/devcapsule/actions/runs/35723771930).

The supplied failure is in
`tests/test_workflow_coordination.py::test_claim_is_shown_live_expires_and_releases`:

```text
assert claim(sender, "alpha", "the config fix") is None
AssertionError: assert 'eeff6fa65e050a97eda3fb7c8a2f43c5df654322' is None
```

Run outcomes and same-revision comparison are owner-supplied evidence; the
complete hosted logs were not independently inspected.

## Cause And Local Confirmation

The test calls `claim` twice without controlling time and assumes the second
call is unchanged. The implementation captures the current UTC time on each
call, derives the expiry, and serializes both timestamps to whole seconds.
It returns `None` only when the serialized claim equals the stored claim.
The assertion passes if both timestamps fall in the same second, and fails
if the calls cross a second boundary. Git subprocess execution lies between
the calls; no execution-speed assumption can guarantee the desired timing.

A bounded probe using the existing test's disposable bare-remote fixture and
the public `now` argument confirmed the cause without sleeping or touching
shared coordination: a claim at 2026-09-22T12:00:00Z created a commit, the same
claim at the identical time returned `None`, and the same slice one second
later created another commit. This establishes the test's timing dependency;
it does not independently settle the desired renewal contract.

## Owner Direction And Temporary Treatment

The owner requested an xfail and a bug, explicitly declining a quick fix
because the failure exhibits a wrong approach to testing. The existing test
is marked `xfail(strict=False, raises=AssertionError)` with this record named
in the reason. Its timing and assertions are unchanged. Non-strict behavior
allows the existing intermittent passes without turning XPASS into CI failure.
An unexpected non-assertion exception still fails normally.

This is quarantine, not correction or closure. The marker covers a combined
lifecycle test, so its later assertion failures are also expected failures;
the suite no longer provides a reliable gate for those obligations through
this test. Do not interpret a passing rerun as restored coverage.

## Required Follow-Up And Close Criteria

Workflow-improvements owns the design review and repair. Establish intended
claim identity, renewal and expiry behavior from the contract first, then
test those obligations with deliberate temporal inputs and boundary cases.
Separate live display, unchanged-claim behavior, renewal, expiry and release
where needed so a failure identifies an obligation and does not hide the rest.
Assess adjacent clock-dependent tests within that bounded review. Freezing
both calls to the same instant alone must not substitute for deciding and
testing what advancing time means. Neither sleeps nor retries are a repair.

Close after the agreed contract is covered without wall-clock-speed
assumptions, the xfail is removed, and the relevant checks pass. No runtime
claim change or release-blocking classification is authorized by this report.

## Quarantine Validation

The full `nox -s build` passed after adding the marker: 1,044 tests passed,
18 deselected, one existing xfail, and this test XPASS. Type checking and all
nine packaged checks passed. XPASS is consistent with the reported flakiness;
it is not evidence of a repair. Runtime and the test body remain unchanged.
