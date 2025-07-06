"""TUI command for claude-code-autoyes."""

import click

# Import the modular TUI (now the only implementation)
from ..tui.app import run_tui


@click.command()
@click.option(
    "--debug", is_flag=True, help="Enable debug mode with performance monitoring"
)
def tui(debug: bool) -> None:
    """Launch interactive TUI."""
    run_tui(debug_mode=debug)
