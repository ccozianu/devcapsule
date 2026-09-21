"""Read-only vendor signals. These are maintained adapters, not vendor promises.

No installer is executed and no executable payload is acquired here. A release
pointer establishes availability, never the support/security state of old builds.
"""
from __future__ import annotations

from datetime import date
import json
from typing import Any
from urllib.request import Request, urlopen

from devcapsule.compat import CliError
from devcapsule.components.channels import ChannelNotice, ChannelReport, ChannelVersion


def read_metadata(url: str, *, limit: int = 2 * 1024 * 1024) -> bytes:
    with urlopen(Request(url, headers={"User-Agent": "DevCapsule-update-check"}), timeout=8) as response:
        payload = response.read(limit + 1)
    if len(payload) > limit:
        raise ValueError("metadata size limit exceeded")
    return payload


def read_json(url: str) -> Any:
    return json.loads(read_metadata(url))


def exact_version(value: Any) -> str:
    if not isinstance(value, str) or not 1 < len(value) < 80:
        raise ValueError("expected a dotted release version")
    parts = value.split(".")
    if len(parts) < 2 or any(not part or not part.isascii() or not part.isdigit() for part in parts):
        raise ValueError("expected a dotted release version")
    return value


def _available(source: str, current: str, latest: Any, detail: str = "") -> ChannelReport:
    latest = exact_version(latest)
    current_parts = tuple(map(int, exact_version(current).split(".")))
    latest_parts = tuple(map(int, latest.split(".")))
    return ChannelReport(source, ChannelVersion(current, "available" if latest == current else "unknown",
                         "This release feed does not assess installed-version support."),
                         (ChannelVersion(latest, "available", detail),) if latest_parts > current_parts else ())


class VendorDiscovery:
    source: str

    def check(self, current: str, platform: str) -> ChannelReport:
        if platform not in {"linux-amd64", "linux-arm64"}:
            raise CliError(f"No discovery adapter for {platform}.")
        try:
            return self._check(current, platform)
        except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as exc:
            raise CliError(f"Vendor discovery unavailable at {self.source}: {exc}") from exc

    def _check(self, current: str, platform: str) -> ChannelReport:
        raise NotImplementedError


class JetBrainsDiscovery(VendorDiscovery):
    source = "https://data.services.jetbrains.com/products/releases?code=PY&latest=true&type=release"

    def _check(self, current: str, platform: str) -> ChannelReport:
        document = read_json(self.source)
        # PY currently maps to PCP; admit the two observed product keys explicitly.
        releases = document.get("PCP", document.get("PY"))
        if not isinstance(releases, list) or len(releases) != 1 or releases[0]["type"] != "release":
            raise ValueError("expected one PyCharm release")
        release = releases[0]
        artifact = release["downloads"]["linux" if platform == "linux-amd64" else "linuxARM64"]
        if not artifact.get("link") or not artifact.get("checksumLink"):
            raise ValueError("platform download/checksum missing")
        return _available(self.source, current, release["version"])


class CodiumDiscovery(VendorDiscovery):
    source = "https://api.github.com/repos/VSCodium/vscodium/releases/latest"

    def _check(self, current: str, platform: str) -> ChannelReport:
        release = read_json(self.source)
        if release["prerelease"] is not False or release["draft"] is not False:
            raise ValueError("expected a published stable release")
        latest = exact_version(release["tag_name"])
        arch = "x64" if platform == "linux-amd64" else "arm64"
        name = f"VSCodium-linux-{arch}-{latest}.tar.gz"
        if not any(asset.get("name") == name for asset in release["assets"]):
            raise ValueError("platform archive missing")
        return _available(self.source, current, latest)


class ClaudeDiscovery(VendorDiscovery):
    source = "https://downloads.claude.ai/claude-code-releases/latest"

    def _check(self, current: str, platform: str) -> ChannelReport:
        latest = exact_version(read_metadata(self.source, limit=128).decode().strip())
        manifest = read_json(f"https://downloads.claude.ai/claude-code-releases/{latest}/manifest.json")
        arch = "linux-x64" if platform == "linux-amd64" else "linux-arm64"
        if manifest["version"] != latest or not manifest["platforms"][arch].get("checksum"):
            raise ValueError("version/platform manifest mismatch")
        return _available(self.source, current, latest, "Vendor latest channel")


class AntigravityDiscovery(VendorDiscovery):
    source = "https://antigravity-cli-auto-updater-974169037036.us-central1.run.app/manifests/"

    def _check(self, current: str, platform: str) -> ChannelReport:
        source = self.source + platform.replace("-", "_") + ".json"
        manifest = read_json(source)
        if not manifest.get("url") or not manifest.get("sha512"):
            raise ValueError("download/checksum missing")
        return _available(source, current, manifest["version"])


class PostgresqlDiscovery(VendorDiscovery):
    source = "https://www.postgresql.org/versions.json"

    def _check(self, current: str, platform: str) -> ChannelReport:
        # Existing base locks record only the major. Do not invent an installed
        # minor version or claim that an upstream minor is missing from the base.
        major_only = current.isascii() and current.isdigit()
        major = current if major_only else exact_version(current).split(".")[0]
        rows = read_json(self.source)
        row = next((row for row in rows if row["major"] == major), None)
        if row is None:
            raise ValueError(f"no support record for PostgreSQL {major}")
        if type(row["supported"]) is not bool:
            raise ValueError("invalid supported flag")
        end = date.fromisoformat(row["eolDate"])
        latest = major + "." + row["latestMinor"]
        report = _available(self.source, current if not major_only else major + ".0", latest,
                            "Requires a reviewed DevCapsule base update")
        supported = row["supported"] and end >= date.today()
        detail = f"Upstream major {major} support ends {end}; distribution backports are not assessed."
        notices = () if supported else (ChannelNotice(f"postgresql-{major}-eol", "end-of-support", detail),)
        # A minor release in an unsupported major is not a remedy for its EOL.
        candidates = report.candidates if supported and not major_only else ()
        if major_only:
            detail += f" Latest upstream minor: {latest}; installed minor is not recorded in this base lock."
        return ChannelReport(self.source, ChannelVersion(current, "available" if supported else "unsupported", detail, notices), candidates)
