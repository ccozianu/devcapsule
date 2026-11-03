"""What ``project wrap`` reads off a freshly added source to declare its needs.

The rules are facts about build tools, each with its source beside it, kept
as data so a new WPILib year or Gradle line is a one-line change.  Only what
the showcase of the wrapped-projects work order exercises is here: a Gradle
wrapper, with or without WPILib's GradleRIO plugin.  Anything else is
reported as undetected, and the developer completes the manifest with the
ordinary ``project config`` commands.

This module reads files and nothing else: no Git, no network, no writes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

__all__ = ["Detection", "detect"]

# WPILib ships and requires one JDK per season: 2025 and 2026 both ship
# JDK 17 (WPILib release notes; GradleRIO's toolchain check refuses others).
# The key is the GradleRIO plugin's year, the first component of its version.
GRADLERIO_JAVA_LINES: dict[str, str] = {"2025": "17", "2026": "17"}

# Gradle's Java compatibility table (docs.gradle.org/current/userguide/compatibility.html):
# every 8.x and 9.0 run on JDK 17; 9.1 is the first to run on JDK 25.
# Select 17 for 8.x and 9.0, and the capsule's default 25 from 9.1 onward.
# This is a wrapper selection rule, not Gradle's minimum Java requirement.
GRADLE_JAVA_LINES: tuple[tuple[tuple[int, int], str], ...] = (((9, 1), "25"), ((8, 0), "17"))

# Keep strings as whole tokens. A plugin example inside a string must never
# become an executable declaration. Comments are discarded below.
_SCRIPT_TOKEN = re.compile(
    "|".join((
        r"//[^\n]*", r"/\*.*?\*/",  # comments
        r"\$/.*?/\$", r"/(?:\\.|[^/\\])*/",  # Groovy slashy strings
        r'""".*?"""', r"'''.*?'''",  # multiline strings
        r'"(?:\\.|[^"\\])*"', r"'(?:\\.|[^'\\])*'",
        r"[A-Za-z_$][\w$]*", r"[^\s]",
    )),
    re.DOTALL,
)
_PLUGIN_YEAR = re.compile(r'''(["'])(\d{4})(?:\.[^"']*)?\1''')
_DISTRIBUTION_PROPERTY = re.compile(r"^[ \t]*distributionUrl[ \t]*(?:[=:][ \t]*|[ \t]+)([^\r\n]*)", re.MULTILINE)
_DISTRIBUTION_PATTERN = re.compile(r"/gradle-(\d+)\.(\d+)(?:[.\w-]*)-(?:bin|all)\.zip(?:[?#].*)?$")


@dataclass(frozen=True)
class Detection:
    """What a source needs, as read off its files.

    ``capabilities`` are the project capabilities every checkout must have;
    ``ide`` is the IDE to recommend; ``java`` is the Java line, or ``None``
    when the rules cannot name one; ``evidence`` says what was read.
    """

    capabilities: tuple[str, ...]
    ide: str | None
    java: str | None
    evidence: tuple[str, ...]


def detect(source: Path) -> Detection | None:
    """Detect the showcase's shapes; ``None`` when none of the rules apply."""
    build_script = next((source / name for name in ("build.gradle", "build.gradle.kts") if (source / name).is_file()), None)
    if not (source / "gradlew").is_file() or build_script is None:
        return None
    evidence = [f"Gradle wrapper and {build_script.name}"]
    year = _gradlerio_year(build_script.read_text(encoding="utf-8", errors="replace"))
    if year is not None:
        java = GRADLERIO_JAVA_LINES.get(year)
        evidence.append(f"GradleRIO {year}" + (f": WPILib {year} builds with Java {java}" if java else f": no Java line known for WPILib {year}"))
        return Detection(("java",), "java-ide", java, tuple(evidence))
    gradle = _gradle_java_line(source)
    evidence.append(f"Gradle {gradle[0]}: runs on Java {gradle[1]}" if gradle is not None else "no supported Gradle version found in distributionUrl in gradle-wrapper.properties")
    return Detection(("java",), "java-ide", gradle[1] if gradle is not None else None, tuple(evidence))


def _gradle_java_line(source: Path) -> tuple[str, str] | None:
    """The wrapper's Gradle version and the Java line it runs on, from ``gradle-wrapper.properties``."""
    properties = source / "gradle" / "wrapper" / "gradle-wrapper.properties"
    if not properties.is_file():
        return None
    declarations = _DISTRIBUTION_PROPERTY.findall(properties.read_text(encoding="utf-8", errors="replace"))
    match = _DISTRIBUTION_PATTERN.search(declarations[-1].strip()) if declarations else None
    if match is None:
        return None
    version = (int(match.group(1)), int(match.group(2)))
    for minimum, line in GRADLE_JAVA_LINES:
        if version >= minimum:
            return f"{version[0]}.{version[1]}", line
    return None


def _gradlerio_year(script: str) -> str | None:
    """Read a literal ``id ... version ...`` declaration, without evaluating Gradle."""
    tokens = [match.group() for match in _SCRIPT_TOKEN.finditer(script)
              if not match.group().startswith(("//", "/*"))]
    for index, token in enumerate(tokens):
        if token != "id":
            continue
        rest = tokens[index + 1:]
        if rest[:1] == ["("]:
            if len(rest) < 3 or rest[2] != ")":
                continue
            plugin, rest = rest[1], rest[3:]
        elif rest:
            plugin, rest = rest[0], rest[1:]
        else:
            continue
        if plugin not in ('"edu.wpi.first.GradleRIO"', "'edu.wpi.first.GradleRIO'") or rest[:1] != ["version"]:
            continue
        rest = rest[1:]
        if rest[:1] == ["("]:
            rest = rest[1:]
        match = _PLUGIN_YEAR.fullmatch(rest[0]) if rest else None
        if match is not None:
            return match.group(2)
    return None
