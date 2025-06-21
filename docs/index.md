# Claude Code Auto-Yes

Automatically respond "yes" to prompts in Claude Code sessions running in tmux.

## What is Claude Code Auto-Yes?

Claude Code Auto-Yes is a tool that monitors your tmux sessions for Claude Code instances and automatically responds "yes" to confirmation prompts. This eliminates the need to manually confirm actions during development workflows.

## Features

- 🤖 **Automatic prompt detection** - Finds Claude prompts using smart pattern matching
- 🎯 **Tmux integration** - Works seamlessly with tmux sessions  
- 🔧 **Session management** - Enable/disable auto-yes per session
- 🖥️ **Interactive TUI** - Manage sessions with a beautiful terminal interface
- ⚡ **CLI commands** - Quick status checks and daemon control
- 🛡️ **Safe operation** - Process-based detection to avoid false positives

## Quick Start

### Installation

```bash
# Install via UV tool
uv tool install claude-code-autoyes

# Or install from source
git clone https://github.com/safurrier/claude-code-autoyes.git
cd claude-code-autoyes
make dev-install
```

### Basic Usage

```bash
# Check current status
claude-code-autoyes status

# Launch interactive TUI
claude-code-autoyes tui

# Enable auto-yes for all Claude sessions
claude-code-autoyes enable-all

# Start the background daemon
claude-code-autoyes daemon start
```

## How It Works

1. **Detection**: Scans tmux panes for Claude Code processes
2. **Monitoring**: Background daemon watches enabled sessions for prompts
3. **Response**: Automatically sends "Enter" key when Claude prompts are detected
4. **Control**: Fine-grained control over which sessions have auto-yes enabled

## Installation Options

### End Users

```bash
# Install as a UV tool (recommended)
uv tool install claude-code-autoyes

# Or use pip
pip install claude-code-autoyes
```

### Developers

```bash
# Clone and set up development environment
git clone https://github.com/safurrier/claude-code-autoyes.git
cd claude-code-autoyes
make setup
make dev-install
```

## Development

See the [Getting Started](getting-started.md) guide for detailed development instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite: `make check`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.