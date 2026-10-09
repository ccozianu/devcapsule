"""Bounded extraction of whole toolchain archives without links or special files."""
from pathlib import Path, PurePosixPath
import shutil
import tarfile

from devcapsule.compat import CliError


def extract_tar_directory(archive: Path, destination: Path) -> Path:
    try:
        with tarfile.open(archive, "r:gz") as package:
            members = []
            size = 0
            for member in package:
                path = PurePosixPath(member.name)
                if (path.is_absolute() or ".." in path.parts or "\\" in member.name
                        or not (member.isfile() or member.isdir())):
                    raise CliError(f"Unsafe component tar entry: {member.name!r}")
                size += member.size
                members.append(member)
                if len(members) > 100_000 or size > 4 * 1024**3:
                    raise CliError("Component tar exceeds extraction limits.")
            if not members:
                raise CliError("Component tar is empty.")
            destination.mkdir(parents=True)
            for member in members:
                target = destination / member.name
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source = package.extractfile(member)
                    assert source is not None
                    with source, target.open("wb") as output:
                        shutil.copyfileobj(source, output)
                    target.chmod(0o755 if member.mode & 0o111 else 0o644)
    except (OSError, tarfile.TarError) as exc:
        raise CliError(f"Cannot extract verified component tar: {exc}") from exc
    return destination
