"""The embedded resolution matrix: capability set + platform → platform lock.

*Offline And The Embedded Matrix* (see
``engineering-docs/design-notes/devcapsule/v1-user-experience.md``): the
client ships a minimal embedded matrix with base digests pinned, so ``init``
resolves entirely from local data — a pure file-producing derivation that
needs no network and never probes the container daemon, because the daemon is
exactly the capability that requires explicit authorization.

The generated lock follows the scoped-digest principle: it records a digest
of exactly the inputs it derives from — the normalized capability set — and
nothing more.  The retired whole-manifest digest is deliberately not written;
no other manifest field may affect a lock's validity, and ``lock_for``
already refuses to read it.  The recorded ``resolution-matrix-version`` is
informational per ``R-COMPAT-001``: a newer client's matrix changes what
would be *generated next time*, never the validity of a lock that stands.

The pins below are the proven current formation: the published v026 base at
its immutable registry digest, and the exact component artifact set validated
by the recursive dogfood E2E.  Advancing any pin advances
``MATRIX_VERSION``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from devcapsule.project_configuration import (
    ProjectConfigurationError,
    canonical_digest,
    quote_toml,
    render_toml_scalar,
)

__all__ = [
    "BASE_SATISFIED_CAPABILITIES",
    "GeneratedLock",
    "INTERACTIVE_CAPABILITY",
    "MATRIX_VERSION",
    "SUPPORTED_PLATFORMS",
    "generate_platform_lock",
    "normalize_capability_need",
    "supported_capabilities",
]


MATRIX_VERSION = "embedded-1"

SUPPORTED_PLATFORMS = ("linux-amd64",)

# Satisfied by every pinned base image and therefore never a lock entry:
# recipe version 4 ships CPython, the Docker CLI suite, Node.js, and the
# Temurin JDK plus Maven.
BASE_SATISFIED_CAPABILITIES = frozenset(
    {"python", "docker-cli", "node", "java", "maven"}
)

# The V1 curated slice has exactly one interactive surface; a capability set
# without it has nothing to run and fails with that explanation rather than
# generating an unrunnable lock.
INTERACTIVE_CAPABILITY = "python-ide"

_BASE_TABLE: dict[str, Any] = {
    "reference": (
        "docker.io/mycodespaceai/devcapsule-base"
        "@sha256:695f9eb6dd269dc694b3367f6a2570d500b938998d6f7aa3aa00e5d04cc7394a"
    ),
    "build-mnemonic": "v026",
}

_PYCHARM_TABLE: dict[str, Any] = {
    "version": "2026.2.0.1",
    "variant": "professional",
    "delivery-policy": "local-materialization",
    "url": "https://download.jetbrains.com/python/pycharm-2026.2.0.1.tar.gz",
    "sha256": "4a37cb2d15703553c61e814d8e014bfa47308508470de5f968c4e9645b771675",
}

# Ancillary component tables keyed by the capability that selects them; the
# inner key is the component id the lock records.
_ANCILLARY_COMPONENT_TABLES: dict[str, tuple[str, dict[str, Any]]] = {
    "codex-agent": (
        "codex",
        {
            "version": "0.145.0",
            "delivery-policy": "local-materialization",
            "integration": "jetbrains-ai-assistant",
            "acp-version": "1.1.9",
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
    ),
    "claude-code-agent": (
        "claude-code",
        {
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
    ),
    "postgresql-client": (
        "postgresql-client",
        {
            "version": "16",
            "delivery-policy": "base-image",
            "license": "PostgreSQL",
        },
    ),
}

_MATERIALIZATION_TABLE: dict[str, Any] = {
    "recipe": "jetbrains-local-materialization",
    "recipe-version": "1",
}


@dataclass(frozen=True)
class GeneratedLock:
    """One derived platform lock, rendered and ready to be written."""

    platform: str
    matrix_version: str
    capabilities: tuple[str, ...]
    content: str


def supported_capabilities() -> tuple[str, ...]:
    """The complete capability vocabulary this matrix can resolve."""

    return tuple(
        sorted(
            BASE_SATISFIED_CAPABILITIES
            | {INTERACTIVE_CAPABILITY}
            | set(_ANCILLARY_COMPONENT_TABLES)
        )
    )


def normalize_capability_need(need: object) -> tuple[str, ...]:
    """Normalize a manifest ``capabilities.need`` value: sorted, unique, known."""

    if not isinstance(need, Sequence) or isinstance(need, (str, bytes)):
        raise ProjectConfigurationError("capabilities.need must be an array of capability names.")
    names: set[str] = set()
    for item in need:
        if not isinstance(item, str) or not item:
            raise ProjectConfigurationError(
                "capabilities.need entries must be non-empty strings."
            )
        names.add(item)
    unknown = sorted(names - set(supported_capabilities()))
    if unknown:
        raise ProjectConfigurationError(
            "The embedded resolution matrix does not know "
            + ", ".join(repr(name) for name in unknown)
            + "; supported capabilities: "
            + ", ".join(supported_capabilities())
            + "."
        )
    return tuple(sorted(names))


def generate_platform_lock(need: object, platform: str) -> GeneratedLock:
    """Derive one complete platform lock from a capability set, offline."""

    capabilities = normalize_capability_need(need)
    if platform not in SUPPORTED_PLATFORMS:
        supported = ", ".join(SUPPORTED_PLATFORMS)
        raise ProjectConfigurationError(
            f"The embedded resolution matrix has no entry for platform {platform!r}; "
            f"supported platforms: {supported}. A lock for another platform is authored "
            "on that platform."
        )
    if INTERACTIVE_CAPABILITY not in capabilities:
        raise ProjectConfigurationError(
            f"The V1 environment needs the {INTERACTIVE_CAPABILITY!r} capability to select "
            "its interactive surface; add it to capabilities.need."
        )

    components: dict[str, Any] = {
        "interactive-surface": "pycharm",
        "pycharm": dict(_PYCHARM_TABLE),
    }
    for capability in capabilities:
        selected = _ANCILLARY_COMPONENT_TABLES.get(capability)
        if selected is not None:
            component_id, table = selected
            components[component_id] = table

    document: dict[str, Any] = {
        "devcapsule-lock-format-version": 1,
        "resolution-matrix-version": MATRIX_VERSION,
        "platform": platform,
        # The scoped digest: the one derivation input beside the platform,
        # which the filename already carries.
        "capabilities-digest": canonical_digest({"need": list(capabilities)}),
        "base": _BASE_TABLE,
        "components": components,
        "materialization": _MATERIALIZATION_TABLE,
    }
    header = (
        "# Generated by 'devcapsule project init' from the embedded resolution "
        f"matrix {MATRIX_VERSION}.\n"
        "# Commit this file: it pins the exact environment collaborators receive.\n"
    )
    return GeneratedLock(
        platform=platform,
        matrix_version=MATRIX_VERSION,
        capabilities=capabilities,
        content=header + _render_document(document),
    )


def _render_document(document: Mapping[str, Any]) -> str:
    """Render the restricted lock shape (string/int/bool scalars, nested tables).

    Insertion order is preserved so the generated file reads in the
    conventional lock order; generation is deterministic because every input
    table is built deterministically above.
    """

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
