"""TUI command for claude-code-autoyes."""

import click

# Import the modular TUI (now the only implementation)
from ..tui.app import run_tui


@click.command()
def tui() -> None:
    """Launch interactive TUI."""
    run_tui()
