"""Check or intentionally advance DevCapsule's distribution version."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Callable


VERSION_PATTERN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
VersionReader = Callable[[Path, str | None], tuple[str, str]]


class VersionError(ValueError):
    """The checked-in distribution versions are invalid or inconsistent."""


def _pyproject_version_and_replacement(
    path: Path, replacement: str | None
) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    in_project = False
    found: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project = stripped == "[project]"
            continue
        if in_project:
            match = re.fullmatch(r'version\s*=\s*"([^"]+)"\s*', stripped)
            if match is not None:
                found.append((index, match.group(1)))
    if len(found) != 1:
        raise VersionError(
            f"{path} must contain exactly one [project] version; found {len(found)}"
        )
    index, current = found[0]
    if replacement is not None:
        newline = "\n" if lines[index].endswith("\n") else ""
        lines[index] = f'version = "{replacement}"{newline}'
    return current, "".join(lines)


def _package_version_and_replacement(
    path: Path, replacement: str | None
) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r'^__version__ = "([^"]+)"$', text, flags=re.MULTILINE)
    if match is None:
        raise VersionError(f"{path} must define __version__ as a quoted string")
    current = match.group(1)
    updated = text
    if replacement is not None:
        updated = text[: match.start(1)] + replacement + text[match.end(1) :]
    return current, updated


def _build_info_version_and_replacement(
    path: Path, replacement: str | None
) -> tuple[str, str]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VersionError(f"cannot read {path}: {exc}") from exc
    current = document.get("version")
    if not isinstance(current, str):
        raise VersionError(f"{path} must contain a string version")
    # The editable-source build mnemonic is derived, not independently
    # managed: it must always read v<version>-local. Official and binary
    # mnemonics are stamped at build time by scripts/build-pex.sh instead.
    if document.get("build_mnemonic") != f"v{current}-local":
        raise VersionError(
            f"{path} build_mnemonic must be 'v{current}-local'; "
            "the editable-source mnemonic is derived from the version"
        )
    if replacement is not None:
        document["version"] = replacement
        document["build_mnemonic"] = f"v{replacement}-local"
    updated = json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n"
    return current, updated


def _sources(project_root: Path) -> dict[Path, VersionReader]:
    return {
        project_root / "pyproject.toml": _pyproject_version_and_replacement,
        project_root / "devcapsule" / "__init__.py": _package_version_and_replacement,
        project_root
        / "devcapsule"
        / "_build_info.json": _build_info_version_and_replacement,
    }


def checked_version(project_root: Path = PROJECT_ROOT) -> str:
    versions = {
        path: reader(path, None)[0] for path, reader in _sources(project_root).items()
    }
    distinct = set(versions.values())
    if len(distinct) != 1:
        details = ", ".join(f"{path.name}={version}" for path, version in versions.items())
        raise VersionError(f"distribution versions disagree: {details}")
    version = distinct.pop()
    if VERSION_PATTERN.fullmatch(version) is None:
        raise VersionError(
            f"distribution version {version!r} must use numeric MAJOR.MINOR.PATCH form"
        )
    return version


def next_version(current: str, requested: str) -> str:
    parts = tuple(int(part) for part in current.split("."))
    if requested == "major":
        selected = (parts[0] + 1, 0, 0)
    elif requested == "minor":
        selected = (parts[0], parts[1] + 1, 0)
    elif requested == "patch":
        selected = (parts[0], parts[1], parts[2] + 1)
    elif VERSION_PATTERN.fullmatch(requested) is not None:
        explicit = requested.split(".")
        selected = (int(explicit[0]), int(explicit[1]), int(explicit[2]))
    else:
        raise VersionError(
            "version must be major, minor, patch, or an explicit numeric MAJOR.MINOR.PATCH"
        )
    if selected <= parts:
        raise VersionError(
            f"new distribution version {'.'.join(map(str, selected))} must be greater than {current}"
        )
    return ".".join(map(str, selected))


def bump_version(requested: str, project_root: Path = PROJECT_ROOT) -> tuple[str, str]:
    current = checked_version(project_root)
    selected = next_version(current, requested)
    replacements = {
        path: reader(path, selected)[1]
        for path, reader in _sources(project_root).items()
    }
    for path, text in replacements.items():
        path.write_text(text, encoding="utf-8")
    if checked_version(project_root) != selected:
        raise VersionError("distribution version did not update consistently")
    return current, selected


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check or intentionally advance the DevCapsule distribution version."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="verify all version sources agree")
    group.add_argument(
        "version",
        nargs="?",
        help="major, minor, patch, or an explicit numeric MAJOR.MINOR.PATCH",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.check:
            print(f"DevCapsule package version: {checked_version()}")
        else:
            previous, selected = bump_version(args.version)
            print(f"DevCapsule package version: {previous} -> {selected}")
    except VersionError as exc:
        print(f"bump-version: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
