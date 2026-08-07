"""Run the isolated contributor bootstrap inside a disposable base container.

The outer E2E test supplies only one owned workspace at ``/e2e``.  This driver
uses the base image's system Python and never needs the current development
container, its virtual environment, its credentials, or its Docker socket.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Mapping, Sequence


SYSTEM_PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
PINNED_REQUIREMENT = re.compile(r"([A-Za-z0-9_.-]+)==([^\s;]+)")


class BootstrapFailure(RuntimeError):
    """The disposable contributor environment violated its contract."""


class ContributorBootstrap:
    """Small bootstrap operations whose evidence is checked by the outer E2E."""

    def __init__(self, run_root: Path) -> None:
        self.run_root = run_root.resolve(strict=True)
        self.checkout = self.run_root / "checkout"
        self.package_root = self.checkout / "devcapsule"
        self.contributor_root = self.run_root / "contributor"
        self.home = self.contributor_root / "home"
        self.venv = self.contributor_root / "venv"
        self.venv_python = self.venv / "bin/python3.12"
        self.evidence_path = self.run_root / "contributor-bootstrap.json"

    def create_private_layout(self) -> None:
        for directory in (self.contributor_root, self.home):
            directory.mkdir(mode=0o700, parents=True, exist_ok=False)
            directory.chmod(0o700)

    def bootstrap_environment(self) -> dict[str, str]:
        # This is intentionally an allowlist.  Package installation cannot see
        # the launching contributor's pip config, private indexes, credentials,
        # Python path, user site, SSH agent, cloud tokens, or Docker endpoint.
        environment = {
            "PATH": f"{self.venv}/bin:{SYSTEM_PATH}",
            "HOME": str(self.home),
            "XDG_CONFIG_HOME": str(self.run_root / "xdg/config"),
            "XDG_CACHE_HOME": str(self.run_root / "xdg/cache"),
            "XDG_DATA_HOME": str(self.run_root / "xdg/data"),
            "XDG_STATE_HOME": str(self.run_root / "xdg/state"),
            "XDG_RUNTIME_DIR": str(self.run_root / "xdg/runtime"),
            "PIP_CONFIG_FILE": "/dev/null",
            "PIP_CACHE_DIR": str(self.run_root / "xdg/cache/pip"),
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_INPUT": "1",
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
        }
        # A credential-free proxy may be necessary on an otherwise public
        # network.  The outer launcher has already rejected URL userinfo.
        for name in ("HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY"):
            value = os.environ.get(name)
            if value:
                environment[name] = value
        return environment

    def create_venv(self, environment: Mapping[str, str]) -> None:
        system_python = Path(sys.executable).resolve(strict=True)
        if system_python != Path("/usr/bin/python3.12"):
            raise BootstrapFailure(
                f"bootstrap must use /usr/bin/python3.12, found {system_python}"
            )
        self._run(
            [str(system_python), "-m", "venv", "--copies", str(self.venv)],
            environment,
        )
        if self.venv_python.is_symlink() or not stat.S_ISREG(
            self.venv_python.lstat().st_mode
        ):
            raise BootstrapFailure("venv python3.12 is not an independent copied file")

    def install_locked_dependencies(self, environment: Mapping[str, str]) -> None:
        self._run(
            [
                str(self.venv_python),
                "-m",
                "pip",
                "install",
                "--requirement",
                str(self.package_root / "dev-requirements.txt"),
            ],
            environment,
        )

    def install_editable_package(self, environment: Mapping[str, str]) -> None:
        self._run(
            [
                str(self.venv_python),
                "-m",
                "pip",
                "install",
                "--editable",
                str(self.package_root),
                "--no-deps",
            ],
            environment,
        )

    def python_identity(
        self,
        executable: Path,
        environment: Mapping[str, str],
    ) -> Mapping[str, object]:
        script = (
            "import json,platform,sys;"
            "print(json.dumps({'executable':sys.executable,'implementation':"
            "platform.python_implementation(),'version':platform.python_version(),"
            "'prefix':sys.prefix,'base_prefix':sys.base_prefix},sort_keys=True))"
        )
        value = json.loads(
            self._run([str(executable), "-c", script], environment).stdout
        )
        if not isinstance(value, dict):
            raise BootstrapFailure("Python identity probe returned a non-object")
        return value

    def package_versions(
        self,
        environment: Mapping[str, str],
    ) -> dict[str, str]:
        value = json.loads(
            self._run(
                [str(self.venv_python), "-m", "pip", "list", "--format=json"],
                environment,
            ).stdout
        )
        if not isinstance(value, list):
            raise BootstrapFailure("pip package inventory returned a non-list")
        versions: dict[str, str] = {}
        for item in value:
            if not isinstance(item, dict):
                raise BootstrapFailure("pip package inventory contains a non-object")
            name = item.get("name")
            version = item.get("version")
            if not isinstance(name, str) or not isinstance(version, str):
                raise BootstrapFailure("pip package inventory contains malformed values")
            versions[self._normalize_package(name)] = version
        return versions

    def verify_locked_versions(self, versions: Mapping[str, str]) -> None:
        expected = self._locked_versions(self.package_root / "dev-requirements.txt")
        for package in ("nox", "pex", "wheel"):
            if versions.get(package) != expected.get(package):
                raise BootstrapFailure(
                    f"{package} does not match the committed development lock"
                )
        if "pip" not in versions:
            raise BootstrapFailure("the contributor venv has no pip installation")

    def verify_import_isolation(
        self,
        environment: Mapping[str, str],
    ) -> Mapping[str, object]:
        script = (
            "import devcapsule,json,sys;"
            "print(json.dumps({'module_file':devcapsule.__file__,"
            "'executable':sys.executable,'prefix':sys.prefix,"
            "'base_prefix':sys.base_prefix,'sys_path':sys.path},sort_keys=True))"
        )
        value = json.loads(
            self._run([str(self.venv_python), "-c", script], environment).stdout
        )
        if not isinstance(value, dict):
            raise BootstrapFailure("import isolation probe returned a non-object")

        module_file = self._required_string(value, "module_file")
        executable = self._required_string(value, "executable")
        prefix = self._required_string(value, "prefix")
        base_prefix = self._required_string(value, "base_prefix")
        expected_module_root = (self.package_root / "devcapsule").resolve(strict=True)
        if not Path(module_file).resolve(strict=True).is_relative_to(expected_module_root):
            raise BootstrapFailure("devcapsule import did not resolve beneath the clean clone")
        if Path(executable).resolve(strict=True) != self.venv_python.resolve(strict=True):
            raise BootstrapFailure("import probe did not use the contributor venv Python")
        if Path(prefix).resolve(strict=True) != self.venv.resolve(strict=True):
            raise BootstrapFailure("import probe has the wrong contributor prefix")
        if Path(base_prefix).resolve(strict=True) == self.venv.resolve(strict=True):
            raise BootstrapFailure("contributor venv did not retain a distinct base prefix")

        raw_sys_path = value.get("sys_path")
        if not isinstance(raw_sys_path, list) or not all(
            isinstance(item, str) for item in raw_sys_path
        ):
            raise BootstrapFailure("import probe returned a malformed sys.path")
        allowed_roots = (self.run_root, Path("/usr"))
        for item in raw_sys_path:
            if not item:
                continue
            selected = Path(item).resolve(strict=False)
            if not any(
                selected == root or selected.is_relative_to(root)
                for root in allowed_roots
            ):
                raise BootstrapFailure(f"sys.path escaped contributor isolation: {selected}")
        return value

    def write_evidence(self, value: Mapping[str, object]) -> None:
        descriptor = os.open(
            self.evidence_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        self.evidence_path.chmod(0o600)

    @staticmethod
    def _run(
        command: Sequence[str],
        environment: Mapping[str, str],
    ) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            env=dict(environment),
        )
        if completed.returncode != 0:
            raise BootstrapFailure(
                f"bootstrap command failed with exit {completed.returncode}: "
                f"{' '.join(command)}\nstdout: {completed.stdout.strip()}\n"
                f"stderr: {completed.stderr.strip()}"
            )
        return completed

    @classmethod
    def _locked_versions(cls, path: Path) -> dict[str, str]:
        versions: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            match = PINNED_REQUIREMENT.fullmatch(line.strip())
            if match is not None:
                versions[cls._normalize_package(match.group(1))] = match.group(2)
        return versions

    @staticmethod
    def _normalize_package(value: str) -> str:
        return re.sub(r"[-_.]+", "-", value).lower()

    @staticmethod
    def _required_string(value: Mapping[str, object], name: str) -> str:
        selected = value.get(name)
        if not isinstance(selected, str) or not selected:
            raise BootstrapFailure(f"import probe has no valid {name}")
        return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    arguments = parser.parse_args()

    bootstrap = ContributorBootstrap(arguments.run_root)
    bootstrap.create_private_layout()
    environment = bootstrap.bootstrap_environment()
    bootstrap.create_venv(environment)
    system_identity = bootstrap.python_identity(Path(sys.executable), environment)
    venv_identity = bootstrap.python_identity(bootstrap.venv_python, environment)
    initial_versions = bootstrap.package_versions(environment)
    bootstrap.install_locked_dependencies(environment)
    bootstrap.install_editable_package(environment)
    final_versions = bootstrap.package_versions(environment)
    bootstrap.verify_locked_versions(final_versions)
    import_probe = bootstrap.verify_import_isolation(environment)
    bootstrap.write_evidence(
        {
            "schema_version": 1,
            "system_python": system_identity,
            "venv_python": venv_identity,
            "initial_packages": initial_versions,
            "final_packages": final_versions,
            "import_probe": import_probe,
            "environment_names": sorted(environment),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
