"""Check or intentionally advance DevCapsule's distribution version.

The version is authored in exactly one place, the ``[project]`` table of
``pyproject.toml``; everything else derives it — runtime code through
``importlib.metadata``, built artifacts through the build-time record
``scripts/build-pex.sh`` stamps. This script therefore only validates that
single source's shape and rewrites it on an intentional bump.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


VERSION_PATTERN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
PROJECT_ROOT = Path(__file__).resolve().parents[1]


class VersionError(ValueError):
    """The checked-in distribution version is invalid."""


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


def checked_version(project_root: Path = PROJECT_ROOT) -> str:
    version, _ = _pyproject_version_and_replacement(
        project_root / "pyproject.toml", None
    )
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
    path = project_root / "pyproject.toml"
    _, updated = _pyproject_version_and_replacement(path, selected)
    path.write_text(updated, encoding="utf-8")
    if checked_version(project_root) != selected:
        raise VersionError("distribution version did not update consistently")
    return current, selected


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check or intentionally advance the DevCapsule distribution version."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="verify the version's form")
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
