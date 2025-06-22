# Claude Code Auto-Yes

Stop clicking "yes" on every Claude Code prompt. This tool monitors your tmux sessions and automatically responds to confirmation prompts, so you can focus on coding instead of clicking.

## The Problem

You're using Claude Code and hitting your flow state. Code is working, ideas are flowing, and then... "Do you want to continue?" appears on screen. You click yes. Two minutes later: "Would you like to proceed?" Another click. Then you step away for coffee and come back to find your script stopped, waiting for a response you never saw.

These constant interruptions break your concentration and slow down your workflow.

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

**Portable script** (no installation):
```bash
curl -s https://raw.githubusercontent.com/safurrier/claude-code-autoyes/main/claude_code_autoyes.py | uv run --script -
```

**Development setup**:
```bash
git clone https://github.com/safurrier/claude-code-autoyes.git
cd claude-code-autoyes
make setup
```

## Requirements

- Python 3.9 or newer
- tmux for session management
- Claude Code running in tmux sessions

That's it. No complex setup, no configuration files, no database backends.

## License

MIT License - use it however you want.