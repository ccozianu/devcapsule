"""``project wrap``: a foreign repository as a submodule, declared, explained, repeatable (work order of 2026-11-02)."""

from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from devcapsule import cli
from devcapsule.configuration.file_formats import ProjectConfigurationError
from devcapsule.configuration.storage import load_toml
from devcapsule.wrap import GUIDANCE_MARKER, WrapRequest, wrap_project
from tests.test_wrap_detection import gradle_project

GRADLERIO = 'plugins {\n    id "java"\n    id "edu.wpi.first.GradleRIO" version "2025.3.2"\n}\n'


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture(autouse=True)
def local_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolated homes, and Git allowed to clone from a local path, which it refuses by default since 2.38.1."""
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "protocol.file.allow")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "always")


def upstream(tmp_path: Path, name: str, *, script: str = GRADLERIO) -> str:
    """A bare repository holding one commit of a Gradle project, as a URL ``wrap`` can clone."""
    work = gradle_project(tmp_path / "work" / name, script=script)
    git(work, "init", "--quiet")
    git(work, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "add", "-A")
    git(work, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "--quiet", "-m", "seed")
    bare = tmp_path / "remote" / f"{name}.git"
    git(tmp_path, "clone", "--quiet", "--bare", str(work), str(bare))
    return str(bare)


def wrapper(tmp_path: Path) -> Path:
    root = tmp_path / "frc-learning"
    root.mkdir()
    git(root, "init", "--quiet")
    return root


def request(root: Path, url: str, **fields) -> WrapRequest:
    return WrapRequest(directory=root, url=url, creator="https://github.com/example", interactive=False, **fields)


def test_a_first_wrap_builds_the_whole_wrapper(tmp_path: Path) -> None:
    url = upstream(tmp_path, "RobotCode2025Public")
    root = wrapper(tmp_path)
    report = wrap_project(request(root, url))
    text = report.render()
    assert text.startswith(f"Added the submodule RobotCode2025Public from {url}; its Git directory is embedded in the tree.")
    assert "GradleRIO 2025: WPILib 2025 builds with Java 17" in text
    assert report.initialized is not None and report.initialized.required == ("java",)
    assert "Recommended ide = java-ide" in text
    assert "Declared source RobotCode2025Public; the manifest is updated." in text
    assert "Wrote AGENTS.md." in text and "Wrote README.md." in text
    manifest = load_toml(root / ".devcapsule" / "devcapsule.toml")
    assert manifest["capabilities"] == {"required": ["java"]}
    assert manifest["sources"] == {"RobotCode2025Public": {"java": "17"}}
    assert manifest["recommendations"] == {"ide": "java-ide"}
    assert (root / ".devcapsule" / "devcapsule.linux-amd64.lock").is_file()
    # The submodule is registered, staged, and its Git directory lives in the tree the capsule mounts.
    assert git(root, "config", "-f", ".gitmodules", "submodule.RobotCode2025Public.url") == url
    assert (root / "RobotCode2025Public" / ".git").is_dir()
    assert not (root / ".git" / "modules" / "RobotCode2025Public").exists()
    assert "worktree" not in (root / "RobotCode2025Public" / ".git" / "config").read_text()
    assert git(root / "RobotCode2025Public", "status", "--porcelain") == ""
    assert git(root, "status", "--porcelain") == "A  .gitmodules\nA  RobotCode2025Public\n?? .devcapsule/\n?? AGENTS.md\n?? README.md"
    agents = (root / "AGENTS.md").read_text()
    assert agents.startswith(GUIDANCE_MARKER + "\n")
    assert "### `RobotCode2025Public`" in agents and f"- Origin: {url}" in agents
    assert "- Intent: learn from it; it is read-only, nothing is pushed." in agents
    assert 'export JAVA_HOME=/opt/java/17; export PATH="$JAVA_HOME/bin:$PATH"' in agents
    readme = (root / "README.md").read_text()
    assert readme.startswith(GUIDANCE_MARKER + "\n# frc-learning\n") and "git submodule update --init" in readme


def test_a_second_wrap_extends_the_manifest_and_regenerates_the_guidance(tmp_path: Path) -> None:
    url = upstream(tmp_path, "RobotCode2025Public")
    other = upstream(tmp_path, "AdvantageKit", script='plugins { id "java" }\n')
    root = wrapper(tmp_path)
    wrap_project(request(root, url))
    text = wrap_project(request(root, other, upstream="https://github.com/Mechanical-Advantage/AdvantageKit")).render()
    assert "Gradle 8.11: runs on Java 17" in text
    assert "Declared source AdvantageKit; the manifest is updated." in text
    assert "Requires:" not in text  # nothing re-initialized; java was already required
    manifest = load_toml(root / ".devcapsule" / "devcapsule.toml")
    assert manifest["sources"] == {"AdvantageKit": {"upstream": "https://github.com/Mechanical-Advantage/AdvantageKit", "java": "17"},
                                   "RobotCode2025Public": {"java": "17"}}
    agents = (root / "AGENTS.md").read_text()
    assert agents.index("### `AdvantageKit`") < agents.index("### `RobotCode2025Public`")
    assert ("- Intent: change it in your fork; pull requests go to the fork's origin, never to the upstream. "
            "Upstream: https://github.com/Mechanical-Advantage/AdvantageKit.") in agents


def test_a_rerun_keeps_the_submodule_and_redeclares(tmp_path: Path) -> None:
    url = upstream(tmp_path, "RobotCode2025Public")
    root = wrapper(tmp_path)
    wrap_project(request(root, url))
    text = wrap_project(request(root, url)).render()
    assert text.startswith(f"Kept the submodule RobotCode2025Public, already added from {url}.")
    assert "Redeclared source RobotCode2025Public" in text
    assert git(root, "status", "--porcelain").count("RobotCode2025Public") == 1


def test_an_undetected_source_declares_nothing_but_itself(tmp_path: Path) -> None:
    work = tmp_path / "work" / "notes"
    work.mkdir(parents=True)
    (work / "README.md").write_text("notes\n")
    git(work, "init", "--quiet")
    git(work, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "add", "-A")
    git(work, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "--quiet", "-m", "seed")
    root = wrapper(tmp_path)
    text = wrap_project(request(root, str(work), path="notes")).render()
    assert "Detected nothing in notes that these rules know; declare what it needs with 'devcapsule project config require CAPABILITY'." in text
    manifest = load_toml(root / ".devcapsule" / "devcapsule.toml")
    assert manifest["capabilities"] == {"required": []}
    assert manifest["sources"] == {"notes": {}}
    assert "recommendations" not in manifest
    assert "- Builds with Java" not in (root / "AGENTS.md").read_text()


def test_the_owners_own_guidance_is_kept_and_named(tmp_path: Path) -> None:
    url = upstream(tmp_path, "RobotCode2025Public")
    root = wrapper(tmp_path)
    (root / "AGENTS.md").write_text("# Mine\n")
    text = wrap_project(request(root, url)).render()
    assert "Kept your AGENTS.md; it does not carry the wrap marker. Add the wrapped sources to it yourself." in text
    assert (root / "AGENTS.md").read_text() == "# Mine\n"
    assert (root / "README.md").read_text().startswith(GUIDANCE_MARKER)


def test_refusals_name_the_remedy_before_anything_changes(tmp_path: Path) -> None:
    url = upstream(tmp_path, "RobotCode2025Public")
    plain = tmp_path / "plain"
    plain.mkdir()
    with pytest.raises(ProjectConfigurationError, match="not a Git repository; 'git init' there first"):
        wrap_project(request(plain, url))
    root = wrapper(tmp_path)
    nested = root / "inside"
    nested.mkdir()
    with pytest.raises(ProjectConfigurationError, match="Wrap at the repository's top level"):
        wrap_project(request(nested, url))
    (root / "RobotCode2025Public").mkdir()
    with pytest.raises(ProjectConfigurationError, match="exists and is not a submodule added from"):
        wrap_project(request(root, url))
    with pytest.raises(ProjectConfigurationError, match="--path"):
        wrap_project(request(root, url, path="../escape"))
    assert not (root / ".devcapsule").exists() and not (root / ".gitmodules").exists()


@pytest.mark.parametrize("url, name", [
    ("https://github.com/Mechanical-Advantage/RobotCode2025Public", "RobotCode2025Public"),
    ("https://github.com/Mechanical-Advantage/RobotCode2025Public.git", "RobotCode2025Public"),
    ("git@github.com:ccozianu/devcapsule-sample-frc-learning.git", "devcapsule-sample-frc-learning"),
    ("/tmp/remote/robot.git/", "robot"),
])
def test_the_submodule_is_named_after_the_repository(url: str, name: str) -> None:
    from devcapsule.wrap import _repository_name
    assert _repository_name(url) == name


def test_the_command_line_reaches_the_operation(tmp_path: Path, capsys) -> None:
    url = upstream(tmp_path, "RobotCode2025Public")
    root = wrapper(tmp_path)
    assert cli.main(["project", "--path", str(root), "wrap", url, "--creator", "https://github.com/example", "--ide", "none",
                     "--upstream", "https://github.com/Mechanical-Advantage/RobotCode2025Public"]) == 0
    out = capsys.readouterr().out
    assert "Declared source RobotCode2025Public; the manifest is updated." in out
    assert out.rstrip().endswith("then 'devcapsule project run' opens the capsule.")
    assert load_toml(root / ".devcapsule" / "devcapsule.toml")["sources"]["RobotCode2025Public"]["upstream"] == "https://github.com/Mechanical-Advantage/RobotCode2025Public"
    assert cli.main(["project", "--path", str(root), "config", "show"]) == 0
    assert "source      RobotCode2025Public  java 17" in capsys.readouterr().out
