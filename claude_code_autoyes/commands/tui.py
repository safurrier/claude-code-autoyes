"""TUI command for claude-code-autoyes."""

import importlib.util

import click

# Import the tui module directly to avoid package/module conflicts
from ..tui.app import run_new_tui


@click.command()
@click.option(
    "--version",
    type=click.Choice(["original", "new"]),
    default="original",
    help="TUI version to launch (original or new)",
)
def tui(version: str) -> None:
    """Launch interactive TUI."""
    if version == "new":
        run_new_tui()
    else:
        # Import the original TUI module
        from pathlib import Path

        parent_dir = Path(__file__).parent.parent
        tui_module_path = parent_dir / "tui.py"

        spec = importlib.util.spec_from_file_location(
            "claude_code_autoyes.tui_original", tui_module_path
        )
        if spec is None or spec.loader is None:
            raise ImportError("Failed to load original TUI module")
        tui_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tui_module)

        app = tui_module.ClaudeAutoYesApp()
        app.run()
