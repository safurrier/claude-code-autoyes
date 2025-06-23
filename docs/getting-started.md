# Getting Started

This guide will get you up and running with claude-code-autoyes in just a few minutes.

## Prerequisites

**Required:**
- **tmux** - This tool only works with Claude Code running in tmux sessions. [Install tmux](https://github.com/tmux/tmux/wiki/Installing) if you don't have it.
- **Python 3.9+**
- **Claude Code** running in tmux panes

**Important**: Claude Code must be running inside tmux sessions for this tool to detect and monitor it.

## Installation

Install using UV (recommended):
```bash
uv tool install git+https://github.com/safurrier/claude-code-autoyes.git
```

Or run without installing:
```bash
git clone https://github.com/safurrier/claude-code-autoyes.git
cd claude-code-autoyes
uv run claude_code_autoyes.py
```

## Typical Workflow

Here's the standard way to use the tool:

1. **Start Claude Code in tmux**: Launch your Claude Code session within a tmux session
2. **Check sessions**: Use `claude-code-autoyes status` to see detected Claude sessions
3. **Enable auto-yes**: Use `claude-code-autoyes enable-all` or enable specific sessions via TUI
4. **Start daemon**: Run `claude-code-autoyes daemon start` to begin monitoring
5. **Work normally**: The tool will automatically respond to Claude prompts

*[Screenshot placeholder: Terminal showing typical workflow commands and output]*

## Basic Usage

### Command Line Interface

Check the status of tmux sessions:
```bash
claude-code-autoyes status
```

Enable auto-yes for all Claude Code sessions:
```bash
claude-code-autoyes enable-all
```

Launch the interactive TUI:
```bash
claude-code-autoyes tui
```

*[Screenshot placeholder: TUI interface showing Claude instances and controls]*

### Daemon Control

Start the background daemon:
```bash
claude-code-autoyes daemon start
```

Check daemon status:
```bash
claude-code-autoyes daemon status
```

Stop the daemon:
```bash
claude-code-autoyes daemon stop
```

## Interactive TUI

The Terminal User Interface provides a visual way to manage sessions:

```bash
claude-code-autoyes tui
```

*[Demo placeholder: Animated GIF showing TUI navigation and theme switching]*

Features:
- View all tmux sessions and panes
- See which sessions have Claude Code running
- Toggle auto-yes on/off per session
- Real-time status updates
- **Multiple themes**: 11 beautiful themes including Dracula, Nord, Gruvbox, and more
- **Jump navigation**: Quick keyboard navigation to any UI element
- **Enhanced controls**: Improved focus management and responsiveness

### TUI Keyboard Shortcuts
- `↑↓`: Navigate instances
- `Enter/Space`: Toggle selected instance
- `1-9`: Quick toggle by number
- `d`: Toggle daemon
- `r`: Refresh
- `t`: Cycle themes
- `v`: Jump Mode (quick navigation)
- `Ctrl+Q`: Quit

## How It Works

### Detection Process

1. **Session Discovery**: Scans tmux sessions for running processes
2. **Claude Identification**: Looks for processes with "claude" in the name (case-insensitive)
3. **Prompt Monitoring**: Watches enabled sessions for specific prompt patterns:
   - "Do you want to"
   - "Would you like to"
   - "Proceed?"
   - "❯ 1. Yes"

### Response Mechanism

- When a prompt is detected, the daemon automatically sends an "Enter" key to the session
- Configurable delay between responses to avoid overwhelming the system
- Session-specific enable/disable controls for fine-grained management

## Troubleshooting

### Common Issues

**No sessions detected:**
- Ensure Claude Code is running in a tmux session
- Check that the process name contains "claude" (case-insensitive)
- Verify tmux is accessible from the command line

**Daemon not responding:**
- Check daemon status: `claude-code-autoyes daemon status`
- Review daemon logs: `/tmp/claude-autoyes.log`
- Restart the daemon: `claude-code-autoyes daemon restart`

**Auto-yes not working:**
- Verify the session is enabled: `claude-code-autoyes status`
- Check that prompts match the expected patterns
- Ensure no conflicting input is being sent to the session

## Documentation

### Viewing Documentation

Serve documentation locally:
```bash
make docs-serve
```

The documentation will be available at http://localhost:8000

### Building Documentation

Build static documentation:
```bash
make docs-build
```

The built documentation will be in the `site/` directory.

## Development

Want to contribute or modify the tool?

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/safurrier/claude-code-autoyes.git
   cd claude-code-autoyes
   ```

2. Set up the development environment:
   ```bash
   make setup
   ```

3. Install development tools:
   ```bash
   make dev-install
   ```

4. Run the tests to verify everything works:
   ```bash
   make test
   ```

### Development Workflow

1. Make your changes to the code
2. Add or update tests as needed
3. Run quality checks:
   ```bash
   make check
   ```
4. Update documentation if needed
5. Commit your changes
6. Create a pull request

### Available Commands

Run `make` to see all available commands:

- `make setup` - Set up development environment
- `make test` - Run tests with coverage
- `make lint` - Run linting
- `make format` - Format code
- `make mypy` - Run type checking
- `make check` - Run all quality checks
- `make docs-serve` - Serve documentation locally
- `make docs-build` - Build documentation

### Testing

Run the test suite:
```bash
make test
```

Run specific tests:
```bash
uv run -m pytest tests/test_specific.py::test_function_name
```

Run tests with coverage:
```bash
make test-coverage
```