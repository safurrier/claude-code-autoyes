"""Enable all command for claude-code-autoyes."""

import click

from ..core import ClaudeDetector, ConfigManager


@click.command("enable-all")
def enable_all():
    """Enable auto-yes for all Claude instances."""
    detector = ClaudeDetector()
    config = ConfigManager()

    instances = detector.find_claude_instances()
    if not instances:
        click.echo("No Claude instances found.")
        return

    session_panes = [f"{inst.session}:{inst.pane}" for inst in instances]
    config.enable_all(session_panes)

    click.echo(f"Enabled auto-yes for {len(instances)} Claude instances.")
