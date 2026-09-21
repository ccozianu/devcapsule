"""Distribution metadata from trusted component implementations, never downloaded code."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping, Protocol


@dataclass(frozen=True)
class ChannelNotice:
    """An explicit upstream notice affecting this exact version.

    The adapter owns applicability and classification. Generic code must not
    infer a vulnerability from version age, withdrawal, or free-form prose.
    Identity should change when the underlying advisory materially changes.
    """
    identity: str
    kind: Literal["security", "end-of-support"]
    detail: str


@dataclass(frozen=True)
class ChannelVersion:
    version: str
    status: str  # available, withdrawn, unsupported, or unknown
    detail: str = ""
    notices: tuple[ChannelNotice, ...] = ()


@dataclass(frozen=True)
class ChannelReport:
    source: str
    current: ChannelVersion
    candidates: tuple[ChannelVersion, ...]


@dataclass(frozen=True)
class ChannelSelection:
    """Exact replacement metadata and declared structural constraints.

    Requirements are exact companion versions. The caller refuses a mismatch
    and names it; it never upgrades an unrelated component implicitly.
    """
    metadata: Mapping[str, Any]
    platforms: tuple[str, ...]
    requires: tuple[tuple[str, str], ...] = ()
    base_families: tuple[str, ...] = ()
    status: str = "available"
    detail: str = ""


class DiscoveryChannel(Protocol):
    def check(self, current: str, platform: str) -> ChannelReport: ...


class DistributionChannel(DiscoveryChannel, Protocol):
    def select(self, version: str, platform: str) -> ChannelSelection: ...
