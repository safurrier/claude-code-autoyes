"""Daemon management commands for claude-code-autoyes."""

import click

from ..core.config import ConfigManager
from ..core.daemon import DaemonManager


@click.group()
def daemon() -> None:
    """Manage the auto-yes daemon."""
    pass


@daemon.command()
def start() -> None:
    """Start the auto-yes daemon."""
    config = ConfigManager()
    daemon_manager = DaemonManager()

    if daemon_manager.is_running():
        click.echo("✓ Daemon: Already running")
        return

    if daemon_manager.start(config):
        click.echo("✓ Daemon: Started successfully")
    else:
        click.echo("✗ Daemon: Failed to start")
        raise click.ClickException("Failed to start daemon")


@daemon.command()
def stop() -> None:
    """Stop the auto-yes daemon."""
    daemon_manager = DaemonManager()

    if not daemon_manager.is_running():
        click.echo("✓ Daemon: Not running")
        return

    if daemon_manager.stop():
        click.echo("✓ Daemon: Stopped successfully")
    else:
        click.echo("✗ Daemon: Failed to stop")
        raise click.ClickException("Failed to stop daemon")


@daemon.command()
def status() -> None:
    """Show daemon status."""
    daemon_manager = DaemonManager()
    click.echo(daemon_manager.get_status())


@daemon.command()
def restart() -> None:
    """Restart the auto-yes daemon."""
    daemon_manager = DaemonManager()
    config = ConfigManager()

    # Stop if running
    if daemon_manager.is_running():
        if not daemon_manager.stop():
            click.echo("✗ Daemon: Failed to stop")
            raise click.ClickException("Failed to stop daemon")
        click.echo("✓ Daemon: Stopped")

    # Start
    if daemon_manager.start(config):
        click.echo("✓ Daemon: Started successfully")
    else:
        click.echo("✗ Daemon: Failed to start")
        raise click.ClickException("Failed to start daemon")
