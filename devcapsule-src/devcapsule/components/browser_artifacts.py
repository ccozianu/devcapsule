"""Bounded ZIP extraction and offline Python wheel installation for components."""

from pathlib import Path, PurePosixPath
import re
import shutil
import stat
from urllib.parse import urlsplit
import zipfile

from devcapsule.compat import CliError
from devcapsule.images.build import shell_quote


def wheel_name(url: str) -> str:
    name = urlsplit(url).path.rsplit("/", 1)[-1]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.+-]*\.whl", name):
        raise CliError("A python-wheel artifact URL must end in a wheel filename.")
    return name


def extract_zip(archive: Path, destination: Path) -> Path:
    """Extract regular files only; never follow archive links or escape the root."""
    try:
        with zipfile.ZipFile(archive) as package:
            members = package.infolist()
            if not members or len(members) > 100_000 or sum(m.file_size for m in members) > 2 * 1024**3:
                raise CliError("Browser ZIP exceeds extraction limits or is empty.")
            for member in members:
                path = PurePosixPath(member.filename)
                mode = member.external_attr >> 16
                if (path.is_absolute() or ".." in path.parts or "\\" in member.filename
                        or stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR))):
                    raise CliError(f"Unsafe browser ZIP entry: {member.filename!r}")
            destination.mkdir(parents=True)
            for member in members:
                target = destination / member.filename
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with package.open(member) as source, target.open("wb") as output:
                        shutil.copyfileobj(source, output)
                    target.chmod(0o755 if (member.external_attr >> 16) & 0o111 else 0o644)
    except (OSError, zipfile.BadZipFile) as exc:
        raise CliError(f"Cannot extract verified browser ZIP: {exc}") from exc
    return destination


def wheel_install_step(destination: str, names: tuple[str, ...]) -> tuple[str, ...]:
    """Build an isolated environment with only the acquired, verified wheels."""
    venv = shell_quote(destination + "/venv")
    wheels = " ".join(shell_quote(destination + "/wheels/" + name) for name in names)
    return ("sh", "-ec", f"python3 -m venv {venv}; {venv}/bin/python -m pip install "
            f"--no-index --no-deps --no-cache-dir --disable-pip-version-check {wheels}")
