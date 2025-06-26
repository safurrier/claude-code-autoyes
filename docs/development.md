# Local Development Guide

Quick reference for testing PRs and developing claude-code-autoyes locally.

## Quick Start

```bash
# Show all available commands
make help

# Test a specific PR
make dev-test-pr PR=4

# Test daemon functionality  
make dev-daemon-test

# Watch daemon logs
make dev-logs

# Clean up when done
make dev-uninstall
```

## Commands Overview

### 🔧 Development & Testing Commands

| Command | Purpose |
|---------|---------|
| `make dev-install` | Install current branch as test tool |
| `make dev-uninstall` | Remove test tool installation |
| `make dev-test-pr PR=4` | Test a specific PR |
| `make dev-run` | Run current code without installing |
| `make dev-status` | Show current development status |
| `make dev-daemon-test` | Test daemon with simulated prompts |
| `make dev-logs` | Tail daemon logs |
| `make dev-daemon-stop` | Stop daemon and clean up |

### 📊 Performance Analysis Commands

| Command | Purpose |
|---------|---------|
| `uv run python -m claude_code_autoyes debug --help` | Show all debug commands |
| `uv run python -m claude_code_autoyes debug startup-time` | Measure TUI startup performance |
| `uv run python -m claude_code_autoyes debug navigation-test` | Test navigation responsiveness |
| `uv run python -m claude_code_autoyes debug profile` | Profile with py-spy (requires setup) |
| `uv run python -m claude_code_autoyes tui --debug` | Launch TUI with debug mode |

### Testing Workflow

#### 1. Test a Pull Request
```bash
# Fetch and test PR #4
make dev-test-pr PR=4

# Now you have 'claude-code-autoyes-test' command available
claude-code-autoyes-test --help
claude-code-autoyes-test status
```

#### 2. Test Daemon Functionality
```bash
# Set up test environment and start daemon
make dev-daemon-test

# In another terminal, watch logs
make dev-logs

# Manually test by attaching to tmux session
tmux attach -t claude-test
./scripts/simulate-claude-prompt.sh
```

#### 3. Clean Up
```bash
# Stop everything and clean up
make dev-daemon-stop
make dev-uninstall

# Return to main branch
git checkout main
```

## Tool Installation Details

The development commands use UV tool installation with a unique name:
- **Tool name**: `claude-code-autoyes-test`
- **Installation**: `uv tool install --from . --name claude-code-autoyes-test claude-code-autoyes`
- **Isolation**: Won't conflict with your main installation

## Performance Analysis

### Setup Performance Tools
```bash
# Install optional performance dependencies
uv sync --extra performance

# Verify py-spy installation
uv run py-spy --version
```

### Performance Testing Workflow
```bash
# Quick performance check
uv run python -m claude_code_autoyes debug startup-time
uv run python -m claude_code_autoyes debug navigation-test

# Deep profiling (requires sudo on macOS)
uv run python -m claude_code_autoyes tui &
TUI_PID=$!
sudo uv run py-spy record -p $TUI_PID -d 10 -o /tmp/profile.svg
kill $TUI_PID
# Open /tmp/profile.svg in browser

# Run performance test suite
uv run -m pytest tests/performance/ -v
```

### Performance Benchmarks
- **Startup Time**: ~0.53s (good performance)
- **Navigation**: ~0.056s average (excellent responsiveness)
- **Import Overhead**: Textual ~0.086s, others <0.010s

## Daemon Testing

The daemon testing workflow:

1. **Creates test tmux session**: `claude-test`
2. **Installs test tool**: `claude-code-autoyes-test`
3. **Enables all sessions**: Configures daemon to monitor all tmux sessions
4. **Starts daemon**: Runs in background monitoring for prompts
5. **Provides test script**: `scripts/simulate-claude-prompt.sh`
6. **Shows logs**: Tail `/tmp/claude-autoyes.log`

## Manual Testing

For manual testing without make commands:

```bash
# Install test version
uv tool install --from . --name my-test-tool claude-code-autoyes

# Test commands
my-test-tool status
my-test-tool daemon start
my-test-tool daemon status

# Clean up
uv tool uninstall my-test-tool
```

## Troubleshooting

### Tool Installation Issues
```bash
# If installation fails, try forcing reinstall
uv tool install --from . --force-reinstall --name claude-code-autoyes-test claude-code-autoyes
```

### Daemon Issues
```bash
# Check if daemon is running
claude-code-autoyes-test daemon status

# Check logs
cat /tmp/claude-autoyes.log

# Kill any stuck processes
pkill -f claude-autoyes
```

### Tmux Issues
```bash
# List tmux sessions
tmux list-sessions

# Kill specific session
tmux kill-session -t claude-test

# Kill all tmux sessions (careful!)
tmux kill-server
```

## Project Structure

```
claude-code-autoyes/
├── claude_code_autoyes/     # Main package
├── tests/                   # Test suite
├── scripts/                 # Development scripts (auto-generated)
├── docs/                    # Documentation
├── Makefile                 # Development commands
└── claude_code_autoyes.py   # UV script entry
```

## Contributing

1. Create your feature branch
2. Make changes
3. Test with `make dev-install`
4. Run quality checks: `make check`
5. Create pull request
6. Test PR with `make dev-test-pr PR=<number>`