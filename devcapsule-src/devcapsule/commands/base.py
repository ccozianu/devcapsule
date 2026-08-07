"""Class-based Click command helpers."""

from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import Any, ClassVar

import click


class BaseCommand:
    """Base class for class-backed Click commands."""

    name: ClassVar[str]
    help: ClassVar[str] = ""
    short_help: ClassVar[str | None] = None
    params: ClassVar[list[click.Parameter]] = []
    context_settings: ClassVar[dict[str, Any] | None] = None
    hidden: ClassVar[bool] = False
    pass_context: ClassVar[bool] = False

    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)

    @classmethod
    def to_click_command(cls) -> click.Command:
        if cls.pass_context:

            @click.pass_context
            def callback(ctx: click.Context, **kwargs: Any) -> Any:
                return cls(ctx=ctx, **kwargs).run()

        else:

            def callback(**kwargs: Any) -> Any:
                return cls(**kwargs).run()

        return click.Command(
            name=cls.name,
            callback=callback,
            params=cls.params,
            help=cls.help,
            short_help=cls.short_help,
            context_settings=cls.context_settings,
            hidden=cls.hidden,
        )

    def run(self) -> Any:
        raise NotImplementedError


class DiscoveredCommandGroup(click.Group):
    """Click group that discovers commands from a package."""

    def __init__(self, *args: Any, package_name: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.package_name = package_name

    def list_commands(self, ctx: click.Context) -> list[str]:
        package = importlib.import_module(self.package_name)
        if not hasattr(package, "__path__"):
            return []

        commands: list[str] = []
        for module_info in pkgutil.iter_modules(package.__path__):
            module_name = module_info.name
            if module_name.startswith("_") or module_name == "base":
                continue
            import_path = f"{self.package_name}.{module_name}"
            module = importlib.import_module(import_path)
            command_class = command_from_module(module, import_path)
            if not command_class.hidden:
                commands.append(command_class.name)
        return sorted(commands)

    def get_command(self, ctx: click.Context, name: str) -> click.Command | None:
        module_name = name.replace("-", "_")
        import_path = f"{self.package_name}.{module_name}"
        try:
            module = importlib.import_module(import_path)
        except ModuleNotFoundError as exc:
            if exc.name == import_path:
                return None
            raise

        command_class = command_from_module(module, import_path)
        return command_class.to_click_command()


class BaseGroup(BaseCommand):
    """Base class for discovered Click command groups."""

    subcommand_package: ClassVar[str]

    @classmethod
    def to_click_command(cls) -> click.Command:
        return DiscoveredCommandGroup(
            name=cls.name,
            package_name=cls.subcommand_package,
            help=cls.help,
            short_help=cls.short_help,
            context_settings=cls.context_settings,
            hidden=cls.hidden,
            no_args_is_help=True,
        )


def command_from_module(module: ModuleType, import_path: str) -> type[BaseCommand]:
    command_class = getattr(module, "COMMAND", None)
    if command_class is None:
        raise click.ClickException(f"Command module {import_path!r} does not define COMMAND.")
    if not isinstance(command_class, type) or not issubclass(command_class, BaseCommand):
        raise click.ClickException(f"{import_path}.COMMAND must be a BaseCommand subclass.")
    return command_class
