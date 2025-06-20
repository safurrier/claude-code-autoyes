# Getting Started

This guide will help you get started with claude-code-autoyes.

## Prerequisites

- Python 3.9 or higher
- Git

## Installation

### End Users

Install from PyPI:
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

3. Run the tests to verify everything works:
   ```bash
   make test
   ```

## Basic Usage

```python
import claude_code_autoyes

# Add your basic usage examples here
```

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