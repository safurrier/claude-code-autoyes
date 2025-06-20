# Claude Code AutoYes

Interactive TUI for managing auto-yes across Claude instances in tmux. Never miss a Claude prompt again!

## Features

- 🖥️ **Interactive TUI**: Beautiful terminal interface for managing Claude instances
- 🔍 **Auto-Detection**: Automatically finds Claude instances running in tmux panes
- ⚡ **Daemon Mode**: Background process to automatically respond to prompts
- 🎯 **Selective Control**: Enable/disable auto-yes per Claude instance
- 📊 **Real-time Status**: Live monitoring of Claude instances and their states
- 🛠️ **Multiple Installation Options**: UV tool, UV script, or traditional pip

## Installation

### UV Tool (Recommended)
Install as a global tool with uv:
```bash
# Install from GitHub
uv tool install git+https://github.com/safurrier/claude-code-autoyes.git

# Or install locally
git clone https://github.com/safurrier/claude-code-autoyes.git
cd claude-code-autoyes
uv tool install .
```

### UV Script (Alternative)
```bash
# Download and run directly with UV
curl -s https://raw.githubusercontent.com/safurrier/claude-code-autoyes/main/claude_code_autoyes.py | uv run --script -

# Or run locally
git clone https://github.com/safurrier/claude-code-autoyes.git
cd claude-code-autoyes
uv run claude_code_autoyes.py
```

### Development Installation
```bash
git clone https://github.com/safurrier/claude-code-autoyes.git
cd claude-code-autoyes
make setup
```

## Usage

### Installed as UV Tool
```bash
# Launch interactive TUI (default)
claude-code-autoyes

# Show current status
claude-code-autoyes status

# Enable auto-yes for all Claude instances
claude-code-autoyes enable-all

# Disable auto-yes for all instances
claude-code-autoyes disable-all

# Launch TUI explicitly
claude-code-autoyes tui
```

### Running as Script
```bash
# UV script (portable)
uv run claude_code_autoyes.py

# Module execution
uv run -m claude_code_autoyes

# With specific commands
uv run claude_code_autoyes.py status
uv run -m claude_code_autoyes enable-all
```

## TUI Interface

The interactive TUI provides:

- **Table View**: All detected Claude instances with their status
- **Quick Toggle**: Press 1-9 to quickly toggle individual instances
- **Daemon Control**: Start/stop background daemon with 'd' key
- **Bulk Operations**: Enable/disable all instances at once
- **Real-time Updates**: Live status updates every few seconds

### Keyboard Shortcuts
- `↑↓`: Navigate instances
- `Enter/Space`: Toggle selected instance
- `1-9`: Quick toggle by number
- `d`: Toggle daemon
- `r`: Refresh
- `q`: Quit

## How It Works

1. **Detection**: Scans tmux panes for Claude processes
2. **Monitoring**: Tracks which instances need auto-yes responses
3. **Automation**: Background daemon watches for prompts and responds automatically
4. **Control**: Fine-grained control over which instances are automated

## Development

### Quality Checks
```bash
make check      # Run all checks (test, mypy, lint, format)
make test       # Run tests with coverage
make test-smoke # Fast module import tests
make test-e2e   # CLI equivalence tests
```

### Project Structure
```
claude-code-autoyes/
├── claude_code_autoyes/      # Main package
│   ├── core/                 # Business logic
│   │   ├── models.py        # Data models
│   │   ├── detector.py      # Claude detection
│   │   ├── config.py        # Configuration management
│   │   └── daemon.py        # Background daemon
│   ├── commands/            # CLI commands
│   ├── cli.py              # Main CLI entry point
│   ├── tui.py              # TUI application
│   └── __main__.py         # Module execution
├── tests/                   # Test suite
│   ├── e2e/                # End-to-end tests
│   ├── smoke/              # Smoke tests
│   ├── integration/        # Integration tests
│   └── unit/               # Unit tests
└── claude_code_autoyes.py   # UV script wrapper
```

## Requirements

- Python 3.9+
- tmux (for Claude instance detection)
- Claude Code instances running in tmux

## License

MIT License - see LICENSE file for details.