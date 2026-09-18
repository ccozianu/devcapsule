"""Check or intentionally advance DevCapsule's distribution version.

The version is authored in exactly one place, the ``[project]`` table of
``pyproject.toml``; everything else derives it — runtime code through
``importlib.metadata``, built artifacts through the build-time record
``scripts/build-pex.sh`` stamps. Two derived copies are kept in step by this
script rather than at build time, because they are read by humans and agents
straight from the repository: the ``version`` in the frontmatter of the root
``WORKFLOW.md`` and of the packaged workflow definition, which is what a
project's ``[workflow] version`` declaration refers to. A bump rewrites all
three and turns the definition's ``#### Unreleased`` changes entry into the
new version's entry; ``--check`` verifies the copies agree.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


VERSION_PATTERN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Workflow definitions whose frontmatter mirrors the distribution version,
# relative to the project root. Absent files are skipped: a checkout that
# carries only pyproject.toml, as the tests build, has nothing to mirror.
DEFINITION_COPIES = (
    Path("..") / "WORKFLOW.md",
    Path("devcapsule") / "assets" / "project_workflow" / "definition" / "WORKFLOW.md",
)
FRONTMATTER_VERSION = re.compile(r"^(---\n(?:(?!---\n).*\n)*?version:[ \t]*)([^\n]+)$", re.M)
UNRELEASED_HEADING = re.compile(r"^#### Unreleased$", re.M)


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
    for relative in DEFINITION_COPIES:
        path = project_root / relative
        if not path.is_file():
            continue
        mirrored = _definition_version(path)
        if mirrored != version:
            raise VersionError(
                f"{path} frontmatter declares version {mirrored!r}; pyproject.toml "
                f"says {version!r}. Run the bump to resynchronize."
            )
    return version


def _definition_version(path: Path) -> str | None:
    match = FRONTMATTER_VERSION.search(path.read_text(encoding="utf-8"))
    return None if match is None else match.group(2).strip()


def _stamp_definition(path: Path, version: str) -> None:
    """Set the frontmatter version and close the Unreleased changes entry."""
    text = path.read_text(encoding="utf-8")
    text, count = FRONTMATTER_VERSION.subn(lambda m: m.group(1) + version, text, count=1)
    if count != 1:
        raise VersionError(f"{path} has no frontmatter version to stamp")
    text = UNRELEASED_HEADING.sub(f"#### {version}", text, count=1)
    path.write_text(text, encoding="utf-8")


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
    for relative in DEFINITION_COPIES:
        definition = project_root / relative
        if definition.is_file():
            _stamp_definition(definition, selected)
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
