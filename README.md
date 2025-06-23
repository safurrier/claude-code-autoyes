# Claude Code AutoYes

Automatically respond to Claude Code prompts in tmux sessions. No more manual clicking - stay focused on your work.

## Why You Need This

Claude Code frequently asks "Do you want to continue?" and similar confirmation prompts. These interruptions break your flow, and you sometimes miss prompts when stepping away from your screen.

This tool monitors your tmux sessions and automatically responds to these prompts. You control which sessions get automated responses and which ones you want to handle manually.

## Quick Start

Let's get you up and running in under 2 minutes.

### Step 1: Install
```bash
uv tool install git+https://github.com/safurrier/claude-code-autoyes.git
```

### Step 2: See What's Running
```bash
claude-code-autoyes status
```

You'll see a list of your tmux sessions and which ones have Claude Code running. Something like:
```
Session: main, Pane: 0 - Claude detected ❌ (disabled)
Session: work, Pane: 1 - Claude detected ❌ (disabled)
```

### Step 3: Enable Auto-Yes
```bash
claude-code-autoyes enable-all
```

### Step 4: Start the Daemon
```bash
claude-code-autoyes daemon start
```

That's it! Now when Claude prompts you, the tool automatically responds. To see it in action, run the interactive TUI:

```bash
claude-code-autoyes
```

## The Interactive Interface

The TUI gives you real-time control over everything. Press individual number keys (1-9) to quickly toggle specific Claude instances, or use the buttons for bulk operations.

**Pro tips:**
- Press `t` to cycle through 11 themes (try Dracula or Nord)
- Press `v` for jump mode - quick keyboard navigation to any part of the interface
- Press `d` to toggle the daemon on/off
- Use `Ctrl+Q` to quit (not just `q` - we learned that lesson)

## When Things Go Wrong

**"No sessions detected"**: Make sure Claude Code is actually running in a tmux session. This tool can't see processes outside tmux.

**"Daemon not responding"**: Check if it's actually running with `claude-code-autoyes daemon status`. If it's stuck, restart it:
```bash
claude-code-autoyes daemon stop
claude-code-autoyes daemon start
```

**"It's not auto-responding"**: Verify the session is enabled with `claude-code-autoyes status`. The daemon only watches enabled sessions.

## How It Actually Works

The tool scans tmux sessions looking for processes with "claude" in the name. When it finds them, it can monitor those panes for specific prompt patterns like:
- "Do you want to"
- "Would you like to" 
- "Proceed?"
- "❯ 1. Yes"

When a prompt appears in an enabled session, the daemon sends an "Enter" keypress to that tmux pane. It's that simple.

## Advanced Usage

### Selective Control
You don't have to enable all sessions. Use the TUI to toggle individual Claude instances, or enable/disable specific ones:

```bash
# Check what's available first
claude-code-autoyes status

# Enable just session "main", pane 0
claude-code-autoyes enable main:0

# Disable a specific session
claude-code-autoyes disable work:1
```

### Different Installation Methods

**UV Tool** (recommended - installs globally):
```bash
uv tool install git+https://github.com/safurrier/claude-code-autoyes.git
```

**UV Script** (run without installing):
```bash
# Clone and run directly
git clone https://github.com/safurrier/claude-code-autoyes.git
cd claude-code-autoyes
uv run claude_code_autoyes.py
```

**Development Setup** (if you want to hack on it):
```bash
git clone https://github.com/safurrier/claude-code-autoyes.git
cd claude-code-autoyes
make setup
```

### Daemon Management

The daemon runs in the background monitoring your enabled sessions. You can:
- `claude-code-autoyes daemon start` - Start monitoring
- `claude-code-autoyes daemon stop` - Stop monitoring  
- `claude-code-autoyes daemon status` - Check if it's running
- `claude-code-autoyes daemon restart` - Restart if it gets stuck

Logs go to `/tmp/claude-autoyes.log` if you need to debug issues.

## Keyboard Reference

When using the TUI:
- `↑↓` - Navigate the list
- `Enter` or `Space` - Toggle the selected session
- `1-9` - Instantly toggle sessions by number
- `d` - Start/stop the daemon
- `r` - Refresh the session list
- `t` - Cycle through themes
- `v` - Jump mode (press letter keys to jump to interface elements)
- `Ctrl+Q` - Quit

## Requirements

- **tmux** - This tool only works with Claude Code running in tmux sessions. [Install tmux](https://github.com/tmux/tmux/wiki/Installing) if you don't have it.
- **Python 3.9+** 
- **Claude Code** running in tmux panes

**Important**: Claude Code must be running inside tmux sessions for this tool to detect and monitor it.

## Development

Want to contribute or run the tests?

```bash
make check      # Run all quality checks
make test       # Run the test suite
make docs-serve # Preview documentation locally
```

The codebase uses modern Python with strict typing, comprehensive tests, and a modular TUI architecture. Check out `PROJECT_CONVENTIONS.md` for development guidelines.

## License

MIT License - use it, modify it, share it.