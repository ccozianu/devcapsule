"""VS Code plus Claude IDE configuration."""

from __future__ import annotations

import click


class VscodeWithClaudeConfiguration:
    """WIP interface for the VS Code plus Claude proof-point configuration."""

    name = "vscode_with_claude"
    help = "WIP: VS Code plus Claude is registered but not implemented."
    ide = "vscode"
    agent = "claude"
    implemented = False

    def to_click_command(self) -> click.Command:
        group = click.Group(name=self.name, help=self.help, no_args_is_help=True)
        group.add_command(self.build_command())
        group.add_command(self.run_command())
        return group

    def build_command(self) -> click.Command:
        def callback() -> int:
            return self.build()

        return click.Command(
            name="build",
            callback=callback,
            help="Build the VS Code plus Claude image.",
        )

    def run_command(self) -> click.Command:
        def callback() -> int:
            return self.run()

        return click.Command(
            name="run",
            callback=callback,
            help="Launch the VS Code plus Claude configuration.",
        )

    def build(self) -> int:
        return self._not_implemented("build")

    def run(self) -> int:
        return self._not_implemented("run")

    def _not_implemented(self, command: str) -> int:
        raise click.ClickException(
            f"{self.name} {command} is registered as the next configuration module, "
            "but its Docker image and launcher are not implemented yet."
        )


__all__ = ["VscodeWithClaudeConfiguration"]
