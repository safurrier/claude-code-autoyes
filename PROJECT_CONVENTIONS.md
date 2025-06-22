# Project Conventions

## Code Style Standards

### Python Conventions
- **NO INLINE IMPORTS** - All imports at top of file
- Import order: standard lib → third-party → project imports
- snake_case for functions/variables, PascalCase for classes
- Prefer dataclasses over dictionaries
- Use proper type hints from `typing` module - avoid `Any`
- Specific exceptions with context over generic ones

### Function Design
- Descriptive docstrings with Args and Returns sections
- Avoid boolean parameters - use enums for options
- Single responsibility principle
- Keep functions short and focused

## CLI Design (Click Framework)

### Framework Choice
- **Use Click over argparse or typer** for consistency
- Leverage Click's decorator-based API
- Use Click's CliRunner for testing

### Command Structure
- Subcommands for complex tools: `tool subcommand [options]`
- Support `--help` on every command and subcommand
- Sensible defaults covering 80% of use cases
- Environment variable support for configuration

## Testing Strategy (Progressive Approach)

### Testing Evolution
1. **E2E Tests** - Start here (full functionality)
2. **Smoke Tests** - Add next (quick validation)
3. **Integration Tests** - Component interaction
4. **Unit Tests** - Detailed behavior testing

### Anti-Patterns to Avoid
- Excessive mocking/patching (code smell)
- Testing implementation details vs behavior
- Checking specific strings in outputs (brittle)
- Complex test setup without builders

### Preferred Approaches
- Use stubs and fakes over mocks
- Test behavior, not implementation
- Table-driven testing with parametrization
- Arrange-Act-Assert pattern

## Build System

### Commands
- `make setup` - Project initialization
- `make test` - Run all tests
- `make check` - All quality checks
- `make format` - Code formatting
- `uv run -m pytest path/to/test.py` - Specific tests

### Quality Gates
- Pre-commit hooks enforce standards
- MyPy type checking required
- ruff formatting and linting
- Test coverage monitoring

## Architecture Principles (MODEST)

- **Modularity**: Swappable, reusable components
- **Orthogonality**: Independent components, localized changes
- **Dependency Injection**: External dependencies passed in
- **Explicitness**: Clear intent, avoid magic
- **Single Responsibility**: One reason to change
- **Testability**: Designed for easy testing

## File Organization

### Preferences
- **Edit existing files** over creating new ones
- Modular package structure with clear separation
- Business logic separate from CLI/TUI code
- Standard package layout with __init__.py files

### Current Structure
```
claude_code_autoyes/
├── cli.py                 # Main Click command group
├── commands/              # Subcommand modules
├── tui/                   # TUI application package
├── core/                  # Business logic
└── tests/                 # Progressive testing
    ├── e2e/              # End-to-end tests
    ├── smoke/            # Quick validation
    ├── integration/      # Component interaction
    └── unit/             # Detailed behavior
```

## Error Handling

### User Experience
- Design error messages to guide users back to success
- Include helpful context and potential solutions
- Use specific exception types with clear messages
- Show progress indicators for operations >1 second

## Documentation Style

### Natural Writing
- Mix paragraph lengths intentionally
- Use specific, concrete examples
- Write like telling a colleague
- Avoid academic/formal language

### Git Commit Messages
- Imperative mood: "Add feature" not "Added feature"
- Be specific and concise
- Focus on what changed and why
- Avoid generic corporate language

## TUI-Specific Conventions

### Architecture
- Module-based design with self-contained components
- Reactive properties with `init=False` for performance
- Direct TextualApp extension (avoid abstraction layers)
- CSS variables for dynamic theming

### Performance
- Progressive loading: config → database → app
- Deferred initialization for heavy components
- Efficient CSS refresh: `self.refresh_css(animate=False)`
- Lazy loading patterns

### Testing
- Timeout-based detection for TUI launch verification
- Component isolation for unit tests
- Mock external dependencies (file systems, networks)
- Verify keyboard navigation paths

## Safety Nets

### Pre-commit Hooks
- MyPy type checking
- ruff linting and formatting
- Test execution
- **Never bypass with --no-verify** unless absolutely necessary

### Development Workflow
1. Make changes
2. Test locally: `uv run mypy .`
3. Test E2E: `uv run pytest tests/e2e/`
4. Commit normally (let hooks run)
5. Never bypass safety nets

## Code Quality Metrics

### Success Indicators
- Components are easily testable
- New features don't require modifying existing components
- Code follows established conventions
- Natural, authentic documentation
- Progressive testing coverage as features stabilize