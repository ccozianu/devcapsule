"""Shared runtime path and mount planning for IDE launchers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from .project import ProjectPlan, plan_project


@dataclass(frozen=True)
class SharedRuntimeOptions:
    project: Path
    profile: str | None = None
    global_settings: str | Path | None = None
    project_state: str | Path | None = None
    project_state_root: str | Path | None = None
    project_mount: str | None = None


@dataclass(frozen=True)
class SharedRuntimePlan:
    project: Path
    project_id: str
    project_mount: str
    profile_root: Path | None
    global_settings: Path
    project_state: Path


def resolve_existing_or_create(path: str | Path) -> Path:
    resolved = Path(path).expanduser()
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved.resolve()


def resolve_profile_root(
    profile: str,
    env: Mapping[str, str],
    *,
    explicit_root_env_var: str,
    default_prefix: str,
) -> Path:
    if any(separator in profile for separator in ("/", "\\")) or profile in {".", ".."}:
        raise ValueError("--profile must be a simple profile name, not a path.")

    explicit_root = env.get(explicit_root_env_var, "")
    if explicit_root:
        return Path(explicit_root).expanduser()

    config_home = Path(env.get("XDG_CONFIG_HOME") or Path(env.get("HOME", "~")).expanduser() / ".config")
    return config_home / f"{default_prefix}{profile}"


def project_state_from_root(root: str | Path | None, project: Path) -> Path | None:
    if not root:
        return None

    state_root = Path(root).expanduser().resolve(strict=False)
    project = project.resolve(strict=False)
    try:
        relative_project = project.relative_to(state_root.parent)
    except ValueError:
        relative_project = Path(project.name)
    return state_root / relative_project


def plan_shared_runtime(
    options: SharedRuntimeOptions,
    env: Mapping[str, str],
    *,
    explicit_profile_root_env_var: str,
    profile_dir_prefix: str,
    default_global_settings: Path,
    default_project_state: Callable[[ProjectPlan], Path],
) -> SharedRuntimePlan:
    project_plan = plan_project(options.project, options.project_mount)
    profile_root = (
        resolve_profile_root(
            options.profile,
            env,
            explicit_root_env_var=explicit_profile_root_env_var,
            default_prefix=profile_dir_prefix,
        )
        if options.profile
        else None
    )
    global_settings = resolve_existing_or_create(options.global_settings or (profile_root / "state" if profile_root else default_global_settings))
    project_state = resolve_existing_or_create(
        options.project_state
        or project_state_from_root(options.project_state_root, project_plan.project_path)
        or default_project_state(project_plan)
    )
    return SharedRuntimePlan(
        project=project_plan.project_path,
        project_id=project_plan.project_id,
        project_mount=project_plan.project_mount,
        profile_root=profile_root,
        global_settings=global_settings,
        project_state=project_state,
    )
