"""Main CLI entry point for claude-code-autoyes."""

import click

from .commands import daemon, disable_all, enable_all, status, tui


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Interactive TUI for managing auto-yes across Claude instances in tmux."""
    if ctx.invoked_subcommand is None:
        # Default to TUI if no subcommand
        ctx.invoke(tui)


# Register subcommands
cli.add_command(status)
cli.add_command(enable_all)
cli.add_command(disable_all)
cli.add_command(tui)
cli.add_command(daemon)


if __name__ == "__main__":
    cli()
