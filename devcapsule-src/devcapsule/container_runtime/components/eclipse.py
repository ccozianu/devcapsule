"""Launch Eclipse in the foreground with a checkout-scoped workspace."""

from dataclasses import dataclass
from pathlib import Path

from ..contract import RuntimePlan, RuntimePlanError


@dataclass(frozen=True)
class EclipseLaunch:
    command: tuple[str, ...]


def plan(runtime: RuntimePlan) -> EclipseLaunch:
    config = runtime.component.configuration
    values: dict[str, str] = {}
    for name in ("installation_path", "launcher", "workspace_slot"):
        value = config.get(name)
        if not isinstance(value, str) or not value or any(c in value for c in "\x00\r\n"):
            raise RuntimePlanError(f"Eclipse {name} must be a non-empty one-line string")
        values[name] = value
    installation = Path(values["installation_path"])
    launcher = Path(values["launcher"])
    if not installation.is_absolute():
        raise RuntimePlanError("Eclipse installation_path must be absolute")
    if launcher.is_absolute() or ".." in launcher.parts:
        raise RuntimePlanError("Eclipse launcher must be relative to installation_path")
    workspace = runtime.slots_by_name().get(runtime.component.slot_name(values["workspace_slot"]))
    if workspace is None:
        raise RuntimePlanError("Eclipse workspace_slot must name a declared state slot")
    # Eclipse's native workspace lock protects concurrent access and is released
    # by the OS after a stopped/crashed process; never delete its .lock file.
    # Project import stays an IDE operation: do not write .project into user repos.
    return EclipseLaunch((str(installation / launcher), "-data", workspace))
