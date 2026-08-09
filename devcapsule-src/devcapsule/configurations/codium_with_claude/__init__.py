"""VSCodium plus Claude Code configuration."""

from .configuration import CodiumWithClaudeConfiguration
from ._image_build import (
    CodiumImageBuildOptions,
    build_codium_image,
    build_codium_image_spec,
    normalize_codium_archive,
    parse_codium_build_options,
)
from ._launcher import CodiumRunOptions, build_codium_run_command, run_codium

__all__ = [
    "CodiumImageBuildOptions",
    "CodiumRunOptions",
    "CodiumWithClaudeConfiguration",
    "build_codium_image",
    "build_codium_image_spec",
    "build_codium_run_command",
    "run_codium",
    "normalize_codium_archive",
    "parse_codium_build_options",
]
