# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Global auto-yes toggle**: Master switch to enable/disable entire auto-yes functionality
- **Automatic daemon lifecycle**: Daemon now starts automatically with TUI and stops when TUI quits
- **Enhanced daemon service**: New `should_process_session()` method checks both session and global state
- Integration with uv for dependency management
- Modern Python development tools:
  - ruff for linting and formatting
  - mypy for type checking
  - pytest with coverage reporting
- GitHub Actions workflow for automated testing
- Docker development environment improvements

### Changed
- **Simplified user experience**: No more manual daemon start/stop - it's fully automatic
- **TUI streamlined**: Removed Start/Stop daemon buttons and keyboard shortcut
- Global toggle persists across application restarts in config file
- Switched from pip/venv to uv for environment management
- Updated example code to pass mypy type checking
- Modernized project structure and development workflow
- Updated Python version to 3.12

### Removed
- Manual daemon control buttons from TUI (daemon is now automatic)
- `d` key binding for daemon toggle (no longer needed)
- Legacy dependency management approach
- Outdated Docker configuration elements

### Fixed
- Type hints in example code to pass mypy checks
- Docker environment management
- Development workflow and quality checks

## [0.1.0] - 2024-04-14
- Initial fork from eugeneyan/python-collab-template
- Added Docker environment management
- Setup package installation configuration
