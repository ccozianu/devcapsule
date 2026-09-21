"""Pinned npm meta-package + platform-alias distribution, without running npm."""
from __future__ import annotations

import json
import re
from typing import Any
from urllib.error import URLError
from urllib.parse import quote, urlparse
from urllib.request import urlopen

from devcapsule.compat import CliError
from devcapsule.components.channels import ChannelNotice, ChannelReport, ChannelSelection, ChannelVersion


class NpmChannel:
    def __init__(self, package: str, platform_aliases: dict[str, str], *, node_engine: str = ">=16"):
        self.package = package
        self.platform_aliases = platform_aliases
        self.node_engine = node_engine
        self.source = "https://registry.npmjs.org/" + quote(package, safe="@")

    def _metadata(self, version: str = "") -> dict[str, Any]:
        url = self.source + ("/" + quote(version, safe="") if version else "")
        try:
            with urlopen(url, timeout=15) as response:
                payload = response.read(16 * 1024 * 1024 + 1)
            if len(payload) > 16 * 1024 * 1024:
                raise ValueError("metadata exceeds 16 MiB")
            value = json.loads(payload)
            if not isinstance(value, dict):
                raise ValueError("expected a JSON object")
            return value
        except (URLError, ValueError, OSError) as exc:
            raise CliError(f"Distribution check unavailable at {url}: {exc}. Retry 'project versions check'; saved choices are unchanged.") from exc

    def check(self, current: str, platform: str) -> ChannelReport:
        if platform not in self.platform_aliases:
            return ChannelReport(self.source, ChannelVersion(current, "unsupported", f"No package for {platform}"), ())
        document = self._metadata()
        versions = document.get("versions")
        tags = document.get("dist-tags")
        if not isinstance(versions, dict) or not isinstance(tags, dict) or not isinstance(tags.get("latest"), str):
            raise CliError(f"Malformed distribution metadata at {self.source}: expected versions and dist-tags.latest.")
        def status(version: str) -> ChannelVersion:
            data = versions.get(version)
            if data is None:
                return ChannelVersion(version, "withdrawn", "Not listed in the current registry metadata")
            if not isinstance(data, dict):
                raise CliError(f"Malformed npm version {version!r}.")
            deprecated = data.get("deprecated")
            if deprecated is not None and not isinstance(deprecated, str):
                raise CliError(f"Malformed npm deprecation notice for {version!r}.")
            notices = (ChannelNotice("npm-deprecation", "end-of-support", deprecated),) if deprecated else ()
            return ChannelVersion(version, "unsupported" if deprecated else "available", deprecated or "", notices)
        latest = tags["latest"]
        if latest not in versions:
            raise CliError("Malformed npm metadata: latest is not a published version.")
        # Registry labels are discovery only. Selection resolves the label again
        # to a concrete version and immutable SRI identities before preparation.
        return ChannelReport(self.source, status(current), (status(latest),) if latest != current else ())

    def select(self, version: str, platform: str) -> ChannelSelection:
        alias = self.platform_aliases.get(platform)
        if alias is None:
            raise CliError(f"{self.package} has no distribution for {platform}.")
        meta = self._metadata(version)
        exact = meta.get("version")
        if not isinstance(exact, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?", exact):
            raise CliError("Malformed npm metadata: expected an exact safe version.")
        if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?", version) and version != exact:
            raise CliError("Registry response does not match the requested exact version.")
        engines = meta.get("engines")
        if meta.get("name") != self.package or meta.get("dependencies") or not isinstance(engines, dict) or engines.get("node") != self.node_engine:
            raise CliError("The npm package changed its name, dependencies or Node requirement; a reviewed channel adapter update is needed.")
        dependencies = meta.get("optionalDependencies", {})
        dependency = dependencies.get(alias) if isinstance(dependencies, dict) else None
        prefix = "npm:" + self.package + "@"
        if not isinstance(dependency, str) or not dependency.startswith(prefix):
            raise CliError(f"Missing exact platform dependency {alias!r} in npm metadata.")
        platform_version = dependency[len(prefix):]
        if platform_version != exact + alias.removeprefix(self.package):
            raise CliError(f"Non-exact or mismatched platform dependency {dependency!r}.")
        binary = self._metadata(platform_version)
        if binary.get("name") != self.package or binary.get("version") != platform_version or binary.get("dependencies"):
            raise CliError("Malformed or incompatible platform package metadata.")
        operating_system, architecture = platform.split("-", 1)
        npm_arch = {"amd64": "x64", "arm64": "arm64"}.get(architecture)
        if binary.get("os") != [operating_system] or binary.get("cpu") != [npm_arch]:
            raise CliError("Platform package OS/CPU does not match the selected platform.")
        metadata = {
            "version": exact, "delivery-policy": "local-materialization", "npm-package": self.package,
            **self._artifact(meta),
            "artifacts": {platform: {"npm-package": alias, **self._artifact(binary)}},
        }
        return ChannelSelection(metadata, (platform,), base_families=("ubuntu-24.04",),
                                status="unsupported" if meta.get("deprecated") else "available",
                                detail=str(meta.get("deprecated") or ""))

    @staticmethod
    def _artifact(metadata: dict[str, Any]) -> dict[str, str]:
        dist = metadata.get("dist", {})
        url, integrity = (dist.get("tarball"), dist.get("integrity")) if isinstance(dist, dict) else (None, None)
        if not isinstance(url, str) or urlparse(url).scheme != "https" or urlparse(url).netloc != "registry.npmjs.org":
            raise CliError("npm artifact must be an HTTPS registry.npmjs.org URL.")
        if not isinstance(integrity, str) or not re.fullmatch(r"sha512-[A-Za-z0-9+/]{86}==", integrity):
            raise CliError("npm artifact must publish a SHA-512 integrity value.")
        return {"url": url, "integrity": integrity}
