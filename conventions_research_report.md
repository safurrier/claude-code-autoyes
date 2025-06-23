# Comprehensive Conventions Research Report

This report consolidates all user conventions from ~/.claude/ domains to ensure implementation plans follow exact established standards.

## 1. Testing Conventions

### Progressive Testing Philosophy
**Core Approach**: End-to-End → Smoke → Integration → Unit Tests
- Start with E2E tests for critical user paths
- Add smoke tests for system validation
- Build integration tests for component interaction
- Refine with unit tests for complex logic

### Test Organization (From Current Project)
```
tests/
├── e2e/          # Complete user workflow validation
├── integration/  # Component interaction testing
├── smoke/        # High-level system validation  
└── unit/         # Individual component behavior
```

### Critical Testing Patterns

#### TUI Launch Detection Pattern
**Core Principle**: TUI apps that launch successfully run indefinitely; failed launches exit immediately.
```python
def test_tui_launches_successfully():
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-m", "myapp", "tui"],
            timeout=2,  # Short timeout
            capture_output=True,
            text=True
        )
        # Quick exit = probably failed
        assert result.returncode in [0, 130]
    except subprocess.TimeoutExpired:
        # Timeout = successful launch and running
        assert True, "TUI launched successfully"
```

#### Test Doubles Over Mocks
- **AVOID mocks and patching** - major code smell that couples tests to implementation
- **Prefer stubs, fakes, and test doubles** - test behavior without coupling
- Only replace external dependencies and side effects
- Create test doubles at architectural boundaries

#### Anti-Patterns to Avoid
- **Checking for specific strings in outputs** (brittle implementation coupling)
- **Excessive patching** (breaks with any refactoring)
- **Testing implementation details** instead of behavior
- **Complex test setup** (use builders/factories)

### Test Naming Convention
Pattern: `test_[unit_of_work]_[scenario]_[expected_outcome]`

Examples:
- `test_order_total_with_empty_cart_returns_zero`
- `test_user_login_with_invalid_credentials_raises_error`

### Project-Specific Test Commands
From current project CLAUDE.md:
- `make test` - All tests
- `uv run -m pytest tests/e2e/` - E2E validation
- `uv run mypy .` - Type checking
- Use project conventions over generic pytest commands

## 2. Python Conventions

### Package Management with uv
**Standard Commands**:
- `uv run <script>` - Run scripts
- `uv add <package>` - Add project dependencies  
- `uv tool install <tool>` - Global tool installation
- `uv run --with <package> <command>` - One-off usage

### Code Style Requirements

#### Type Hints
- **Use type hints everywhere possible**
- **Avoid `Any` as type hint** - be specific
- **Prefer dataclasses over dictionaries** for structured data
- **Strict typing with mypy** (from project config)

#### Import Organization 
**CRITICAL RULE**: **NO INLINE IMPORTS** - Place ALL imports at top of file
- Exception: Only when explicitly needed with comment explaining why
- Standard lib first, third-party second, project imports last
- This rule requires constant reinforcement

#### Multiple Edits Pattern for Code Organization
When adding functionality requiring imports and functions:
1. **Edit 1**: Add import at top of file
2. **Edit 2**: Add function definition at module level  
3. **Edit 3**: Add implementation/usage

**Prevents**: Nested functions and inline imports

#### Naming Conventions
- **snake_case** for variables, functions, file names
- **PascalCase** for classes
- Use descriptive names that reflect purpose

#### Function Design
- Write descriptive docstrings with Args and Returns sections
- **Avoid boolean parameters** - use enums for readability
- Follow single responsibility principle
- Prefer composition over inheritance

### CLI Tool Standards
- **Use Click for CLIs** - provides clean, composable patterns
- Prefer Click over argparse for new projects
- Support from ~/.claude/domains/python/cli/ patterns

### Data Structures
- **Prefer dataclasses over dictionaries** for structured data
- **Use enums over hardcoded strings** for type safety
- Use small, focused data structures

## 3. Writing Conventions

### Natural Human Communication
**Core Philosophy**: Transform AI-generated content into authentic, natural writing

#### LLM Buzzwords to NEVER Use
| Avoid | Use Instead |
|-------|-------------|
| comprehensive | complete, thorough |
| enhance | improve |
| utilize | use |
| robust | reliable, stable |
| leverage | use |
| facilitate | help, enable |
| pivotal | key, important |
| intricate | complex, detailed |

#### Commit Message Standards
- **Use imperative mood**: "Add feature" not "Added feature"
- **Be specific and concise**: Focus on what changed and why
- **Avoid LLM language**: No "enhance," "implement," "utilize"
- **Natural language**: Write like telling a colleague

**Good Examples**:
```
Fix login timeout issue when session expires
Add user preference toggle for dark mode  
Remove deprecated API calls from payment flow
```

**Avoid**:
```
❌ Enhance user authentication capabilities by implementing robust session management
❌ Utilize comprehensive error handling to significantly improve user experience
```

#### Documentation Anti-Patterns
- **Avoid bullet point symmetry** (4-6 identical bullets everywhere)
- **Mix paragraph lengths intentionally**
- **Vary bullet usage: 1-3 points max, not 4-6**
- **Some sections shouldn't use bullets at all**
- **Focus deeply rather than surface-level coverage**

## 4. TUI Conventions

### Architecture Patterns

#### Module-Based Design
Structure TUI apps as self-contained, reusable modules:
```python
class ModuleName(Container):
    def __init__(self, parent: Widget, **kwargs):
        super().__init__(**kwargs)
        self.page_parent = parent  # Communication channel
    
    def rebuild(self, focus: bool = False) -> None:
        """Rebuild module content efficiently"""
        pass
```

#### Reactive Properties
Use performance-optimized patterns:
```python
# Prevent unnecessary initial triggers
theme: reactive[str] = reactive("default", init=False)
```

#### Focus Management
- Implement visual hierarchy with focus containers
- Maintain focus across updates
- Support keyboard-centric navigation

### Testing Integration
- Use timeout-based detection for launch verification
- Test components in isolation when possible
- Mock external dependencies (file systems, networks)
- Verify keyboard navigation paths

## 5. Project-Specific Conventions (claude-code-autoyes)

### Technology Stack
- **Python 3.10+** (preferably 3.12)
- **Click** for CLI interfaces
- **Textual** for TUI components
- **pytest** with strict markers and coverage
- **mypy** with strict type checking
- **ruff** for formatting and linting

### Development Safety Nets
**CRITICAL**: Never bypass pre-commit hooks with `--no-verify`

Safety net layers:
1. **MyPy**: Type errors and attribute issues at commit time
2. **E2E Tests**: Runtime behavior and integration validation
3. **Pre-commit Hooks**: All checks before code enters repository

### Test Configuration
From pyproject.toml markers:
- `e2e`: End-to-end tests
- `smoke`: Smoke tests  
- `integration`: Integration tests
- `unit`: Unit tests

### Project Commands
- `make setup` - Build/setup
- `make check` - Run all checks
- `make test` - Test all
- `make mypy` - Type checking
- `uv run -m pytest tests/path::test_name` - Single test

## 6. Global Standards (Always Apply)

### AI Attribution Guidelines
- **Never reference Claude, Claude Code, or Anthropic** in git artifacts
- **No AI attribution or co-authorship** in commits
- Keep all AI assistance invisible

### MODEST Principles
- **Modularity**: Swappable, reusable components
- **Orthogonality**: Independent components
- **Dependency Injection**: Pass dependencies explicitly
- **Explicitness**: Clear intent, avoid magic
- **Single Responsibility**: One reason to change
- **Testability**: Design for easy testing

### Quality Standards
- **Simplicity over complexity**
- **Apply 80/20 principle**: Simple features get simple implementations
- **Avoid nested abstractions**: Keep ≤3 layers deep
- **Error handling**: Clear messages that guide users to success
- **Cognitive load awareness**: Design for first-time users

### Logging Standards
- Log after actions completed, not before
- Format: `log.info(f"Action description. [param1={value1}]")`
- INFO logs business-oriented, DEBUG technology-oriented

## Implementation Plan Integration

This research SUPERSEDES all other patterns and MUST be incorporated into any implementation plan. Key priorities:

1. **Follow progressive testing approach**: E2E → Smoke → Integration → Unit
2. **Use TUI launch detection pattern** for TUI testing
3. **Apply multiple edits pattern** for code organization
4. **Avoid all LLM buzzwords** in writing
5. **Implement strict type checking** with mypy
6. **Never bypass safety nets** (pre-commit hooks)
7. **Use Click for CLI**, **Textual for TUI**
8. **Test behavior, not implementation**
9. **Prefer test doubles over mocks**
10. **Follow natural writing patterns** for all communication

These conventions form the foundation for all development work in this project.