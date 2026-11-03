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
def test_plain_gradle_gets_the_declared_selection_for_its_wrapper(tmp_path: Path, distribution: str, line: str) -> None:
    source = gradle_project(tmp_path / "lib", distribution=distribution)
    assert detect(source) == Detection(("java",), "java-ide", line,
                                       ("Gradle wrapper and build.gradle", f"Gradle {distribution}: runs on Java {line}"))


def test_a_gradle_wrapper_without_a_readable_version_names_no_line(tmp_path: Path) -> None:
    source = gradle_project(tmp_path / "lib", distribution=None)
    assert detect(source) == Detection(("java",), "java-ide", None,
                                       ("Gradle wrapper and build.gradle", "no supported Gradle version found in distributionUrl in gradle-wrapper.properties"))


def test_anything_else_is_undetected(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    assert detect(tmp_path) is None
    (tmp_path / "gradlew").write_text("")  # a wrapper without a build script says nothing
    assert detect(tmp_path) is None


@pytest.mark.parametrize("script", [
    '// id "edu.wpi.first.GradleRIO" version "2025.3.2"',
    '/* id "edu.wpi.first.GradleRIO" version "2025.3.2" */',
    '''def example = 'id "edu.wpi.first.GradleRIO" version "2025.3.2"' ''',
    '''def example = """id "edu.wpi.first.GradleRIO" version "2025.3.2"""" ''',
    '''def example = /id "edu.wpi.first.GradleRIO" version "2025.3.2"/ ''',
    '''def example = $/id "edu.wpi.first.GradleRIO" version "2025.3.2"/$ ''',
])
def test_gradlerio_mentions_are_not_plugin_declarations(tmp_path: Path, script: str) -> None:
    source = gradle_project(tmp_path / "lib", script=script, distribution="9.1")
    result = detect(source)
    assert result is not None and result.java == "25"
    assert result.evidence[-1] == "Gradle 9.1: runs on Java 25"


def test_comments_between_plugin_tokens_do_not_hide_the_declaration(tmp_path: Path) -> None:
    source = gradle_project(tmp_path / "lib", script='plugins { id /* plugin */ ("edu.wpi.first.GradleRIO") version /* year */ "2026.1.1" }', distribution="9.1")
    result = detect(source)
    assert result is not None and result.java == "17"


@pytest.mark.parametrize("properties, line", [
    ('# distributionUrl=https://example/gradle-8.11-bin.zip\ndistributionUrl=https://example/gradle-9.1-bin.zip\n', "25"),
    ('other=https://example/gradle-8.11-bin.zip\ndistributionUrl=https://example/gradle-9.1-bin.zip\n', "25"),
    ('other=https://example/gradle-8.11-bin.zip\n', None),
    ('distributionUrl=https://example/gradle-7.6-bin.zip\n', None),
    ('distributionUrl=https://example/unknown.zip\n', None),
])
def test_gradle_version_comes_only_from_distribution_url(tmp_path: Path, properties: str, line: str | None) -> None:
    source = gradle_project(tmp_path / "lib")
    (source / "gradle/wrapper/gradle-wrapper.properties").write_text(properties)
    result = detect(source)
    assert result is not None and result.java == line
