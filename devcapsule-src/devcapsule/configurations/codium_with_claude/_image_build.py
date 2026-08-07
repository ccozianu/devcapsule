"""VSCodium plus Claude Code image-build composition."""

from __future__ import annotations

import contextlib
import os
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path

from devcapsule.compat import CliError
from devcapsule.image_build import (
    AptPackagesComponent,
    BaseImageComponent,
    BuildComponent,
    BuildxImageBuilder,
    DirectoryComponent,
    EntrypointComponent,
    EnvComponent,
    ExecComponent,
    FileComponent,
    ImageBuildSpec,
    LabelComponent,
    resource_to_tempdir,
)
from devcapsule.image_tooling import NODE_CURRENT_BIN, node_tooling_component

DEFAULT_BASE_IMAGE = "ubuntu:24.04"
DEFAULT_IMAGE = "codium-with-claude:latest"


@dataclass(frozen=True)
class CodiumImageBuildOptions:
    image: str = DEFAULT_IMAGE
    base_image: str = DEFAULT_BASE_IMAGE
    network: str = "default"
    extra_apt_packages: tuple[str, ...] = ()
    ide_archive: Path | None = None


def parse_codium_build_options(
    *,
    image: str,
    base_image: str,
    network: str,
    extra_apt_packages: tuple[str, ...],
    ide_archive: Path | None,
) -> CodiumImageBuildOptions:
    resolved_archive = ide_archive.expanduser().resolve() if ide_archive is not None else None
    if resolved_archive is not None and not resolved_archive.is_file():
        raise CliError(f"VSCodium IDE archive does not exist or is not a file: {resolved_archive}")
    return CodiumImageBuildOptions(
        image=image,
        base_image=base_image,
        network=network,
        extra_apt_packages=extra_apt_packages,
        ide_archive=resolved_archive,
    )


def build_codium_image(options: CodiumImageBuildOptions, builder: BuildxImageBuilder | None = None) -> int:
    builder = builder or BuildxImageBuilder()
    with contextlib.ExitStack() as stack:
        assets = Path(stack.enter_context(resource_to_tempdir("devcapsule.assets.codium_with_claude")))
        codium_root = None
        if options.ide_archive is not None:
            extract_root = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="devcapsule-codium-archive-")))
            codium_root = normalize_codium_archive(options.ide_archive, extract_root)
        builder.build(
            build_codium_image_spec(options, assets_root=assets, codium_root=codium_root),
            network=options.network,
        )
    return 0


def normalize_codium_archive(archive_path: Path, destination: Path) -> Path:
    try:
        with tarfile.open(archive_path, "r:*") as archive:
            archive.extractall(destination, filter="data")
    except (tarfile.TarError, OSError) as exc:
        raise CliError(f"Could not extract VSCodium IDE archive {archive_path}: {exc}") from exc

    launchers = sorted(destination.glob("**/bin/codium"))
    if not launchers:
        raise CliError("The supplied VSCodium IDE archive does not contain bin/codium")
    if len(launchers) > 1:
        raise CliError("The supplied VSCodium IDE archive contains multiple bin/codium launchers")
    launcher = launchers[0]
    if not launcher.is_file() or not os.access(launcher, os.X_OK):
        raise CliError("The supplied VSCodium IDE archive does not contain executable bin/codium")
    return launcher.parent.parent


def build_codium_image_spec(
    options: CodiumImageBuildOptions,
    *,
    assets_root: Path,
    codium_root: Path | None = None,
) -> ImageBuildSpec:
    packages = (
        "ca-certificates",
        "curl",
        "git",
        "gnupg",
        "xz-utils",
        "openssh-client",
        "python3.12",
        "python3.12-dev",
        "python3.12-venv",
        "python3-pip",
        "python-is-python3",
        "build-essential",
        "ripgrep",
        "strace",
        "sudo",
        "gosu",
        "tini",
        "xterm",
        "libasound2t64",
        "libatk-bridge2.0-0",
        "libatk1.0-0",
        "libcairo2",
        "libdrm2",
        "libgbm1",
        "libglib2.0-0",
        "libgtk-3-0",
        "libnspr4",
        "libnss3",
        "libpango-1.0-0",
        "libx11-6",
        "libxcb1",
        "libxcomposite1",
        "libxdamage1",
        "libxext6",
        "libxfixes3",
        "libxkbcommon0",
        "libxkbfile1",
        "libxrandr2",
        "libxshmfence1",
        "xdg-utils",
    ) + options.extra_apt_packages
    codium_repository_lines = """
install -d -m 0755 /etc/apt/keyrings
curl -fsSL https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg \
  | gpg --dearmor -o /etc/apt/keyrings/vscodium-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/vscodium-archive-keyring.gpg] https://download.vscodium.com/debs vscodium main" > /etc/apt/sources.list.d/vscodium.list
""".strip().splitlines()
    install_lines: list[str] = []
    if codium_root is None:
        install_lines.extend(codium_repository_lines)
        install_lines.extend(
            (
                "apt-get update",
                "apt-get install -y --no-install-recommends codium",
            )
        )
    components: list[BuildComponent] = [
        BaseImageComponent(options.base_image),
        AptPackagesComponent(packages),
    ]
    if codium_root is not None:
        components.extend(
            (
                DirectoryComponent(codium_root, "/opt/codium"),
                ExecComponent(
                    (
                        "bash",
                        "-euxo",
                        "pipefail",
                        "-c",
                        "if [[ ! -f /opt/codium/chrome-sandbox ]]; then "
                        "echo 'VSCodium archive is missing /opt/codium/chrome-sandbox' >&2; exit 1; fi; "
                        "chown root:root /opt/codium/chrome-sandbox; "
                        "chmod 4755 /opt/codium/chrome-sandbox",
                    )
                ),
                ExecComponent(("ln", "-s", "/opt/codium/bin/codium", "/usr/local/bin/codium")),
            )
        )
    components.extend((
        *(
            (
                ExecComponent(("bash", "-euxo", "pipefail", "-c", "\n".join(install_lines))),
            )
            if install_lines
            else ()
        ),
        node_tooling_component(),
        ExecComponent(
            (
                "bash",
                "-euxo",
                "pipefail",
                "-c",
                "python3.12 --version\n"
                "codium --no-sandbox --user-data-dir=/tmp/codium-version-check --version",
            )
        ),
        ExecComponent(
            (
                "ln",
                "-s",
                "/opt/codium/codium" if codium_root is not None else "/usr/share/codium/codium",
                "/usr/local/bin/codium-foreground",
            )
        ),
        FileComponent(assets_root / "entrypoint.sh", "/usr/local/bin/codium-entrypoint", permissions=0o755),
        ExecComponent(("mkdir", "-p", "/workspace/project", "/ide-global-settings", "/ide-project-state")),
        EnvComponent(
            (
                ("PATH", f"{NODE_CURRENT_BIN}:${{PATH}}"),
                ("PROJECT_PATH", "/workspace/project"),
                ("IDE_GLOBAL_SETTINGS_PATH", "/ide-global-settings"),
                ("IDE_PROJECT_STATE_PATH", "/ide-project-state"),
                ("HOME", "/ide-global-settings/home"),
                ("XDG_CONFIG_HOME", "/ide-global-settings/home/.config"),
                ("XDG_DATA_HOME", "/ide-global-settings/home/.local/share"),
                ("XDG_CACHE_HOME", "/ide-project-state/home/.cache"),
            )
        ),
        LabelComponent(
            (
                ("devcapsule.configuration", "codium_with_claude"),
                ("devcapsule.ide", "vscodium"),
                ("devcapsule.agent", "claude-code"),
                ("devcapsule.builder", "python-on-whales"),
            )
        ),
        EntrypointComponent(("/usr/bin/tini", "--", "/usr/local/bin/codium-entrypoint")),
    ))
    return ImageBuildSpec(image=options.image, base_image=options.base_image, components=tuple(components))
