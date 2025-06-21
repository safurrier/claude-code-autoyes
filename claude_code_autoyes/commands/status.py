"""Status command for claude-code-autoyes."""

import click

from ..core import ClaudeDetector, ConfigManager


@click.command()
def status() -> None:
    """Show current status of Claude instances."""
    detector = ClaudeDetector()
    config = ConfigManager()
    instances = detector.find_claude_instances()

    click.echo(f"Found {len(instances)} Claude instances:")
    for instance in instances:
        pane_id = f"{instance.session}:{instance.pane}"
        status_text = "ON" if config.is_enabled(pane_id) else "OFF"
        click.echo(f"  {pane_id} - [{status_text}]")
