# Comprehensive Conventions Research Report

## Executive Summary

This report consolidates user-established conventions from ~/.claude/ directory and current project patterns to inform TUI restructuring decisions. The research reveals strong opinions on code organization, testing strategies, CLI design, and writing style that must be incorporated into the restructuring plan.

## Technology Stack Assessment

**Current Project Stack:**
- Python 3.10+ with strict typing (mypy)
- Click CLI framework (user's explicit preference over argparse/typer)
- Textual TUI framework (0.89.0+)
- pytest with comprehensive testing markers
- uv for package management
- ruff for formatting/linting
- Pre-commit hooks enforced

**Mapped Domain Conventions:**
- Python core patterns
- CLI/Click best practices
- Testing progressive approach
- Git standards
- Writing authenticity guidelines

## Critical User Conventions

### 1. Python Development Standards

**Code Organization (STRICT):**
- **NO INLINE IMPORTS** - All imports at top of file (frequently violated, requires constant reinforcement)
- Standard lib → third-party → project imports
- snake_case for functions/variables, PascalCase for classes
- Prefer dataclasses over dictionaries
- Use proper type hints from `typing` module
- Avoid `Any` type hints - be specific

**Error Handling:**
- Use specific exceptions with context
- Design error messages to guide users back to success
- Include helpful context and potential solutions

**Function Design:**
- Write descriptive docstrings with Args and Returns sections
- Avoid boolean parameters - use enums for options
- Follow single responsibility principle
- Keep functions short and focused

### 2. CLI Design Philosophy (Click-Centric)

**Framework Choice (FIRM):**
- **Use Click over argparse or typer** for consistency and reliability
- Leverage Click's decorator-based API for readability
- Use Click's built-in testing utilities (CliRunner)

**Command Structure:**
- Use subcommands for complex tools (`tool subcommand [options]`)
- Support `--help` on every command and subcommand
- Provide sensible defaults that cover 80% of use cases
- Environment variable support for configuration

**User Experience:**
- Make errors actionable with specific guidance
- Show progress indicators for operations >1 second
- Support both human-readable and machine-readable output
- Use colors by default for interactive terminals with `--no-color` option

### 3. Testing Strategy (Progressive Approach)

**Testing Evolution Timeline:**
```
End-to-End Tests (Start here)
    ↓
Smoke Tests (Add next) 
    ↓
Integration Tests (Then add these)
    ↓
Unit Tests & Property-Based Tests (Refine with these)
```

**Anti-Patterns to AVOID:**
- **Excessive mocking/patching** (major code smell)
- **Checking specific strings in outputs** (brittle, couples to implementation)
- Testing implementation details instead of behavior
- Complex test setup without builders/factories

**Preferred Approaches:**
- Use stubs and fakes over mocks
- Test behavior, not implementation
- Table-driven testing with parametrization
- Arrange-Act-Assert pattern consistently

### 4. Writing and Communication Standards

**LLM Tell Elimination (CRITICAL):**
Never use these words (instant LLM tells):
- intricate, pivotal, commendable, realm, showcase, delve
- meticulous, versatile, notable, comprehensive, utilize
- enhance, capabilities, crucial, robust, seamless, leverage

**Natural Writing Patterns:**
- Mix paragraph lengths intentionally
- Avoid 4-bullet syndrome (vary bullet counts: 1-3 max)
- Use specific, concrete examples
- Write like telling a colleague, not writing an academic paper

**Git Commit Style:**
- Imperative mood: "Add feature" not "Added feature"
- Be specific and concise
- Avoid LLM language ("enhance," "implement," "utilize")
- Focus on what changed and why

### 5. Code Quality Standards (MODEST Principles)

- **Modularity**: Building components that are swappable and reusable
- **Orthogonality**: Components should be independent and changes localized
- **Dependency Injection**: External dependencies should be passed in
- **Explicitness**: Intent should be clear in code, avoid magic
- **Single Responsibility**: Each component should have one reason to change
- **Testability**: Code should be designed to be easily testable

### 6. Project-Specific Patterns

**Build Commands:**
- Use `make` commands for all operations
- `make test` for all tests, `uv run -m pytest` for specific tests
- Pre-commit hooks enforce quality standards

**File Organization:**
- Prefer editing existing files over creating new ones
- Use modular package structure with clear separation
- Keep business logic separate from CLI/TUI code

## TUI Restructuring Implications

### Recommended Structure Based on Conventions

```
claude_code_autoyes/
├── __init__.py
├── cli.py                   # Main Click group (follows convention)
├── commands/                # Subcommand modules (established pattern)
│   ├── __init__.py
│   ├── tui.py              # TUI command entry point
│   ├── daemon.py
│   ├── status.py
│   └── ...
├── tui/                    # NEW: Dedicated TUI package
│   ├── __init__.py
│   ├── app.py              # Main TUI application
│   ├── widgets/            # Reusable TUI components
│   │   ├── __init__.py
│   │   ├── table.py        # Instance table widget
│   │   ├── status.py       # Status display widget
│   │   └── controls.py     # Button/control widgets
│   ├── screens/            # Different TUI screens if needed
│   │   ├── __init__.py
│   │   └── main.py         # Main screen
│   └── theme.py            # CSS/styling separated
├── core/                   # Business logic (unchanged)
│   └── ...
└── tests/                  # Progressive testing approach
    ├── e2e/                # Start here per conventions
    ├── smoke/              # Add next
    ├── integration/        # Then these
    └── unit/               # Refine with these
```

### Key Restructuring Principles

1. **Separation of Concerns**: Move TUI code into dedicated package
2. **Reusable Components**: Create widget library following modularity principle
3. **Testable Design**: Structure for dependency injection and testing
4. **Click Integration**: Maintain clean command structure
5. **Progressive Enhancement**: Allow TUI features to be added incrementally

### Testing Strategy for TUI

**Phase 1: E2E Tests**
- Basic TUI functionality (launch, navigate, quit)
- Critical user paths (toggle instances, daemon control)

**Phase 2: Smoke Tests** 
- Quick validation of major TUI components
- Interface responsiveness checks

**Phase 3: Integration Tests**
- TUI-to-core integration
- Configuration persistence through TUI

**Phase 4: Unit Tests**
- Individual widget behavior
- State management logic

### Code Organization Rules

1. **No inline imports** in TUI modules
2. **Type hints** for all TUI component interfaces
3. **Dataclasses** for TUI state management
4. **Explicit dependency injection** for core services
5. **Single responsibility** for each widget/component

## Implementation Priorities

1. **Extract current TUI into modular structure** (follows editing over creating)
2. **Add proper testing foundation** (start with E2E as per conventions)
3. **Implement widget library** (reusability principle)
4. **Enhance CLI integration** (maintain Click standards)
5. **Add comprehensive documentation** (natural writing style)

## Success Metrics

- TUI components are easily testable
- New features can be added without modifying existing components
- Code follows all established conventions
- Natural, authentic documentation and commit messages
- Progressive testing coverage as features stabilize

This research provides the foundation for a TUI restructuring that aligns with established user conventions while enabling future growth and maintainability.