# Getting Started

This guide will help you get started with claude-code-autoyes, a tool that automatically responds "yes" to Claude Code prompts in tmux sessions.

## Prerequisites

- Python 3.10 or higher
- tmux (for session monitoring)
- Git (for development)

## Installation

### End Users

Install using UV (recommended):
```bash
uv tool install claude-code-autoyes
```

Or install from PyPI:
```bash
pip install claude-code-autoyes
```

### Developers

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

## Typical Workflow

1. **Start Claude Code in tmux**: Launch your Claude Code session within a tmux session
2. **Check sessions**: Use `claude-code-autoyes status` to see detected Claude sessions
3. **Enable auto-yes**: Use `claude-code-autoyes enable-all` or enable specific sessions via TUI
4. **Start daemon**: Run `claude-code-autoyes daemon start` to begin monitoring
5. **Work normally**: The tool will automatically respond to Claude prompts

## Interactive TUI

The Terminal User Interface provides a visual way to manage sessions:

```bash
claude-code-autoyes tui
```

Features:
- View all tmux sessions and panes
- See which sessions have Claude Code running
- Toggle auto-yes on/off per session
- Real-time status updates

## How It Works

### Detection Process

1. **Session Discovery**: Scans tmux sessions for running processes
2. **Claude Identification**: Looks for `claude_code_autoyes`, `claude-code-autoyes`, or `claude-autoyes` processes
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

## Development Workflow

1. Make your changes to the code
2. Add or update tests as needed
3. Run quality checks:
   ```bash
   make check
   ```
4. Update documentation if needed
5. Commit your changes
6. Create a pull request

## Available Commands

Run `make` to see all available commands:

- `make setup` - Set up development environment
- `make test` - Run tests with coverage
- `make lint` - Run linting
- `make format` - Format code
- `make mypy` - Run type checking
- `make check` - Run all quality checks
- `make docs-serve` - Serve documentation locally
- `make docs-build` - Build documentation

## Testing

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