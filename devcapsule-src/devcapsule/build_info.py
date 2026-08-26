"""Embedded, inspectable source identity for a DevCapsule distribution."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from importlib.resources import files
import json
from pathlib import Path
import re
from typing import Any, Mapping
from zipfile import BadZipFile, ZipFile


class BuildInfoError(ValueError):
    """A distribution's embedded build information is absent or malformed."""


@dataclass(frozen=True)
class BuildInfo:
    schema_version: int
    version: str
    source_repository: str
    source_revision: str
    source_url: str
    build_mnemonic: str = "unknown"

    @classmethod
    def from_mapping(cls, value: object) -> BuildInfo:
        if not isinstance(value, dict):
            raise BuildInfoError("build information must be a JSON object")
        schema_version = value.get("schema_version")
        if schema_version not in {1, 2}:
            raise BuildInfoError(f"unsupported build-information schema: {schema_version!r}")
        build_mnemonic = (
            "unknown" if schema_version == 1 else _string(value, "build_mnemonic")
        )
        if build_mnemonic != "unknown" and re.fullmatch(
            r"(?:local-)?v[0-9][0-9A-Za-z._-]*", build_mnemonic
        ) is None:
            raise BuildInfoError(
                "build information 'build_mnemonic' must be a release tag such as "
                "'v0.2.7', a local label such as 'v0.2.7-local' or "
                "'v0.2.7-local-linux-x86_64', or a v026-era label such as "
                "'v026' or 'local-v026'"
            )
        return cls(
            schema_version=schema_version,
            version=_string(value, "version"),
            source_repository=_string(value, "source_repository"),
            source_revision=_string(value, "source_revision"),
            source_url=_string(value, "source_url"),
            build_mnemonic=build_mnemonic,
        )

    @classmethod
    def from_json(cls, value: str) -> BuildInfo:
        try:
            document = json.loads(value)
        except json.JSONDecodeError as exc:
            raise BuildInfoError(f"build information is not valid JSON: {exc.msg}") from exc
        return cls.from_mapping(document)

    @property
    def has_public_revision(self) -> bool:
        if re.fullmatch(r"[0-9a-f]{40,64}", self.source_revision) is None:
            return False
        if re.fullmatch(r"https://github\.com/[^/]+/[^/]+", self.source_repository) is None:
            return False
        return self.source_url == f"{self.source_repository}/commit/{self.source_revision}"

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)


def current_build_info() -> BuildInfo:
    resource = files("devcapsule").joinpath("_build_info.json")
    try:
        return BuildInfo.from_json(resource.read_text(encoding="utf-8"))
    except OSError as resource_error:
        # Some editable installers expose the project root as the package's
        # resource location even though imports resolve to this source tree.
        # The sibling path preserves source/PEX command parity without
        # weakening the packaged-resource validation.
        sibling = Path(__file__).with_name("_build_info.json")
        try:
            return BuildInfo.from_json(sibling.read_text(encoding="utf-8"))
        except OSError as sibling_error:
            raise BuildInfoError(
                f"cannot read embedded build information: {resource_error}; "
                f"source fallback failed: {sibling_error}"
            ) from sibling_error


def read_pex_build_info(path: str | Path) -> BuildInfo:
    """Read metadata from a PEX without executing the selected artifact."""

    selected = Path(path)
    try:
        with ZipFile(selected) as archive:
            candidates = [name for name in archive.namelist() if name.endswith("/devcapsule/_build_info.json")]
            if len(candidates) != 1:
                raise BuildInfoError(
                    f"PEX must contain exactly one devcapsule/_build_info.json; found {len(candidates)}"
                )
            return BuildInfo.from_json(archive.read(candidates[0]).decode("utf-8"))
    except (OSError, BadZipFile, UnicodeDecodeError) as exc:
        raise BuildInfoError(f"cannot read build information from PEX {selected}: {exc}") from exc


def build_info_json(info: BuildInfo) -> str:
    return json.dumps(info.to_mapping(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _string(value: Mapping[str, Any], key: str) -> str:
    selected = value.get(key)
    if not isinstance(selected, str) or not selected or "\x00" in selected:
        raise BuildInfoError(f"build information {key!r} must be a non-empty string")
    return selected
