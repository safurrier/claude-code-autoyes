# Claude Code Auto-Yes

Automatically respond to Claude Code prompts in tmux sessions. No more manual clicking - stay focused on your work.

## The Problem

Claude Code frequently asks "Do you want to continue?" and similar confirmation prompts. These interruptions break your flow, and you sometimes miss prompts when stepping away from your screen.

## The Solution

Claude Code Auto-Yes watches your tmux sessions and automatically responds to these prompts. When Claude asks "Do you want to continue?", the tool sends "yes" for you. When it asks "Proceed?", you get automatic confirmation.

You stay in control:
- Enable auto-yes for sessions where you want full automation
- Leave it disabled when you need to review each step carefully
- Toggle specific Claude instances on or off through a simple interface

## Quick Start

The fastest way to get running:

```bash
# Install the tool
uv tool install git+https://github.com/safurrier/claude-code-autoyes.git

# Check what Claude sessions are running
claude-code-autoyes status

# Enable auto-yes for all of them
claude-code-autoyes enable-all

# Start the background daemon
claude-code-autoyes daemon start
```

Now when Claude prompts you, the tool automatically responds. To see everything in action, launch the interactive interface:

```bash
claude-code-autoyes
```

## What You Get

**Visual Control**: An interactive terminal interface showing all your Claude instances with real-time status updates.

**Smart Detection**: Automatically finds Claude Code processes running in tmux panes without any configuration.

**Selective Automation**: Enable auto-yes for some sessions while keeping manual control over others.

**Background Monitoring**: A daemon that watches enabled sessions and responds to prompts even when you're not looking.

**Multiple Themes**: Choose from 11 beautiful color schemes including Dracula, Nord, and Gruvbox.

**Quick Navigation**: Jump mode lets you navigate the entire interface with single keystrokes.

## How It Works

The tool scans your tmux sessions looking for processes with "claude" in the name. For each Claude instance it finds, it can monitor that tmux pane for specific prompt patterns:

- "Do you want to"
- "Would you like to"
- "Proceed?"
- "❯ 1. Yes"

When one of these patterns appears in an enabled session, the daemon automatically sends an "Enter" keypress to that tmux pane. It's that straightforward.

## Beyond the Basics

Once you're comfortable with the basics, you can:

- **Fine-tune control** by enabling only specific Claude instances instead of all of them
- **Use keyboard shortcuts** to instantly toggle sessions (press 1-9 for quick access)
- **Monitor daemon logs** if something isn't working as expected
- **Try different themes** to match your terminal setup

The tool includes comprehensive commands for every scenario, from quick status checks to detailed daemon management.

## Getting Help

- **Quick reference**: Run `claude-code-autoyes --help` to see all available commands
- **Detailed guides**: Check the [Getting Started](getting-started.md) page for step-by-step instructions
- **Development info**: See [Development](development.md) if you want to contribute or modify the tool

## Installation Options

**Global tool** (recommended):
```bash
uv tool install git+https://github.com/safurrier/claude-code-autoyes.git
```

**Run without installing**:
```bash
git clone https://github.com/safurrier/claude-code-autoyes.git
cd claude-code-autoyes
uv run claude_code_autoyes.py
```

**Development setup**:
```bash
git clone https://github.com/safurrier/claude-code-autoyes.git
cd claude-code-autoyes
make setup
```

## Requirements

- **tmux** - This tool only works with Claude Code running in tmux sessions. [Install tmux](https://github.com/tmux/tmux/wiki/Installing) if you don't have it.
- **Python 3.9+**
- **Claude Code** running in tmux panes

**Important**: Claude Code must be running inside tmux sessions for this tool to detect and monitor it.

That's it. No complex setup, no configuration files, no database backends.

## License

MIT License - use it however you want.