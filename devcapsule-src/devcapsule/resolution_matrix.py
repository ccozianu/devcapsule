"""The resolution matrix: capability needs × platform → a verified formation.

The user expresses capability needs; this module looks up component versions
that satisfy those needs on a platform, constrained by what has been tested
(D-0007). Verification is a fact about a combination and does not expire:
the matrix accumulates **verified edges** — (component version, base
version, platform) with the evidence that verified them — plus **declared
couplings** for component pairs with an integration surface, which need
jointly verified version pairs. Components without a declared coupling
compose freely on a shared verified base (default orthogonality). New
releases append rows; removal is explicit retirement, never an implicit
effect of newer versions arriving.

Resolution selects the newest verified combination and is a pure offline
derivation: same need, same matrix ⇒ identical lock bytes. It needs no
network and never probes the container daemon, because the daemon is
exactly the capability that requires explicit authorization.

The generated lock follows the scoped-digest principle: it records a digest
of exactly the inputs it derives from — the normalized capability set — and
nothing more. The recorded ``resolution-matrix-version`` is informational
per ``R-COMPAT-001``: a newer client's matrix changes what would be
*generated next time*, never the validity of a lock that stands.

The public surface is deliberately minimal (Parnas): ``MATRICES`` keyed by
``Platform``, ``ResolutionMatrix`` with ``capabilities``/``normalize``/
``resolve``, the ``Formation`` a resolution returns, and
``ResolutionError``. Everything else — the capability taxonomy, the pins,
the selection policy, the evidence, the lock rendering — is this module's
secret.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from devcapsule.platforms import Platform
from devcapsule.project_configuration import (
    ProjectConfigurationError,
    canonical_digest,
    quote_toml,
    render_toml_scalar,
)

__all__ = [
    "MATRICES",
    "Formation",
    "ResolutionError",
    "ResolutionMatrix",
]


class ResolutionError(ProjectConfigurationError):
    """The need cannot be satisfied by any verified combination.

    The message is complete and displayable; callers show it verbatim.
    """


_MATRIX_VERSION = "embedded-12"


# --------------------------------------------------------------------------
# The internal model: pins carry their lock fragment verbatim (the literal
# stays visually diffable against the generated lock), the typed wrappers
# carry what resolution needs to know about them.


@dataclass(frozen=True)
class _BasePin:
    """One published base image and the capabilities it ships."""

    mnemonic: str
    # The compatibility generation this base belongs to. Verified edges key
    # on the substrate, not the mnemonic: what a smoke establishes is that a
    # component runs on this OS/toolchain surface, and our own base releases
    # on the same substrate (rebuilds varying only the embedded runtime PEX)
    # inherit that verification instead of each demanding a fresh smoke.
    # Ruled 2026-09-02 by the product owner (amending D-0007); bumping the
    # substrate string is the deliberate act reserved for substantial base
    # changes — a new OS release, a toolchain overhaul, or a runtime-plan
    # vocabulary the older generation cannot execute.
    substrate: str
    satisfies: frozenset[str]
    lock_table: Mapping[str, Any]


@dataclass(frozen=True)
class _VerifiedEdge:
    """A tested (component version, base substrate) pair, with its evidence.

    The evidence string names the concrete base the smoke ran on; the edge
    itself holds for every base pin sharing that substrate.
    """

    component_id: str
    component_version: str
    substrate: str
    evidence: str


@dataclass(frozen=True)
class _ComponentPin:
    """One component version and its lock fragment."""

    component_id: str
    version: str
    lock_table: Mapping[str, Any]


@dataclass(frozen=True)
class _Coupling:
    """Two components with an integration surface needing joint verification."""

    first_id: str
    second_id: str
    verified: frozenset[tuple[str, str]]
    evidence: str


@dataclass(frozen=True)
class Formation:
    """One resolved formation, ready to be committed as a lock.

    ``unverified`` is empty for a fully verified formation; otherwise it
    names the combinations the matrix has no evidence for — resolution
    proceeded past them at the caller's explicit request (owner ruling
    2026-09-03: the matrix may be stale or wrong, so a sophisticated user
    goes through with a gentle warning, not a brutal refusal).
    """

    capabilities: tuple[str, ...]
    provenance: str
    unverified: tuple[str, ...] = ()
    _document: Mapping[str, Any] = field(repr=False, default_factory=dict)
    _header: str = field(repr=False, default="")

    def render_lock(self) -> str:
        """The exact platform-lock bytes to write and commit."""

        return self._header + _render_document(self._document)


class ResolutionMatrix:
    """One platform's accumulated verified combinations.

    Clients know three operations: ``capabilities()`` (the askable
    vocabulary), ``normalize()`` (canonical, vocabulary-checked form of a
    need), and ``resolve()`` (a ``Formation`` or a ``ResolutionError``).
    """

    def __init__(
        self,
        *,
        platform: Platform,
        matrix_version: str,
        bases: tuple[_BasePin, ...],
        components: Mapping[str, tuple[_ComponentPin, ...]],
        edges: tuple[_VerifiedEdge, ...],
        couplings: tuple[_Coupling, ...],
        surface_capabilities: Mapping[str, str],
        ancillary_capabilities: Mapping[str, str],
        materialization: Mapping[str, Mapping[str, Any]],
    ) -> None:
        # Bases and per-component pins are append-only, newest last;
        # resolution prefers the newest verified combination.
        self._platform = platform
        self._matrix_version = matrix_version
        self._bases = bases
        self._components = components
        self._verified = {
            (edge.component_id, edge.component_version, edge.substrate): edge
            for edge in edges
        }
        self._couplings = couplings
        self._surface_capabilities = dict(surface_capabilities)
        self._ancillary_capabilities = dict(ancillary_capabilities)
        self._materialization = materialization

    def capabilities(self) -> tuple[str, ...]:
        """The complete capability vocabulary this matrix can resolve."""

        base_satisfied: set[str] = set()
        for base in self._bases:
            base_satisfied |= base.satisfies
        return tuple(
            sorted(
                base_satisfied
                | set(self._surface_capabilities)
                | set(self._ancillary_capabilities)
            )
        )

    def normalize(self, need: object) -> tuple[str, ...]:
        """Normalize a manifest ``capabilities.need`` value: sorted, unique, known."""

        if not isinstance(need, Sequence) or isinstance(need, (str, bytes)):
            raise ResolutionError("capabilities.need must be an array of capability names.")
        names: set[str] = set()
        for item in need:
            if not isinstance(item, str) or not item:
                raise ResolutionError(
                    "capabilities.need entries must be non-empty strings."
                )
            names.add(item)
        unknown = sorted(names - set(self.capabilities()))
        if unknown:
            raise ResolutionError(
                "The embedded resolution matrix does not know "
                + ", ".join(repr(name) for name in unknown)
                + "; supported capabilities: "
                + ", ".join(self.capabilities())
                + "."
            )
        return tuple(sorted(names))

    def resolve(self, need: object, *, allow_unverified: bool = False) -> Formation:
        """Derive one complete formation from a capability set, offline.

        Fully verified resolution is always tried first, so the escape hatch
        never degrades a need the matrix can satisfy.  Only when that fails
        and ``allow_unverified`` is set does resolution fall back to the base
        with the fewest unverified combinations (newest on ties), naming each
        one in the formation for the caller's gentle warning and the lock.
        """

        capabilities = self.normalize(need)
        surface_id = self._selected_surface(capabilities)
        required = [surface_id]
        for capability in capabilities:
            component_id = self._ancillary_capabilities.get(capability)
            if component_id is not None:
                required.append(component_id)
        base_needs = {
            capability
            for capability in capabilities
            if capability not in self._surface_capabilities
            and capability not in self._ancillary_capabilities
        }

        # Every base's failure is kept and reported newest-first: the newest
        # base's gap is usually the interesting one (often a single missing
        # edge), and a message naming only the oldest base's problem sent the
        # owner down the wrong path (2026-09-03 bug record).
        failures: list[str] = []
        for base in reversed(self._bases):
            missing_from_base = sorted(base_needs - base.satisfies)
            if missing_from_base:
                failures.append(
                    f"{base.mnemonic}: does not ship " + ", ".join(missing_from_base)
                )
                continue
            chosen, failure = self._verified_selection(required, base)
            if chosen is None:
                failures.append(f"{base.mnemonic}: {failure}")
                continue
            return self._formation(capabilities, surface_id, base, chosen)
        if allow_unverified:
            fallback = self._unverified_selection(required, base_needs)
            if fallback is not None:
                base, chosen, unverified = fallback
                return self._formation(
                    capabilities, surface_id, base, chosen, unverified=unverified
                )
        # Every refusal names --unverified (owner ruling 2026-09-05):
        # adopters must be able to try new components and bases ahead of the
        # matrix and report back. Base capabilities stay hard constraints —
        # the wording says what the flag does and does not bypass.
        if allow_unverified:
            remedy = (
                "--unverified cannot help here: a base that does not ship a "
                "needed toolchain is a hard refusal."
            )
        else:
            remedy = (
                "Pass --unverified to resolve past missing verification with "
                "a gentle warning; the generated lock names every unverified "
                "combination. A base that does not ship a needed toolchain "
                "remains a hard refusal."
            )
        raise ResolutionError(
            "No verified combination satisfies "
            + ", ".join(capabilities)
            + f" on {self._platform}:\n  "
            + "\n  ".join(failures)
            + "\n"
            + remedy
        )

    def _selected_surface(self, capabilities: tuple[str, ...]) -> str:
        interactive = sorted(set(capabilities) & set(self._surface_capabilities))
        if not interactive:
            choices = ", ".join(sorted(self._surface_capabilities))
            raise ResolutionError(
                "The V1 environment needs an interactive-surface capability to select "
                f"its surface; add exactly one of {choices} to capabilities.need."
            )
        if len(interactive) > 1:
            raise ResolutionError(
                "A V1 platform lock holds exactly one interactive surface, but "
                f"capabilities.need selects {', '.join(interactive)}; keep exactly one."
            )
        return self._surface_capabilities[interactive[0]]

    def _verified_selection(
        self, required: list[str], base: _BasePin
    ) -> tuple[dict[str, _ComponentPin] | None, str]:
        """The newest verified pin of every required component on this base."""

        chosen: dict[str, _ComponentPin] = {}
        for component_id in required:
            pin = next(
                (
                    candidate
                    for candidate in reversed(self._components[component_id])
                    if (component_id, candidate.version, base.substrate) in self._verified
                ),
                None,
            )
            if pin is None:
                return None, (
                    f"no verified {component_id} version against base {base.mnemonic} "
                    f"(substrate {base.substrate})"
                )
            chosen[component_id] = pin
        for coupling in self._couplings:
            if coupling.first_id in chosen and coupling.second_id in chosen:
                pair = (
                    chosen[coupling.first_id].version,
                    chosen[coupling.second_id].version,
                )
                if pair not in coupling.verified:
                    return None, (
                        f"{coupling.first_id} {pair[0]} and {coupling.second_id} "
                        f"{pair[1]} have no jointly verified integration"
                    )
        return chosen, ""

    def _unverified_selection(
        self, required: list[str], base_needs: set[str]
    ) -> tuple[_BasePin, dict[str, _ComponentPin], tuple[str, ...]] | None:
        """The capability-satisfying base with the fewest unverified pairs.

        Base capabilities stay a hard constraint — a base that does not ship
        a needed toolchain cannot be forced.  Verification is the only rule
        relaxed: components keep their newest verified pin where one exists
        on the base's substrate and fall back to their newest pin otherwise,
        with every such fallback (and every unverified coupling) named.
        """

        best: tuple[_BasePin, dict[str, _ComponentPin], tuple[str, ...]] | None = None
        for base in reversed(self._bases):
            if base_needs - base.satisfies:
                continue
            chosen: dict[str, _ComponentPin] = {}
            unverified: list[str] = []
            for component_id in required:
                pins = self._components[component_id]
                verified_pin = next(
                    (
                        candidate
                        for candidate in reversed(pins)
                        if (component_id, candidate.version, base.substrate)
                        in self._verified
                    ),
                    None,
                )
                if verified_pin is not None:
                    chosen[component_id] = verified_pin
                    continue
                newest = pins[-1]
                chosen[component_id] = newest
                unverified.append(
                    f"{component_id} {newest.version} on base {base.mnemonic} "
                    f"(substrate {base.substrate})"
                )
            for coupling in self._couplings:
                if coupling.first_id in chosen and coupling.second_id in chosen:
                    pair = (
                        chosen[coupling.first_id].version,
                        chosen[coupling.second_id].version,
                    )
                    if pair not in coupling.verified:
                        unverified.append(
                            f"{coupling.first_id} {pair[0]} with "
                            f"{coupling.second_id} {pair[1]} (no jointly "
                            "verified integration)"
                        )
            if best is None or len(unverified) < len(best[2]):
                best = (base, chosen, tuple(unverified))
        return best

    def _formation(
        self,
        capabilities: tuple[str, ...],
        surface_id: str,
        base: _BasePin,
        chosen: Mapping[str, _ComponentPin],
        unverified: tuple[str, ...] = (),
    ) -> Formation:
        components: dict[str, Any] = {
            "interactive-surface": surface_id,
            surface_id: dict(chosen[surface_id].lock_table),
        }
        for capability in capabilities:
            component_id = self._ancillary_capabilities.get(capability)
            if component_id is not None:
                components[component_id] = dict(chosen[component_id].lock_table)
        document: dict[str, Any] = {
            "devcapsule-lock-format-version": 1,
            "resolution-matrix-version": self._matrix_version,
            "platform": self._platform.value,
            # The scoped digest: the one derivation input beside the platform,
            # which the filename already carries.
            "capabilities-digest": canonical_digest({"need": list(capabilities)}),
            "base": dict(base.lock_table),
            "components": components,
            "materialization": dict(self._materialization[surface_id]),
        }
        header = (
            "# Generated by 'devcapsule project init' from the embedded resolution "
            f"matrix {self._matrix_version}.\n"
            "# Commit this file: it pins the exact environment collaborators receive.\n"
        )
        provenance = (
            f"embedded resolution matrix {self._matrix_version}: "
            f"{surface_id} {chosen[surface_id].version} on base {base.mnemonic}"
        )
        if unverified:
            # The lock shape is scalars and tables, so the list travels as one
            # scalar; collaborators regenerating the lock see the same warning.
            document["unverified-combinations"] = "; ".join(unverified)
            header += (
                "# WARNING: generated past the verified matrix at the owner's "
                "request; see unverified-combinations.\n"
            )
            provenance += f" (unverified: {'; '.join(unverified)})"
        return Formation(
            capabilities=capabilities,
            provenance=provenance,
            unverified=unverified,
            _document=document,
            _header=header,
        )


# --------------------------------------------------------------------------
# The verified data. Pins below are lock fragments verbatim; edges record
# what verified each (component version, base version) pair; advancing the
# generated formation advances _MATRIX_VERSION.

# Substrate generations (owner ruling 2026-09-02, amending D-0007): edges
# verify component-on-substrate, so base releases sharing a substrate share
# edges. The gen1→gen2 boundary is the runtime-plan vocabulary: gen2 bases
# embed a runtime that executes vscode-adapter plans, which gen1 predates.
_SUBSTRATE_GEN1 = "ubuntu-24.04-gen1"
_SUBSTRATE_GEN2 = "ubuntu-24.04-gen2"

_V026_BASE = _BasePin(
    mnemonic="v026",
    substrate=_SUBSTRATE_GEN1,
    # Recipe version 4 ships CPython, the Docker CLI suite, Node.js, and the
    # Temurin JDK plus Maven; these capabilities are therefore satisfied by
    # the base and never a lock entry.
    satisfies=frozenset({"python", "docker-cli", "node", "java", "maven"}),
    lock_table={
        "reference": (
            "docker.io/mycodespaceai/devcapsule-base"
            "@sha256:695f9eb6dd269dc694b3367f6a2570d500b938998d6f7aa3aa00e5d04cc7394a"
        ),
        "build-mnemonic": "v026",
    },
)

# The v0.2.8 base (recipe version 5, same shipped toolchain) embeds a runtime
# PEX that understands the vscode adapter, which v026 predates — the gen2
# substrate; later gen2 releases inherit its verified edges.
_V0_2_8_BASE = _BasePin(
    mnemonic="v0.2.8",
    substrate=_SUBSTRATE_GEN2,
    satisfies=frozenset({"python", "docker-cli", "node", "java", "maven"}),
    lock_table={
        "reference": (
            "docker.io/mycodespaceai/devcapsule-base"
            "@sha256:8be27a7773bdb58e8d4d2f05283752736d12c2062e4c566d33d7f2e71ef336db"
        ),
        "build-mnemonic": "v0.2.8",
    },
)

# The v0.2.9 base is a gen2 rebuild (recipe version 5, same toolchain)
# embedding the 0.2.9 runtime; it inherits gen2's verified edges per the
# 2026-09-02 substrate ruling. Pushed by the owner 2026-09-02; digest read
# from the registry at pinning time.
_V0_2_9_BASE = _BasePin(
    mnemonic="v0.2.9",
    substrate=_SUBSTRATE_GEN2,
    satisfies=frozenset({"python", "docker-cli", "node", "java", "maven"}),
    lock_table={
        "reference": (
            "docker.io/mycodespaceai/devcapsule-base"
            "@sha256:ca9f79619fc0709a13e6a66de8959cda55dd47c23ec073fe0eb353de32734232"
        ),
        "build-mnemonic": "v0.2.9",
    },
)

_PYCHARM_2026_2_0_1 = _ComponentPin(
    component_id="pycharm",
    version="2026.2.0.1",
    lock_table={
        "version": "2026.2.0.1",
        "variant": "professional",
        "delivery-policy": "local-materialization",
        "url": "https://download.jetbrains.com/python/pycharm-2026.2.0.1.tar.gz",
        "sha256": "4a37cb2d15703553c61e814d8e014bfa47308508470de5f968c4e9645b771675",
    },
)

# VSCodium 1.126.04524 is the latest published release as of 2026-08-31; the
# checksum was recomputed locally from the downloaded archive and matches the
# published .sha256 asset. MIT-licensed free/libre binaries, so caching them
# in local environment images needs no per-developer acquisition terms.
_CODIUM_1_126_04524 = _ComponentPin(
    component_id="codium",
    version="1.126.04524",
    lock_table={
        "version": "1.126.04524",
        "delivery-policy": "local-materialization",
        "license": "MIT",
        "url": (
            "https://github.com/VSCodium/vscodium/releases/download/"
            "1.126.04524/VSCodium-linux-x64-1.126.04524.tar.gz"
        ),
        "sha256": "adf3548df055d18e476cdee887488ba7486b879ad99a31a546c6b5c5ff296c24",
    },
)

_CODEX_0_145_0 = _ComponentPin(
    component_id="codex",
    version="0.145.0",
    lock_table={
        "version": "0.145.0",
        "delivery-policy": "local-materialization",
        "license": "Apache-2.0",
        "artifacts": {
            "linux-amd64": {
                "url": (
                    "https://registry.npmjs.org/@openai/codex/-/"
                    "codex-0.145.0-linux-x64.tgz"
                ),
                "sha256": (
                    "11239480f8e3efd1430f23bbe91c1a397856b8bbe6185ccbaee2382d25e03df2"
                ),
                "archive-member": (
                    "package/vendor/x86_64-unknown-linux-musl/bin/codex"
                ),
            }
        },
    },
)

# 0.153.0 advances the pin at the owner's direction 2026-09-03 (the CLI's
# own update notice during the demo-project conversions). The tarball's
# sha512 was verified against the npm registry integrity and the sha256
# computed locally from the same download; the archive member set is
# unchanged since 0.145.0 and the extracted binary was executed hands-on
# (`codex-cli 0.153.0`). The former integration/acp-version metadata is
# gone with the coupling removal (see the couplings note below): codex is
# a standalone CLI component, and locks no longer advertise a
# jetbrains-ai-assistant integration DevCapsule does not deliver.
_CODEX_0_153_0 = _ComponentPin(
    component_id="codex",
    version="0.153.0",
    lock_table={
        "version": "0.153.0",
        "delivery-policy": "local-materialization",
        "license": "Apache-2.0",
        "artifacts": {
            "linux-amd64": {
                "url": (
                    "https://registry.npmjs.org/@openai/codex/-/"
                    "codex-0.153.0-linux-x64.tgz"
                ),
                "sha256": (
                    "856f408ea61b44a381b7d6fb7c82365dfcef649ae2a340fc01282cf63c30cd8a"
                ),
                "archive-member": (
                    "package/vendor/x86_64-unknown-linux-musl/bin/codex"
                ),
            }
        },
    },
)

_CLAUDE_CODE_2_1_227 = _ComponentPin(
    component_id="claude-code",
    version="2.1.227",
    lock_table={
        "version": "2.1.227",
        "delivery-policy": "local-materialization",
        "acquisition-authorization": "claude-code-download",
        "license": "Proprietary",
        "terms-url": "https://www.anthropic.com/legal/commercial-terms",
        "distribution": "user-acquired-not-redistributed",
        "artifacts": {
            "linux-amd64": {
                "url": (
                    "https://downloads.claude.ai/claude-code-releases/"
                    "2.1.227/linux-x64/claude"
                ),
                "sha256": (
                    "6832dc3f1797b890b71116e5f2dbbf9a83fd3d0498c235b4b0f9cd0e6e499ad6"
                ),
            }
        },
    },
)

# 2.1.236 is the stable channel as of 2026-09-03 (the Fable 5.1 release the
# owner directed the update for). The sha256 was computed locally from the
# downloaded binary the same day and matches the vendor manifest's linux-x64
# checksum; the binary was executed hands-on ("2.1.236 (Claude Code)").
_CLAUDE_CODE_2_1_236 = _ComponentPin(
    component_id="claude-code",
    version="2.1.236",
    lock_table={
        "version": "2.1.236",
        "delivery-policy": "local-materialization",
        "acquisition-authorization": "claude-code-download",
        "license": "Proprietary",
        "terms-url": "https://www.anthropic.com/legal/commercial-terms",
        "distribution": "user-acquired-not-redistributed",
        "artifacts": {
            "linux-amd64": {
                "url": (
                    "https://downloads.claude.ai/claude-code-releases/"
                    "2.1.236/linux-x64/claude"
                ),
                "sha256": (
                    "6c8818fa22187aa555c242be4abbacc44d6b71a32ac9631ee7b2b5d12f51f752"
                ),
            }
        },
    },
)

# 2.1.261 advances the pin at the owner's direction 2026-09-04 (the vendor's
# latest, built the same day). The linux-x64 binary's sha256 and size match
# the vendor manifest, and the binary was executed hands-on
# ("2.1.261 (Claude Code)").
_CLAUDE_CODE_2_1_261 = _ComponentPin(
    component_id="claude-code",
    version="2.1.261",
    lock_table={
        "version": "2.1.261",
        "delivery-policy": "local-materialization",
        "acquisition-authorization": "claude-code-download",
        "license": "Proprietary",
        "terms-url": "https://www.anthropic.com/legal/commercial-terms",
        "distribution": "user-acquired-not-redistributed",
        "artifacts": {
            "linux-amd64": {
                "url": (
                    "https://downloads.claude.ai/claude-code-releases/"
                    "2.1.261/linux-x64/claude"
                ),
                "sha256": (
                    "4ae40dd1784e85753e742e09f267d29ecbb82890361ad3817d27560866d364a6"
                ),
            }
        },
    },
)

# The official Antigravity channel serves latest-only, but the artifacts are
# versioned and immutable in GCS; this pin is a deliberate curation. The
# sha256 was computed locally from the downloaded archive (2026-09-02, and
# re-verified with the archive member name on the same date); upstream-sha512
# is the checksum the vendor manifest published for the same bytes, recorded
# as provenance. See the workstream's license and redistribution analysis.
_ANTIGRAVITY_CLI_1_1_24 = _ComponentPin(
    component_id="antigravity-cli",
    version="1.1.24",
    lock_table={
        "version": "1.1.24",
        "delivery-policy": "local-materialization",
        "acquisition-authorization": "antigravity-download",
        "license": "Proprietary",
        "terms-url": "https://antigravity.google/terms/",
        "distribution": "user-acquired-not-redistributed",
        "artifacts": {
            "linux-amd64": {
                "url": (
                    "https://storage.googleapis.com/antigravity-public/"
                    "antigravity-cli/1.1.24-6130423206641664/linux-x64/"
                    "cli_linux_x64.tar.gz"
                ),
                "sha256": (
                    "cff1fb7ed735da72c35658645a4f916cf74f020d4cd30ab95ebe8c2a49a4d569"
                ),
                "archive-member": "antigravity",
                "upstream-sha512": (
                    "ed4df91ea7ced986aa14507a0ab8225d92985190f7d551010eba0c46c569587e"
                    "602cb36af81c9cde7af0d6b380e8dd3a82131361806cd96012d44a3e47fb369a"
                ),
            }
        },
    },
)

_POSTGRESQL_CLIENT_16 = _ComponentPin(
    component_id="postgresql-client",
    version="16",
    lock_table={
        "version": "16",
        "delivery-policy": "base-image",
        "license": "PostgreSQL",
    },
)

_DOGFOOD_E2E = "recursive dogfood E2E (embedded-2 formation)"

_LINUX_AMD64_MATRIX = ResolutionMatrix(
    platform=Platform.LINUX_AMD64,
    matrix_version=_MATRIX_VERSION,
    bases=(_V026_BASE, _V0_2_8_BASE, _V0_2_9_BASE),
    components={
        "pycharm": (_PYCHARM_2026_2_0_1,),
        "codium": (_CODIUM_1_126_04524,),
        "codex": (_CODEX_0_145_0, _CODEX_0_153_0),
        "claude-code": (
            _CLAUDE_CODE_2_1_227,
            _CLAUDE_CODE_2_1_236,
            _CLAUDE_CODE_2_1_261,
        ),
        "antigravity-cli": (_ANTIGRAVITY_CLI_1_1_24,),
        "postgresql-client": (_POSTGRESQL_CLIENT_16,),
    },
    edges=(
        _VerifiedEdge("pycharm", "2026.2.0.1", _SUBSTRATE_GEN1, _DOGFOOD_E2E),
        _VerifiedEdge(
            "codium",
            "1.126.04524",
            _SUBSTRATE_GEN1,
            "product-owner live smoke 2026-08-31 (current-tree runtime PEX override)",
        ),
        _VerifiedEdge(
            "codium",
            "1.126.04524",
            _SUBSTRATE_GEN2,
            "product-owner smoke 2026-09-02: tictactoe sample on the v0.2.8 "
            "base (config-history 20260902T075529Z)",
        ),
        _VerifiedEdge("codex", "0.145.0", _SUBSTRATE_GEN1, _DOGFOOD_E2E),
        _VerifiedEdge(
            "codex",
            "0.145.0",
            _SUBSTRATE_GEN2,
            "product-owner smoke 2026-09-03: five-way formation (codium x "
            "antigravity x claude-code x codex) on the v0.2.9 base",
        ),
        # 0.153.0 advances the pin at the owner's direction 2026-09-03; both
        # substrate edges are provisional pending the next dogfood run (gen1)
        # and the demo-project spins (gen2), per the provisional-edge
        # precedent.
        _VerifiedEdge(
            "codex",
            "0.153.0",
            _SUBSTRATE_GEN1,
            "provisional: owner-directed CLI update 2026-09-03, pending the "
            "next dogfood run",
        ),
        _VerifiedEdge(
            "codex",
            "0.153.0",
            _SUBSTRATE_GEN2,
            "provisional: owner-directed CLI update 2026-09-03, pending the "
            "demo-project three-provider spins",
        ),
        _VerifiedEdge("claude-code", "2.1.227", _SUBSTRATE_GEN1, _DOGFOOD_E2E),
        _VerifiedEdge(
            "claude-code",
            "2.1.227",
            _SUBSTRATE_GEN2,
            "product-owner smoke 2026-09-03: five-way formation (codium x "
            "antigravity x claude-code x codex) on the v0.2.9 base",
        ),
        # 2.1.236 advances the pin at the owner's direction 2026-09-03 (the
        # Fable 5.1 update for us and adopters); both substrate edges are
        # provisional pending the next dogfood run (gen1) and codium smoke
        # (gen2), per the provisional-edge precedent.
        _VerifiedEdge(
            "claude-code",
            "2.1.236",
            _SUBSTRATE_GEN1,
            "provisional: owner-directed CLI update 2026-09-03, pending the "
            "next dogfood run",
        ),
        _VerifiedEdge(
            "claude-code",
            "2.1.236",
            _SUBSTRATE_GEN2,
            "provisional: owner-directed CLI update 2026-09-03, pending the "
            "next codium-formation smoke",
        ),
        # 2.1.261 advances the pin at the owner's direction 2026-09-04; both
        # substrate edges are provisional pending the next dogfood run (gen1)
        # and the demo-project spins (gen2), per the provisional-edge
        # precedent.
        _VerifiedEdge(
            "claude-code",
            "2.1.261",
            _SUBSTRATE_GEN1,
            "provisional: owner-directed CLI update 2026-09-04, pending the "
            "next dogfood run",
        ),
        _VerifiedEdge(
            "claude-code",
            "2.1.261",
            _SUBSTRATE_GEN2,
            "provisional: owner-directed CLI update 2026-09-04, pending the "
            "demo-project three-provider spins",
        ),
        _VerifiedEdge("postgresql-client", "16", _SUBSTRATE_GEN1, _DOGFOOD_E2E),
        _VerifiedEdge(
            "antigravity-cli",
            "1.1.24",
            _SUBSTRATE_GEN2,
            "product-owner smoke 2026-09-02: antigravity working the "
            "tictactoe sample (codium surface, v0.2.8 base)",
        ),
    ),
    # The codex x pycharm coupling is removed until further notice
    # (product-owner ruling 2026-09-03): the jetbrains-ai-assistant
    # integration it stood for is not a delivery we want — the IDE's AI
    # plugin installs its own codex copy and routes usage through the
    # developer's JetBrains-account quota on JetBrains backends, ignoring
    # the logged-in codex already on PATH. DevCapsule ships codex as a
    # standalone CLI component only; the coupling mechanism stays for
    # future jointly-verified integrations.
    couplings=(),
    # Each interactive capability selects exactly one surface component. A V1
    # platform lock holds exactly one interactive surface, so a capability set
    # must name exactly one of these: none has nothing to run, and two would
    # ask one lock to carry two surfaces.
    surface_capabilities={
        "python-ide": "pycharm",
        "frontend-ide": "codium",
    },
    # Ancillary capabilities select additive components; the value is the
    # component id the lock records.
    ancillary_capabilities={
        "codex-agent": "codex",
        "claude-code-agent": "claude-code",
        "antigravity-agent": "antigravity-cli",
        "postgresql-client": "postgresql-client",
    },
    # The materialization recipe follows the selected surface: each surface
    # family unpacks and fixes up its installation differently.
    materialization={
        "pycharm": {
            "recipe": "jetbrains-local-materialization",
            "recipe-version": "1",
        },
        "codium": {
            "recipe": "vscode-local-materialization",
            # Version 2: the chrome-sandbox 4755 step is removed — renderers
            # run --no-sandbox (product-owner ruling 2026-09-02; see the
            # renderer-sandboxing design note).
            "recipe-version": "2",
        },
    },
)

# The map is the platform authority: its keys are the supported platforms,
# total over the Platform enum (D-0006/D-0007). Clients index it with a key
# from Platform.current() or Platform.parse(), never one built from parts.
MATRICES: Mapping[Platform, ResolutionMatrix] = MappingProxyType(
    {
        Platform.LINUX_AMD64: _LINUX_AMD64_MATRIX,
    }
)


# --------------------------------------------------------------------------
# Lock rendering (private): the restricted lock shape — string/int/bool
# scalars and nested tables. Insertion order is preserved so the generated
# file reads in the conventional lock order; generation is deterministic
# because every input table above is built deterministically.


def _render_document(document: Mapping[str, Any]) -> str:
    lines: list[str] = []
    _render_table(None, document, lines)
    return "\n".join(lines) + "\n"


def _render_table(prefix: str | None, table: Mapping[str, Any], lines: list[str]) -> None:
    scalars = {key: value for key, value in table.items() if not isinstance(value, Mapping)}
    subtables = {key: value for key, value in table.items() if isinstance(value, Mapping)}
    if prefix is not None:
        if lines:
            lines.append("")
        lines.append(f"[{prefix}]")
    for key, value in scalars.items():
        if not isinstance(value, (str, int, bool)):
            raise ProjectConfigurationError(
                f"Unsupported lock value type for {key!r}: {type(value).__name__}."
            )
        rendered_key = key if _is_bare_key(key) else quote_toml(key)
        lines.append(f"{rendered_key} = {render_toml_scalar(value)}")
    for key, value in subtables.items():
        component = key if _is_bare_key(key) else quote_toml(key)
        _render_table(component if prefix is None else f"{prefix}.{component}", value, lines)


def _is_bare_key(key: str) -> bool:
    return all(character.isalnum() or character in "-_" for character in key)
