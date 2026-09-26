"""Composable image-build planning and Docker buildx execution."""

from __future__ import annotations

import json
import os
import re
import shutil
import tarfile
import tempfile
from dataclasses import dataclass, field, replace
from importlib import resources
from pathlib import Path
from typing import Protocol

from python_on_whales import docker
from python_on_whales.exceptions import DockerException

from devcapsule.compat import CliError, copy_resource_tree


@dataclass(frozen=True)
class ExecStep:
    args: tuple[str, ...]


@dataclass(frozen=True)
class DirectoryCopy:
    source: Path
    destination: str


@dataclass(frozen=True)
class FileCopy:
    source: Path
    destination: str
    permissions: int | None = None


@dataclass(frozen=True)
class ImageCopy:
    image: str
    source: str
    destination: str


@dataclass(frozen=True)
class BuildStage:
    name: str
    plan: ImageBuildPlan
    exports: tuple[str, ...]


@dataclass(frozen=True)
class ImageBuildPlan:
    base_image: str
    image: str
    apt_packages: tuple[str, ...] = ()
    env: tuple[tuple[str, str], ...] = ()
    labels: tuple[tuple[str, str], ...] = ()
    directories: tuple[DirectoryCopy, ...] = ()
    files: tuple[FileCopy, ...] = ()
    exec_steps: tuple[ExecStep, ...] = ()
    entrypoint: tuple[str, ...] = ()
    command: tuple[str, ...] = ()
    stages: tuple[BuildStage, ...] = ()
    image_copies: tuple[ImageCopy, ...] = ()

    def add_apt_packages(self, *packages: str) -> ImageBuildPlan:
        return replace(self, apt_packages=self.apt_packages + tuple(packages))

    def add_env(self, **values: str) -> ImageBuildPlan:
        return replace(self, env=self.env + tuple(values.items()))

    def add_labels(self, **values: str) -> ImageBuildPlan:
        return replace(self, labels=self.labels + tuple(values.items()))

    def add_directory(self, source: Path, destination: str) -> ImageBuildPlan:
        return replace(self, directories=self.directories + (DirectoryCopy(source=source, destination=destination),))

    def add_file(self, source: Path, destination: str, *, permissions: int | None = None) -> ImageBuildPlan:
        return replace(
            self,
            files=self.files + (FileCopy(source=source, destination=destination, permissions=permissions),),
        )

    def add_exec(self, *args: str) -> ImageBuildPlan:
        return replace(self, exec_steps=self.exec_steps + (ExecStep(args=tuple(args)),))

    def set_entrypoint(self, *args: str) -> ImageBuildPlan:
        return replace(self, entrypoint=tuple(args))

    def set_command(self, *args: str) -> ImageBuildPlan:
        return replace(self, command=tuple(args))


class BuildComponent(Protocol):
    def apply(self, plan: ImageBuildPlan) -> ImageBuildPlan: ...


@dataclass(frozen=True)
class BaseImageComponent:
    image: str

    def apply(self, plan: ImageBuildPlan) -> ImageBuildPlan:
        return replace(plan, base_image=self.image)


@dataclass(frozen=True)
class AptPackagesComponent:
    packages: tuple[str, ...]

    def apply(self, plan: ImageBuildPlan) -> ImageBuildPlan:
        return plan.add_apt_packages(*self.packages)


@dataclass(frozen=True)
class EnvComponent:
    values: tuple[tuple[str, str], ...]

    def apply(self, plan: ImageBuildPlan) -> ImageBuildPlan:
        return replace(plan, env=plan.env + self.values)


@dataclass(frozen=True)
class LabelComponent:
    values: tuple[tuple[str, str], ...]

    def apply(self, plan: ImageBuildPlan) -> ImageBuildPlan:
        return replace(plan, labels=plan.labels + self.values)


@dataclass(frozen=True)
class DirectoryComponent:
    source: Path
    destination: str

    def apply(self, plan: ImageBuildPlan) -> ImageBuildPlan:
        return plan.add_directory(self.source, self.destination)


@dataclass(frozen=True)
class FileComponent:
    source: Path
    destination: str
    permissions: int | None = None

    def apply(self, plan: ImageBuildPlan) -> ImageBuildPlan:
        return plan.add_file(self.source, self.destination, permissions=self.permissions)


@dataclass(frozen=True)
class ExecComponent:
    args: tuple[str, ...]

    def apply(self, plan: ImageBuildPlan) -> ImageBuildPlan:
        return plan.add_exec(*self.args)


@dataclass(frozen=True)
class EntrypointComponent:
    args: tuple[str, ...]

    def apply(self, plan: ImageBuildPlan) -> ImageBuildPlan:
        return plan.set_entrypoint(*self.args)


@dataclass(frozen=True)
class CommandComponent:
    args: tuple[str, ...]

    def apply(self, plan: ImageBuildPlan) -> ImageBuildPlan:
        return plan.set_command(*self.args)


@dataclass(frozen=True)
class ImageCopyComponent:
    image: str
    source: str
    destination: str

    def apply(self, plan: ImageBuildPlan) -> ImageBuildPlan:
        return replace(plan, image_copies=plan.image_copies + (
            ImageCopy(self.image, self.source, self.destination),
        ))


@dataclass(frozen=True)
class ContributionComponent:
    """An independently cached installation with explicit filesystem exports.

    BuildKit keys each stage on its parent, commands and copied inputs. Neither
    another contribution nor the final image's name/metadata enters that key.
    Environment variables belong to the consuming image, not the export.
    """

    name: str
    components: tuple[BuildComponent, ...]
    exports: tuple[str, ...]
    base_image: str = "devcapsule-baseline"

    def apply(self, plan: ImageBuildPlan) -> ImageBuildPlan:
        contribution = ImageBuildSpec(self.name, self.base_image, self.components).build_plan()
        return replace(plan, stages=plan.stages + (
            BuildStage(self.name, contribution, self.exports),
        ))


@dataclass(frozen=True)
class ImageBuildSpec:
    image: str
    base_image: str
    components: tuple[BuildComponent, ...] = field(default_factory=tuple)

    def build_plan(self) -> ImageBuildPlan:
        plan = ImageBuildPlan(base_image=self.base_image, image=self.image)
        for component in self.components:
            plan = component.apply(plan)
        return plan


class BuildxImageBuilder:
    """Build a planned image through the local Docker CLI via python-on-whales."""

    def __init__(self, temporary_root: Path | None = None) -> None:
        self.temporary_root = temporary_root

    def build(self, spec: ImageBuildSpec, *, network: str = "default") -> None:
        plan = spec.build_plan()
        if self.temporary_root is not None:
            self.temporary_root.mkdir(parents=True, exist_ok=True)
        try:
            with tempfile.TemporaryDirectory(
                prefix="devcapsule-buildx-context-", dir=self.temporary_root
            ) as temp_dir:
                context_root = Path(temp_dir)
                dockerfile_path = render_build_context(plan, context_root)
                if network == "host":
                    docker.build(
                        context_root,
                        file=dockerfile_path,
                        tags=[plan.image],
                        load=True,
                        network=network,
                        allow=["network.host"],
                    )
                else:
                    docker.build(
                        context_root,
                        file=dockerfile_path,
                        tags=[plan.image],
                        load=True,
                        network=network,
                    )
        except DockerException as exc:
            raise CliError(str(exc)) from exc
        except OSError as exc:
            location = self.temporary_root or Path(tempfile.gettempdir())
            raise CliError(f"Cannot prepare Docker build context beneath {location}: {exc}") from exc


def render_build_context(plan: ImageBuildPlan, context_root: Path) -> Path:
    context_root.mkdir(parents=True, exist_ok=True)
    dockerfile_lines: list[str] = []
    if plan.stages:
        dockerfile_lines.append("# syntax=docker/dockerfile:1")
        baseline = ImageBuildPlan(plan.base_image, "", apt_packages=plan.apt_packages)
        dockerfile_lines.extend(_render_stage(baseline, context_root, "devcapsule-baseline"))
        names = {"devcapsule-baseline"}
        for stage in plan.stages:
            if not re.fullmatch(r"[a-z][a-z0-9-]*", stage.name) or stage.name in names:
                raise ValueError(f"Invalid or repeated contribution name: {stage.name!r}")
            if stage.plan.stages:
                raise ValueError("Nested contribution stages are not supported")
            names.add(stage.name)
            dockerfile_lines.extend(_render_stage(stage.plan, context_root, stage.name))
        copies = tuple(
            ImageCopy(stage.name, path, path)
            for stage in plan.stages for path in stage.exports
        )
        plan = replace(plan, base_image="devcapsule-baseline", apt_packages=(),
                       image_copies=copies + plan.image_copies)
    dockerfile_lines.extend(_render_stage(plan, context_root))
    dockerfile_path = context_root / "Dockerfile"
    dockerfile_path.write_text("\n".join(dockerfile_lines) + "\n", encoding="utf-8")
    return dockerfile_path


def _render_stage(plan: ImageBuildPlan, context_root: Path, name: str = "") -> list[str]:
    dockerfile_lines = [f"FROM {plan.base_image}" + (f" AS {name}" if name else "")]
    prefix = f"{name}-" if name else ""
    copy_index = 0

    if plan.apt_packages:
        apt_packages = " ".join(plan.apt_packages)
        dockerfile_lines.extend(
            [
                "ARG DEBIAN_FRONTEND=noninteractive",
                "RUN apt-get update \\",
                f" && apt-get install -y --no-install-recommends {apt_packages} \\",
                " && rm -rf /var/lib/apt/lists/*",
            ]
        )

    for directory_copy in plan.directories:
        relative_source = f"{prefix}copy-dir-{copy_index}"
        destination = normalize_container_path(directory_copy.destination)
        shutil.copytree(directory_copy.source, context_root / relative_source, dirs_exist_ok=True, symlinks=True)
        dockerfile_lines.append(f"COPY {relative_source}/ {destination}/")
        copy_index += 1

    for file_copy in plan.files:
        relative_source = f"{prefix}copy-file-{copy_index}"
        destination = normalize_container_path(file_copy.destination)
        destination_parent = Path(destination).parent.as_posix()
        shutil.copy2(file_copy.source, context_root / relative_source)
        dockerfile_lines.append(f"RUN mkdir -p {shell_quote(destination_parent)}")
        dockerfile_lines.append(f"COPY {relative_source} {destination}")
        if file_copy.permissions is not None:
            dockerfile_lines.append(f"RUN chmod {file_copy.permissions:o} {shell_quote(destination)}")
        copy_index += 1

    for copy in plan.image_copies:
        source = normalize_container_path(copy.source)
        destination = normalize_container_path(copy.destination)
        dockerfile_lines.append(f"COPY --link --from={copy.image} {source} {destination}")

    for step in plan.exec_steps:
        dockerfile_lines.append(f"RUN {shell_join(step.args)}")
    for name, value in plan.env:
        dockerfile_lines.append(f"ENV {name}={shell_env_value(value)}")
    for name, value in plan.labels:
        dockerfile_lines.append(f"LABEL {name}={shell_env_value(value)}")
    if plan.entrypoint:
        dockerfile_lines.append(f"ENTRYPOINT {json.dumps(list(plan.entrypoint))}")
    if plan.command:
        dockerfile_lines.append(f"CMD {json.dumps(list(plan.command))}")

    return dockerfile_lines


def normalize_container_path(path: str) -> str:
    if not path.startswith("/"):
        raise CliError(f"Container path must be absolute: {path}")
    return path.rstrip("/") or "/"


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def shell_join(args: tuple[str, ...]) -> str:
    return " ".join(shell_quote(arg) for arg in args)


def shell_env_value(value: str) -> str:
    return json.dumps(value)


def extract_resource_tree(package: str, destination: Path) -> None:
    source = resources.files(package)
    copy_resource_tree(source, destination)


def normalize_archive_directory(source: Path, destination: Path) -> Path:
    """Return the installation root of an unpacked archive.

    JetBrains archives wrap everything in one top-level directory; VS
    Code-family archives are flat, with the installation at the archive root.
    """

    extract_root = destination / "extract"
    extract_root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(source, "r:gz") as archive:
        archive.extractall(extract_root, filter="data")

    entries = list(extract_root.iterdir())
    if not entries:
        raise CliError("The verified archive contains no content")
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return extract_root


def normalize_pycharm_source(source: Path, destination: Path) -> Path:
    if source.is_dir():
        normalized = source
    elif source.is_file():
        normalized = normalize_archive_directory(source, destination)
    else:
        raise CliError(f"PyCharm source path does not exist: {source}")

    launcher = normalized / "bin" / "pycharm.sh"
    if not launcher.is_file():
        raise CliError("The supplied PyCharm source does not contain bin/pycharm.sh")
    if not os.access(launcher, os.X_OK):
        raise CliError("The supplied PyCharm source does not contain executable bin/pycharm.sh")
    return normalized


def resource_to_tempdir(package: str) -> tempfile.TemporaryDirectory[str]:
    temp_dir = tempfile.TemporaryDirectory(prefix="devcapsule-build-assets-")
    extract_resource_tree(package, Path(temp_dir.name))
    for script in Path(temp_dir.name).glob("*.sh"):
        script.chmod(script.stat().st_mode | 0o755)
    return temp_dir
