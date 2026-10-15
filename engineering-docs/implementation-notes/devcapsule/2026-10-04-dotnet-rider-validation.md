# Linux .NET SDK and Rider component validation

Date: 2026-10-04. Workstream: `component-catalog`.
Requirements: R-PRODUCT-001, R-PRODUCT-002, R-DOCS-002.

## Delivered behavior

The owner requested the latest stable Linux .NET SDK first, then JetBrains
Rider and a noVNC smoke comparable to IntelliJ's. `dotnet` adds the complete
SDK to an existing IDE selection; `dotnet-ide` selects Rider and automatically
includes `dotnet-sdk`. A lock missing Rider's dependency is rejected. Existing
locks and unrelated component selections retain their behavior.

The SDK installs offline from its checksum-pinned archive into `/opt/dotnet`,
with `PATH` and `DOTNET_ROOT` set. It includes MSBuild, runtime and targeting
packs. Telemetry is off by default. NuGet caches and user tools belong to the
persistent capsule home, with no host credential or SDK import. The new whole
TAR-directory contribution rejects traversal, links, devices and oversized
archives, retaining executable permissions without setuid/setgid bits.

Rider uses the shared JetBrains adapter, bundled Java runtime, independent
`rider/*` persistent state and stale-directory-lock recovery. JetBrains handles
licensing in the UI; installation does not purchase a license or activate a
trial. Other SDK versions and workloads are outside this slice.

## Vendor provenance

Read on 2026-10-04:

- [Microsoft release index](https://builds.dotnet.microsoft.com/dotnet/release-metadata/releases-index.json)
  and [.NET 10 release metadata](https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json):
  SDK **10.0.401**, released 2026-09-08, latest stable SDK. The .NET 11 entry
  is a release candidate and intentionally excluded.
- [JetBrains Rider release feed](https://data.services.jetbrains.com/products/releases?code=RD&latest=true&type=release):
  **2026.2.3.1**, released 2026-10-01, Linux x64 archive.
- [Rider installation guide](https://www.jetbrains.com/help/rider/Installation_guide.html)
  and [manual .NET installation](https://learn.microsoft.com/en-us/dotnet/core/install/linux-scripted-manual)
  explain complete archive installations and environment requirements.

| Artifact | Bytes | Verified SHA-256 |
|---|---:|---|
| `dotnet-sdk-10.0.401-linux-x64.tar.gz` | 240059572 | `137268c8ad939c064ff1ee2a6fdf0899d8725377114ea012fbd1ad5fa2550418` |
| `JetBrains.Rider-2026.2.3.1.tar.gz` | 2398189581 | `fa4b09a5f7cf4b6635b093adc7313991778a8dc74f25614a2b8976b04dee5d4e` |

The SDK's complete download also matched Microsoft's published SHA-512,
recorded in the lock's `upstream-sha512`. Rider's complete download matched
its vendor `.sha256` file. Both have read-only discovery adapters and probes
in the component-status publication policy. Installation upgrades remain
reviewed catalog changes.

## Validation

Implementation commit: `4df3e4f`.

`nox -s build` passed: 1,138 tests, one existing expected failure and one
existing expected pass, type checks, source and built-executable smokes,
nine packaging integration tests and the documentation contract.
Logs: `.git/rider-build.log` and `.git/rider-final-build.log`. The final gate
passed again after the startup-only component-browser mode, evidence and
resumption records were complete.

The real startup smoke passed. The tested executable's SHA-256 is
`13893e4af2eccb1bc949c354cbebf9e2b9eb4fde63e609dc1f83de72918e8269`.
It is a local validation artifact, reporting source revision `unknown`;
its checksum identifies the tested bytes. It was built from the implementation
now committed as `4df3e4f`, before that commit was made.

The [repeatable smoke commands](../../development/e2e-tests.md#rider-and-net-sdk-smoke)
create a disposable project with host networking, build/run a package-free C#
console application as the normal capsule user, check HTTP/window/pixel facts,
and retain noVNC screenshots and video. Agent mode additionally requires an
editor-saved marker and visual recognition. A license screen cannot satisfy
that stronger criterion. Agent credentials remain in the parent.

## Observed runs and limits

Evidence lives under `devcapsule-src/dist/e2e-evidence/ide-smoke/<run>/rider/`.

| Run | Mode | Result |
|---|---|---|
| `20261004T081323Z-95cbac` | Codex / GPT-6 Astra, child component browser | SDK build/run and GUI startup passed; saved-edit scenario **failed** at mandatory Rider license activation |
| `20261004T081836Z-932fc8` | `--display --surface rider --component-browser` | **Passed**, including SDK identity, C# build/run, HTTP, Rider window and noVNC pixels/video |

Both used image
`sha256:41a5ebbeeec7c2be46783dc104c8812eab95b3778851d15b552ae59a95388736`,
formed on pinned `v0.2.12-rc5` / `ubuntu-24.04@9`. The child runtime's checksum
matched the selected executable. The Playwright binding came from the component's
verified wheels; the parent's browser path was deliberately nonexistent.
The browser ran inside the child component and independently rendered an HTML
fixture. The startup repeat took 20 seconds after the first image build.

The C# fixture restored from local SDK packs with all NuGet sources cleared,
built with zero compiler warnings/errors and printed `DevCapsule .NET smoke passed`.
`dotnet --version` also returned 10.0.401 from a login shell. An SDK diagnostic
reported an issue verifying optional workloads; `dotnet workload list` succeeded
and listed none installed, as intended. No workload update was attempted.

The agent reached Rider's main window and the detected `Smoke` project through
noVNC, then found mandatory activation. Free non-commercial use also required
JetBrains login. Closing the license dialog asked to exit the IDE or return
to activation. No account was accessed, no trial was activated, and no marker
was saved. The harness correctly retained a failure for the saved-edit test.
This establishes GUI startup, **not licensed editing, debugging, SDK detection
inside Rider, or persistence after an editor interaction**. Those remain for
an activated Rider session; the `.NET` CLI proof is independent.

![Rider main window and mandatory activation](assets/2026-10-04-rider-activation.png)

The implementing agent reviewed this screenshot and the earlier noVNC frame.
The script-launcher and Java-options notices match the shared JetBrains runtime;
neither prevented startup. Raw recordings and model transcripts remain local.
The model's CLI selection is recorded without claiming a server-reported model
identity, which Codex JSONL does not supply.

Both test containers, disposable projects and every listed project-record path
were confirmed removed. Vendor downloads and the materialized image remain in
the normal cache for reuse. Raw launcher logs contain ephemeral desktop URLs;
the permanent screenshot and this record contain no access token.

Branch delivery uses SSH Git. The owner opens and merges the PR in GitHub's UI
under `WORKFLOW-LOCAL.md`; no release was cut or website deployed.
