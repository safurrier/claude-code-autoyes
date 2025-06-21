# Project Commands
- Build/setup: `make setup`
- Run all checks: `make check`
- Format code: `make format`
- Type check: `make mypy`
- Lint code: `make lint`
- Test all: `make test`
- Test single: `uv run -m pytest tests/path_to_test.py::test_function_name`
- Dev container: `make dev-env`

# Code Style
- **Types**: Strict typing with mypy, use proper annotations from `typing` module
- **Imports**: Standard lib first, third-party second, project imports last
- **Formatting**: Enforced by ruff formatter
- **Docstrings**: Include Args and Returns sections
- **Classes**: Prefer dataclasses for data structures
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Error Handling**: Prefer specific exceptions with context
- **Python Version**: 3.9+ (preferably 3.12)

# Development Safety Nets

## Pre-commit Hooks
The project uses pre-commit hooks for mypy, linting, formatting, and tests.

**CRITICAL**: Never bypass pre-commit hooks with `--no-verify` unless absolutely necessary. These are safety nets that catch errors before they reach the codebase.

## Development Workflow
1. **Make changes**
2. **Test locally**: `uv run mypy .` for type checking
3. **Test E2E**: `uv run pytest tests/e2e/` for integration validation  
4. **Commit normally**: Let pre-commit hooks run and catch issues
5. **Never bypass safety nets**: Pre-commit hooks exist for a reason

## E2E Testing Patterns
- **TUI testing**: Use timeout-based detection for launch verification
  - Successful launch = process times out (means it's running)
  - Failed launch = immediate exit with error code
- **Subprocess testing**: Use `subprocess.TimeoutExpired` to detect successful service starts

## Safety Net Layers
1. **MyPy**: Catches type errors and attribute issues at commit time
2. **E2E Tests**: Validates actual runtime behavior and integration
3. **Pre-commit Hooks**: Enforces all checks before code enters repository
4. **Each layer catches different classes of errors - all are essential**