"""Project configuration: declarations, local decisions and resolved plans.

The value API is Configuration, Resolution, ConfigurationReview and HostAccess.
The model depends on assessment and resolution, which depend on node domains
and document codecs. Core modules never import execution, storage, operations,
CLI commands or launch adapters.

File adapters live in storage/execution, lifecycle orchestration in operations,
and successful-run snapshots in history. These are separate from the value API.
"""
from .documents import ProjectConfigurationError
from .model import Configuration
from .resolution import Resolution
from .review import ConfigurationReview, HostAccess

__all__ = ["Configuration", "Resolution", "ConfigurationReview", "HostAccess", "ProjectConfigurationError"]
