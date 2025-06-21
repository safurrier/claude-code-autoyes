"""Disable all command for claude-code-autoyes."""

import click

from ..core import ConfigManager


@click.command("disable-all")
def disable_all() -> None:
    """Disable auto-yes for all Claude instances."""
    config = ConfigManager()
    config.disable_all()

    click.echo("Disabled auto-yes for all Claude instances.")
