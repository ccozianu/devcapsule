# Development

How DevCapsule is built and tested, for contributors and agents. The
[developer brief](../../DEVELOPING.md) at the repository root is the short
entry point; the documents here carry the detail, one subject each.

| Document | Answers |
|---|---|
| [Developer environment](developer-environment.md) | How to set up a checkout, run the gate, build the executable, and tell the shipped CLI from the development one |
| [Source layout](source-layout.md) | Where things live in the repository and inside the `devcapsule` package, and which boundaries are enforced |
| [Unit tests](unit-tests.md) | What `nox -s tests` runs, how the suite is organized, its fixtures and resources, and what the hosted runner does |
| [Integration tests](integration-tests.md) | The checks that cross a packaging or process boundary without Docker: the built executable, the CLI smoke, the type check, the documentation contract |
| [End-to-end tests](e2e-tests.md) | The Docker-backed suites, each with its entry point, what it proves, what it needs, and the evidence it leaves |

Placement rule: a document here describes how the project is developed and
verified today. Requirements, decisions, specifications and release records
keep their own homes under `engineering-docs/`; see
[its README](../README.md).
