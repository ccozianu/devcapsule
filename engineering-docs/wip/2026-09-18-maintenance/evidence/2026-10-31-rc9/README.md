# RC9 component refresh and release preparation

The owner selected agent upgrades on 2026-10-31 and requested stable IDE
updates, particularly the JetBrains security updates. This is preparation
for v0.3.0-rc9, not acceptance of the final release.

## Component selection

| Component | Previous default | RC9 default |
|---|---|---|
| Codex | 0.163.0 | 0.166.0 |
| Claude Code | 2.1.302 | 2.1.314 |
| Antigravity CLI | 1.4.2 | 1.4.12 |
| PyCharm | 2026.2.0.1 | 2026.2.4 |
| IntelliJ IDEA | 2026.2.3 | 2026.2.4 |
| Rider | 2026.2.3.1 | 2026.2.4 |
| VSCodium | 1.126.04524 | 1.143.17232 |
| Visual Studio Code | 1.143.1 | 1.144.0 |
| Eclipse Java | 2026-09-R | unchanged |

Sources: the [Codex npm channel](https://registry.npmjs.org/@openai/codex/latest),
[Claude release channel](https://downloads.claude.ai/claude-code-releases/latest),
[Antigravity Linux manifest](https://antigravity-cli-auto-updater-974169037036.us-central1.run.app/manifests/linux_amd64.json),
[JetBrains release feed](https://data.services.jetbrains.com/products/releases?code=PCP,IIU,RD&latest=true&type=release),
[VSCodium releases](https://github.com/VSCodium/vscodium/releases),
[Microsoft stable feed](https://update.code.visualstudio.com/api/update/linux-x64/stable/latest),
and [Eclipse packages](https://www.eclipse.org/downloads/packages/).
The Eclipse 2026-12 milestone is a development build and was excluded.
All nine complete artifacts passed vendor integrity and applicable size checks;
[artifacts.json](artifacts.json) records the URLs, sizes and verified digests.
These are stable-channel selections; this record does not claim a particular
CVE is fixed without an advisory establishing it.

The catalog advances to embedded-30. Earlier pins and edges remain available
for existing locks. The repository's shared schema-1 configuration is retained:
`project init --regenerate` would also migrate its requirements/IDE contract,
which is outside this component refresh. The running baseline
`/usr/local/bin/devcapsule0`, version 0.3.0rc8, source `8d41fabe9f7e`, validated
that existing manifest and lock with `project config check --manifest
.devcapsule/devcapsule.toml --lock .devcapsule/devcapsule.linux-amd64.lock
--json` (exit 0). No project configuration file was edited.

## Agent startup

The four agent downloads passed their vendor integrity checks: npm SHA-512,
Claude's manifest SHA-256 and size, and Antigravity's manifest SHA-512.
SHA-256 values in the catalog were computed from those same complete bytes.

[The probe](agent-startup.sh) ran in a disposable container on
`mycodespaceai/devcapsule-base:v0.3.0.rc6`, image
`sha256:465cd9065654561151a4435bef90a5e15f6a51a1369c16794203529bb5848a4f`,
with host networking. It installed the two npm tarballs through explicitly
named file dependencies, matching production's offline npm layout, and ran
all three CLIs as a fresh uid-1000 user. No account state was supplied.

[The log](agent-startup.log) records Codex 0.166.0, its feature listing and
`exec --help`; Claude Code 2.1.314 and `--help`; Antigravity 1.4.12, help and
changelog. Claude's headless probe returned the expected unauthenticated
result, with zero API usage; its debug line confirms the seeded
`bypassPermissions` default was loaded. The three seed files were
byte-identical after execution. Authenticated actions, model access and
first-use account notices are still downloaded-candidate acceptance work.

Initial probe setup errors were corrected before this successful run: the
artifact bind needed the host source of the nested cache mount; Codex's npm
platform package needed its explicit dependency alias; and the script needed
a file input independent of the child CLIs' standard input.

## Build and documentation checks

The 101 existing resolution/initialization tests pass with regenerated golden
locks and updated default-version expectations. Release-document tests pass
(92). The website build and check pass (252 pages, 21,031 local links, assets
and anchors) after adding the required metadata block to the release notes.

The initial full gate used a long host-mounted scratch path: Unix sockets
exceeded their path limit and a host-isolation fixture received a mountable
path. The rerun uses `/opt/devcapsule-gate/rc9`; the directory first had to be
created with the development user's ownership. These setup failures did not
require product changes. The full gate then passed: 2,644 unit tests (40 deselected, one expected
failure and one non-strict unexpected pass), 18 packaging integration tests,
type and syntax checks, CLI/PEX smoke, documentation contract, and 357
web-console tests. All five updated IDEs completed the graphical startup checks below.

## Graphical startup checks

The built local PEX is identified by [startup-build.json](startup-build.json).
The smoke harness uses fresh projects and the pinned recipe-11 base, verifies
the desktop and token-protected console endpoints, finds an IDE X11 window,
keeps rendered pixels, and checks that the child runtime has exactly the
selected PEX's SHA-256. Host networking follows the local validation policy.

The first run (`20261031T011008Z-702c9c`) completed VSCodium and PyCharm,
including cleanup, then its runner ended with SIGTERM (exit 143) before
IntelliJ startup; there was no failing test assertion. Its interrupted
IntelliJ fixture and records were removed. The remaining surfaces completed in run `20261031T011314Z-518a42`: three
passed, three deselected, exit 0. Both runs used the same PEX checksum.

| Surface | Retained facts and screenshot | Observation |
|---|---|---|
| VSCodium | [facts](codium/facts.json), [desktop](codium/desktop.png) | Welcome/editor shell with fixture project |
| PyCharm | [facts](pycharm/facts.json), [desktop](pycharm/desktop.png) | First-use agreement |
| VS Code | [facts](vscode/facts.json), [desktop](vscode/desktop.png) | Welcome/sign-in screen |
| Rider | [facts](rider/facts.json), [desktop](rider/desktop.png) | Splash/window then first-use agreement |
| IntelliJ | [facts](intellij/facts.json), [desktop](intellij/desktop.png) | Splash/window then first-use agreement |

Rider's .NET 10.0.401 SDK also [built](rider/dotnet-build.txt) and
[ran](rider/dotnet-run.txt) the package-free C# fixture. Its
[component browser](rider/component-browser.json) and IntelliJ's
[component browser](intellij/component-browser.json) rendered test HTML.
The local PEX is a dirty-source preparation build with `source_revision:
unknown`, not a published candidate; its checksum identifies the exact tested
artifact. The catalog's later edits only replace provisional evidence strings
with these observations; the pins and runtime behavior are unchanged.

VSCodium shows its welcome/editor shell and the fixture project. The three
JetBrains screenshots show their first-use agreements. These are startup observations, not proof of
a saved edit, account entitlement, licensing, or persistence after relaunch.

## Release obligations

The preparation promotes 0.3.0 documentation, deprecates 0.2.15 and marks
0.2.14/0.2.12 unsupported. Adopter notes accompany the promotion. A local
`docs-0.3.0` ref supports build checks; publication follows integration of
its promotion commit into the release. The docs tree must match the accepted
final tag.

The human merges the preparation into release and its main propagation.
Only after that disposition is resolved may rc9 be tagged and the published
PEX downloaded and checked. C17, the remaining nine documentation proposals,
and downloaded-candidate acceptance retain their recorded dispositions;
preparing a candidate does not silently close them.
