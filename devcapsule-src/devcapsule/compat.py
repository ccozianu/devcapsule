"""Compatibility helpers for legacy shell-backed commands."""

from __future__ import annotations

from contextlib import contextmanager
from importlib import resources
from importlib.resources.abc import Traversable
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterator, Sequence


class CliError(Exception):
    """User-facing command error."""


def run_script(relative_path: str, args: Sequence[str]) -> int:
    with script_path(relative_path) as script:
        if not os.access(script, os.X_OK):
            raise CliError(f"compatibility script is not executable: {script}")

        completed = subprocess.run([str(script), *args], check=False)
    return completed.returncode


@contextmanager
def script_path(relative_path: str) -> Iterator[Path]:
    local_script = repo_root() / relative_path
    if local_script.exists():
        yield local_script
        return

    with tempfile.TemporaryDirectory(prefix="devcapsule-compat-") as temp_dir:
        temp_root = Path(temp_dir)
        extracted_root = temp_root / "docker4pycharm"
        extract_packaged_docker4pycharm(extracted_root)

        packaged_script = temp_root / relative_path
        if not packaged_script.exists():
            raise CliError(
                "compatibility script is missing from both the repository and "
                f"the packaged assets: {relative_path}"
            )

        yield packaged_script


def repo_root() -> Path:
    override = os.environ.get("DOCKER4IDES_REPO_ROOT")
    if override:
        return Path(override).expanduser().resolve()

    return Path(__file__).resolve().parents[2]


def extract_packaged_docker4pycharm(destination: Path) -> None:
    source = resources.files("devcapsule.assets.docker4pycharm")
    copy_resource_tree(source, destination)

    for script in destination.glob("*.sh"):
        script.chmod(script.stat().st_mode | 0o755)


def copy_resource_tree(source: Traversable, destination: Path) -> None:
    if source.is_dir():
        destination.mkdir(parents=True, exist_ok=True)
        for child in source.iterdir():
            if child.name == "__pycache__" or child.name.endswith(".pyc"):
                continue
            copy_resource_tree(child, destination / child.name)
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as input_file, destination.open("wb") as output_file:
        shutil.copyfileobj(input_file, output_file)
