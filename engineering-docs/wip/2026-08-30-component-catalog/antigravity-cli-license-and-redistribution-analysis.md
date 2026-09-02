# Antigravity CLI: License And Redistribution Analysis

Performed 2026-09-02, the analysis the v1 scope ledger gates track 2 on,
per the delivery contract in this workstream's `CURRENT-STATUS.md`. The
facts below were verified against the live distribution channel on that
date; the artifact verification was performed hands-on.

## Identity And Distribution Facts

- **Product**: Google Antigravity CLI (`agy`), the terminal surface of the
  Antigravity agent platform. Proprietary; the
  [GitHub repository](https://github.com/google-antigravity/antigravity-cli)
  carries docs, examples, and issues — no source, no LICENSE file.
- **Official channel**: `curl -fsSL https://antigravity.google/cli/install.sh | bash`
  ([install docs](https://antigravity.google/docs/cli/install/)). The
  script queries a manifest endpoint
  (`…run.app/manifests/{platform}.json`) that serves **latest-only**:
  no version selection exists in the official installer.
- **But the artifacts themselves are versioned and immutable**: the
  manifest resolves to
  `https://storage.googleapis.com/antigravity-public/antigravity-cli/<version>-<build>/linux-x64/cli_linux_x64.tar.gz`
  with a published **sha512**. Verified 2026-09-02 for version `1.1.24`
  (build `6130423206641664`): 56,692,103 bytes, manifest sha512 matches
  the downloaded artifact, locally computed
  `sha256 = cff1fb7ed735da72c35658645a4f916cf74f020d4cd30ab95ebe8c2a49a4d569`.
  The archive contains exactly one file: the `antigravity` executable.
- **State and credentials**: settings at `~/.gemini/antigravity-cli/`
  (e.g. `settings.json` with `modelProvider`). Authentication is the OS
  keyring plus a browser Google sign-in, with an SSH-style
  print-a-URL flow for headless sessions, or `GEMINI_API_KEY` in the
  environment with `modelProvider = gemini`. Installation alone
  authenticates nothing and grants no host access.

## Terms Analysis

Governing documents: the Google Terms of Service plus the
[Google Antigravity Additional Terms](https://antigravity.google/terms/)
(enterprise channels substitute administrator-accepted terms).

- **Acceptance is per-user and implicit in acquisition**: "BY
  DOWNLOADING, INSTALLING, OR OTHERWISE ACCESSING OR USING … YOU AGREE
  TO BE BOUND". The installer shows no click-through; the download *is*
  the acceptance act. Therefore DevCapsule must put an explicit
  authorization in front of the download — the terms cannot be accepted
  by a tool on a developer's behalf.
- **No redistribution grant exists**: the Additional Terms are silent on
  redistribution and the base Google ToS grant no right to distribute
  the software. Publishing images containing the binary — including any
  DevCapsule base — is not licensed. (D-0005 forbids agent CLIs in bases
  independently.)
- **A developer's own cached local image is not redistribution**: the
  binary is downloaded by the authorized user, onto their machine, into
  a locally-built, locally-cached environment image that is never
  pushed. No copy reaches a third party. This is the same reading the
  Claude Code analysis established, and the risk clause in the delivery
  contract ("if Antigravity's terms forbid even cached local images") is
  **not triggered** — the 2026-08-30 contract stands unmodified.
- **Interaction data**: use sends interaction data to Google per the
  terms — a disclosure for the authorization prompt, not an obstacle.
- **Third-party access prohibition**: the terms forbid third-party tools
  accessing *the service* through Antigravity OAuth. Not implicated:
  DevCapsule installs and launches the CLI for the developer; it does
  not access Google's service or impersonate the CLI's credentials.

## Consequences For The Component

1. **Delivery policy**: `local-materialization` with a per-developer
   acquisition gate, exactly the Claude Code pattern —
   `acquisition-authorization: antigravity-download`,
   `distribution: user-acquired-not-redistributed`,
   `terms-url: https://antigravity.google/terms/`.
2. **Pinned identity**: pin the versioned GCS artifact URL with our
   independently computed sha256 (the materialization layer's checksum),
   recording the manifest's sha512 as upstream provenance. Because the
   official channel is latest-only, advancing the pin is a deliberate
   re-curation — resolve the manifest, verify, re-pin — which is the
   component-update mechanism's job when it arrives.
3. **Installation**: unpack under `/opt/antigravity-cli` with the
   `antigravity` binary exposed on `PATH` (alias `agy`), per the
   contract's archive-over-package preference; the single-file tarball
   makes this trivial.
4. **State slot**: a checkout-scoped persistent slot mapping
   `~/.gemini/antigravity-cli`, in the pattern Claude Code established;
   credentials arrive per-checkout via the keyring/browser flow or a
   `GEMINI_API_KEY` host-environment binding, never by installation.
5. **Inspection**: selection, state location, and authorization state
   reported per the ledger's required outcomes.
