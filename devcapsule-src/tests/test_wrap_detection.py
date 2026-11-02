"""What ``project wrap`` reads off a source: the showcase's Gradle shapes, as data with their sources."""

from __future__ import annotations

from pathlib import Path

import pytest

from devcapsule.wrap_detection import Detection, detect


def gradle_project(root: Path, *, script: str = 'plugins {\n    id "java"\n}\n', distribution: str | None = "8.11", kts: bool = False) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "gradlew").write_text("#!/bin/sh\n")
    (root / ("build.gradle.kts" if kts else "build.gradle")).write_text(script)
    if distribution is not None:
        (root / "gradle" / "wrapper").mkdir(parents=True)
        (root / "gradle" / "wrapper" / "gradle-wrapper.properties").write_text(
            f"distributionUrl=https\\://services.gradle.org/distributions/gradle-{distribution}-bin.zip\n")
    return root


@pytest.mark.parametrize("year, line", [("2025", "17"), ("2026", "17")])
def test_gradlerio_names_the_java_line_of_its_wpilib_year(tmp_path: Path, year: str, line: str) -> None:
    source = gradle_project(tmp_path / "robot", script=f'plugins {{\n    id "edu.wpi.first.GradleRIO" version "{year}.3.2"\n}}\n')
    assert detect(source) == Detection(("java",), "java-ide", line,
                                       ("Gradle wrapper and build.gradle", f"GradleRIO {year}: WPILib {year} builds with Java {line}"))


def test_gradlerio_in_a_kotlin_script_is_read_too(tmp_path: Path) -> None:
    source = gradle_project(tmp_path / "robot", script='plugins {\n    id("edu.wpi.first.GradleRIO") version "2026.1.1"\n}\n', kts=True)
    detection = detect(source)
    assert detection is not None and detection.java == "17" and detection.evidence[0] == "Gradle wrapper and build.gradle.kts"


def test_an_unknown_wpilib_year_requires_java_but_names_no_line(tmp_path: Path) -> None:
    source = gradle_project(tmp_path / "robot", script='plugins { id "edu.wpi.first.GradleRIO" version "2031.1.1" }\n')
    assert detect(source) == Detection(("java",), "java-ide", None,
                                       ("Gradle wrapper and build.gradle", "GradleRIO 2031: no Java line known for WPILib 2031"))


@pytest.mark.parametrize("distribution, line", [("8.11", "17"), ("8.0", "17"), ("9.0", "17"), ("9.1", "25"), ("10.2", "25")])
def test_plain_gradle_gets_the_oldest_line_its_wrapper_runs_on(tmp_path: Path, distribution: str, line: str) -> None:
    source = gradle_project(tmp_path / "lib", distribution=distribution)
    assert detect(source) == Detection(("java",), "java-ide", line,
                                       ("Gradle wrapper and build.gradle", f"Gradle {distribution}: runs on Java {line}"))


def test_a_gradle_wrapper_without_a_readable_version_names_no_line(tmp_path: Path) -> None:
    source = gradle_project(tmp_path / "lib", distribution=None)
    assert detect(source) == Detection(("java",), "java-ide", None,
                                       ("Gradle wrapper and build.gradle", "the Gradle version is not in gradle-wrapper.properties"))


def test_anything_else_is_undetected(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    assert detect(tmp_path) is None
    (tmp_path / "gradlew").write_text("")  # a wrapper without a build script says nothing
    assert detect(tmp_path) is None
