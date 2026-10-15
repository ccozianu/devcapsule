"""Public names for the shipped in-capsule CLI."""

from enum import StrEnum


class RuntimeCommand(StrEnum):
    """Parse strings at configuration boundaries; carry members through image building.

    DEVELOPMENT reserves the usual command name for a development installation.
    Values are also the command names persisted in configuration and image identity.
    """

    STANDARD = "devcapsule"
    DEVELOPMENT = "devcapsule0"
