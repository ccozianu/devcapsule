# DevCapsule component update status

Generated: 2026-10-04T01:32:19.880044+00:00. Valid until: 2026-10-07T01:32:19.880044+00:00.

If that deadline has passed, this page is stale. Probe success only establishes that the named adapter could read metadata from this runner. It does not certify installed software, security coverage, installation, or every released CLI.

Source revision: `8ba2235a9b022c4089dc8c4c3834489fd89509eb`. Probe CLI: `0.2.16.dev0`.

[Machine-readable compatibility contract v1](compatibility-v1.json)

## Observations

| Component / adapter | Platform / baseline | Result | Candidates | Last successful probe | Consecutive failures | Detail |
|---|---|---|---|---|---|---|
| intellij / intellij-v1 | linux-amd64 / 2026.2.3 | ok | &#8212; | 2026-10-04T01:32:19.880044&#43;00:00 | 0 | This release feed does not assess installed-version support. |
| playwright / playwright-v1 | linux-amd64 / 1.63.0 | ok | &#8212; | 2026-10-04T01:32:19.880044&#43;00:00 | 0 | This release feed does not assess installed-version support. |
| pycharm / pycharm-v1 | linux-amd64 / 2026.2.0.1 | ok | 2026.2.3 | 2026-10-04T01:32:19.880044&#43;00:00 | 0 | This release feed does not assess installed-version support. |
| codium / codium-v1 | linux-amd64 / 1.126.04524 | inconclusive | &#8212; | 2026-10-03T06:55:50.400954&#43;00:00 | 1 | Vendor discovery unavailable at https://api.github.com/repos/VSCodium/vscodium/releases/latest: HTTP Error 403: rate limit exceeded |
| codex / codex-v1 | linux-amd64 / 0.153.4 | inconclusive | &#8212; | 2026-10-01T06:52:01.142796&#43;00:00 | 3 | Distribution check unavailable at https://registry.npmjs.org/@openai&#37;2Fcodex: metadata exceeds 16 MiB. Retry &#39;project versions check&#39;&#59; saved choices are unchanged. |
| claude-code / claude-code-v1 | linux-amd64 / 2.1.261 | ok | 2.1.289 | 2026-10-04T01:32:19.880044&#43;00:00 | 0 | This release feed does not assess installed-version support. |
| antigravity-cli / antigravity-cli-v1 | linux-amd64 / 1.1.24 | ok | 1.2.16 | 2026-10-04T01:32:19.880044&#43;00:00 | 0 | This release feed does not assess installed-version support. |
| postgresql-client / postgresql-client-v1 | linux-amd64 / 16 | ok | &#8212; | 2026-10-04T01:32:19.880044&#43;00:00 | 0 | Upstream major 16 support ends 2028-11-09&#59; distribution backports are not assessed. Latest upstream minor: 16.15&#59; installed minor is not recorded in this base lock. |

## Maintained diagnoses

A failed probe alone never creates an upgrade recommendation. Diagnoses below are reviewed separately and apply only to their named adapters, CLI versions and platforms.

No maintained diagnoses. This does not establish that every client can check for updates.
