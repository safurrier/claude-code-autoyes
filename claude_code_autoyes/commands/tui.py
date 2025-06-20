"""TUI command for claude-code-autoyes."""

import click

from ..tui import ClaudeAutoYesApp


@click.command()
def tui():
    """Launch interactive TUI."""
    app = ClaudeAutoYesApp()
    app.run()
