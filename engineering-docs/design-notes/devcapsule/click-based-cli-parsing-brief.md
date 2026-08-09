# Class-Based Click CLI Architecture Brief

## Goal

Implement a Python command-line package using **Click** where:

- CLI parsing, help text, options, arguments, and validation are handled by Click.
- Each subcommand is implemented as its own class.
- Adding a new built-in command requires adding a new module/class only.
- `cli.py` or `main.py` should not need to be edited for every new command.
- Optional external plugin commands can be supported through Python package entry points.

## Recommended Architecture

Use this layered design:

```text
Click
  Provides parsing, help output, argument types, options, shell completion.

BaseCommand
  Project-level class abstraction for each subcommand.

AutoDiscoveryGroup
  Click group that discovers commands dynamically from modules.

Entry points, optional
  Plugin mechanism for external packages to register commands.
```

## Package Layout

Target structure:

```text
src/
  mytool/
    __init__.py
    cli.py
    commands/
      __init__.py
      base.py
      hello.py
      doctor.py
```

Replace `mytool` with the actual package name.

## Dependencies

Add Click to the project dependencies.

```toml
[project]
dependencies = [
    "click>=8.1",
]

[project.scripts]
mytool = "mytool.cli:main"
```

The console script name, here `mytool`, should match the desired command name.

## Core Command Base Class

Create `src/mytool/commands/base.py`.

```python
from __future__ import annotations

from typing import Any, ClassVar

import click


class BaseCommand:
    """
    Base class for class-based Click subcommands.

    Subclasses declare:
      - name
      - help
      - params
      - run()
    """

    name: ClassVar[str]
    help: ClassVar[str] = ""
    short_help: ClassVar[str | None] = None
    params: ClassVar[list[click.Parameter]] = []

    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)

    @classmethod
    def to_click_command(cls) -> click.Command:
        def callback(**kwargs: Any) -> Any:
            command = cls(**kwargs)
            return command.run()

        return click.Command(
            name=cls.name,
            callback=callback,
            params=cls.params,
            help=cls.help,
            short_help=cls.short_help,
        )

    def run(self) -> Any:
        raise NotImplementedError
```

## Built-In Command Discovery

Create `src/mytool/cli.py`.

```python
from __future__ import annotations

import importlib
import pkgutil

import click

import mytool.commands
from mytool.commands.base import BaseCommand


class AutoDiscoveryGroup(click.Group):
    """
    Click group that discovers built-in commands from mytool.commands.* modules.

    Each command module must expose:

        COMMAND = SomeBaseCommandSubclass
    """

    def list_commands(self, ctx: click.Context) -> list[str]:
        commands: list[str] = []

        for module_info in pkgutil.iter_modules(mytool.commands.__path__):
            module_name = module_info.name

            if module_name.startswith("_") or module_name == "base":
                continue

            commands.append(module_name.replace("_", "-"))

        return sorted(commands)

    def get_command(self, ctx: click.Context, name: str) -> click.Command | None:
        module_name = name.replace("-", "_")
        import_path = f"mytool.commands.{module_name}"

        try:
            module = importlib.import_module(import_path)
        except ModuleNotFoundError:
            return None

        command_class = getattr(module, "COMMAND", None)

        if command_class is None:
            raise click.ClickException(
                f"Command module {import_path!r} does not define COMMAND."
            )

        if not issubclass(command_class, BaseCommand):
            raise click.ClickException(
                f"{import_path}.COMMAND must be a BaseCommand subclass."
            )

        return command_class.to_click_command()


@click.command(cls=AutoDiscoveryGroup)
def cli() -> None:
    """Main command group for the tool."""


def main() -> None:
    cli()
```

## Example Command

Create `src/mytool/commands/hello.py`.

```python
from __future__ import annotations

import click

from mytool.commands.base import BaseCommand


class HelloCommand(BaseCommand):
    name = "hello"
    help = "Print a greeting."

    params = [
        click.Argument(["name"]),
        click.Option(
            ["--loud", "-l"],
            is_flag=True,
            help="Print the greeting in uppercase.",
        ),
        click.Option(
            ["--times", "-n"],
            type=int,
            default=1,
            show_default=True,
            help="Number of times to print the greeting.",
        ),
    ]

    def run(self) -> int:
        message = f"Hello, {self.name}!"

        if self.loud:
            message = message.upper()

        for _ in range(self.times):
            click.echo(message)

        return 0


COMMAND = HelloCommand
```

Expected usage:

```bash
mytool hello Costin
mytool hello Costin --loud
mytool hello Costin --times 3
```

## Adding Another Command

To add a new command, create a new file under `src/mytool/commands/`.

Example: `src/mytool/commands/doctor.py`.

```python
from __future__ import annotations

import click

from mytool.commands.base import BaseCommand


class DoctorCommand(BaseCommand):
    name = "doctor"
    help = "Check local environment health."

    params = [
        click.Option(
            ["--verbose", "-v"],
            is_flag=True,
            help="Show detailed diagnostics.",
        ),
    ]

    def run(self) -> int:
        click.echo("Checking environment...")

        if self.verbose:
            click.echo("Python: OK")
            click.echo("Config: OK")
            click.echo("Plugins: OK")

        return 0


COMMAND = DoctorCommand
```

Expected usage:

```bash
mytool doctor
mytool doctor --verbose
```

No changes to `cli.py` should be required.

## Optional External Plugin Support

If plugin support is desired, external packages should declare commands using Python package entry points.

Example plugin `pyproject.toml`:

```toml
[project.entry-points."mytool.commands"]
deploy = "mytool_deploy.commands:DeployCommand"
```

Then update `AutoDiscoveryGroup` to merge built-in commands and entry-point commands.

```python
from importlib.metadata import entry_points
```

Suggested implementation:

```python
class AutoDiscoveryGroup(click.Group):
    def list_commands(self, ctx: click.Context) -> list[str]:
        builtins = {
            module_info.name.replace("_", "-")
            for module_info in pkgutil.iter_modules(mytool.commands.__path__)
            if not module_info.name.startswith("_")
            and module_info.name != "base"
        }

        plugins = {
            ep.name
            for ep in entry_points(group="mytool.commands")
        }

        return sorted(builtins | plugins)

    def get_command(self, ctx: click.Context, name: str) -> click.Command | None:
        for ep in entry_points(group="mytool.commands"):
            if ep.name == name:
                command_class = ep.load()

                if not issubclass(command_class, BaseCommand):
                    raise click.ClickException(
                        f"Entry point {ep.name!r} is not a BaseCommand subclass."
                    )

                return command_class.to_click_command()

        module_name = name.replace("-", "_")
        import_path = f"mytool.commands.{module_name}"

        try:
            module = importlib.import_module(import_path)
        except ModuleNotFoundError:
            return None

        command_class = getattr(module, "COMMAND", None)

        if command_class is None:
            raise click.ClickException(
                f"Command module {import_path!r} does not define COMMAND."
            )

        if not issubclass(command_class, BaseCommand):
            raise click.ClickException(
                f"{import_path}.COMMAND must be a BaseCommand subclass."
            )

        return command_class.to_click_command()
```

## Command Authoring Rules

Each command module should:

1. Define one command class.
2. Subclass `BaseCommand`.
3. Declare `name`.
4. Declare `help`.
5. Declare `params` using Click-native `click.Argument` and `click.Option`.
6. Implement `run(self)`.
7. Export the command class as `COMMAND`.

Example pattern:

```python
class SomeCommand(BaseCommand):
    name = "some-command"
    help = "Do something useful."

    params = [
        click.Option(["--flag"], is_flag=True, help="Example flag."),
    ]

    def run(self) -> int:
        ...
        return 0


COMMAND = SomeCommand
```

## Design Notes

This approach intentionally avoids Click decorators as the main abstraction.

Instead of:

```python
@click.command()
@click.option("--flag")
def command(flag: bool) -> None:
    ...
```

Use:

```python
class SomeCommand(BaseCommand):
    params = [
        click.Option(["--flag"], is_flag=True),
    ]

    def run(self) -> int:
        ...
```

Benefits:

- Subcommands are classes.
- Commands can have constructor state.
- Parsing behavior remains Click-native.
- Help output remains Click-native.
- Adding commands does not require editing the central CLI file.
- External plugins can be added later without redesigning the CLI.

## Acceptance Criteria

A code agent should verify:

- `mytool --help` lists discovered commands.
- `mytool hello --help` shows command-specific options and arguments.
- `mytool hello Costin` prints `Hello, Costin!`.
- `mytool hello Costin --loud` prints uppercase output.
- Adding `commands/doctor.py` automatically enables `mytool doctor`.
- `cli.py` does not require modification when adding a new built-in command.
- Invalid command modules produce a useful Click error.
- Optional plugin commands can be discovered through the `mytool.commands` entry-point group if that feature is enabled.

## Testing Suggestions

Use Click's test runner.

```python
from click.testing import CliRunner

from mytool.cli import cli


def test_hello_command() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["hello", "Costin"])

    assert result.exit_code == 0
    assert "Hello, Costin!" in result.output


def test_hello_loud() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["hello", "Costin", "--loud"])

    assert result.exit_code == 0
    assert "HELLO, COSTIN!" in result.output


def test_help_lists_commands() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "hello" in result.output
```

## Final Recommendation

Implement the CLI using:

- `click.Command`
- `click.Group`
- a custom `AutoDiscoveryGroup`
- a project-specific `BaseCommand`
- one module per command
- optional package entry points for plugin commands

This gives the project class-based, declarative, extensible CLI behavior while still relying on Click for the hard parts of command-line parsing and help generation.
