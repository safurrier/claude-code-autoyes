"""Claude Code Auto-Yes - TUI for managing auto-yes across Claude instances.

A tool that automatically responds "yes" to prompts in Claude Code sessions
running in tmux. Provides both a TUI and CLI interface for managing which
sessions have auto-yes enabled.

The tool consists of:
- A detector that finds Claude instances in tmux panes
- A configuration manager for enabled sessions
- A daemon that monitors and responds to prompts
- CLI commands for control and status
- A TUI for interactive management
"""

__version__ = "0.1.0"
