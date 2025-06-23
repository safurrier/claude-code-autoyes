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

# CI/CD Debugging

## Checking PR Status
When you have an open PR, use these commands to monitor CI status:

```bash
# List open PRs
gh pr list

# Check specific PR status and CI results
gh pr checks <PR_NUMBER>

# View detailed logs for failed runs
gh run view <RUN_ID> --log-failed

# View full run details
gh run view <RUN_ID>
```

## Common CI Failures

### Test Failures
1. **Check local vs CI differences**:
   ```bash
   # Run the same tests locally that failed in CI
   uv run -m pytest tests/e2e/ -v

   # Compare with CI command from .github/workflows/tests.yml
   uv run -m pytest tests --cov=claude_code_autoyes --cov-report=term-missing
   ```

2. **Environment differences**: CI runs on Ubuntu, local may be macOS
3. **Timing issues**: CI may have different timeout behavior
4. **Dependencies**: Check if CI has all required dependencies

## CI Debug Loop
When CI tests are failing, use this iterative debugging workflow:

```bash
# 1. Make your changes and test locally first
uv run -m pytest tests/path/to/failing/test.py -v

# 2. Commit and push changes
git add .
git commit -m "fix: Attempt to resolve CI test failures"
git push

# 3. Wait for CI to run (2-3 minutes)
sleep 180

# 4. Check CI status
gh pr checks <PR_NUMBER>

# 5. If still failing, analyze and fix
gh run view --log-failed  # Review specific failures

# 6. Amend the commit with fixes and force push
git add .
git commit --amend --no-edit
git push --force-with-lease

# 7. Repeat steps 3-6 until CI passes
```

**Key Points:**
- Always test locally before pushing
- Use `--amend` to keep commit history clean
- `--force-with-lease` is safer than `--force`
- Wait adequate time between pushes for CI to complete

## PR Review Comments

To view PR review comments including line-specific feedback:

```bash
# View PR with general comments
gh pr view <PR_NUMBER> --comments

# Get detailed review comments via API (line-specific)
gh api repos/OWNER/REPO/pulls/<PR_NUMBER>/comments

# Get review-level comments
gh api repos/OWNER/REPO/pulls/<PR_NUMBER>/reviews
```

**Example workflow for addressing PR feedback:**
1. `gh pr view 13 --comments` - See general comments
2. `gh api repos/safurrier/ai-sleepwalker/pulls/13/comments` - Get line-specific feedback
3. Address each comment by fixing the code issues
4. Use the CI debug loop above to test fixes


## Debugging Strategy
1. **Reproduce locally**: Always run the failing command locally first
2. **Check commit**: Ensure PR is testing your latest code
3. **Review logs**: Use `gh run view --log-failed` for specific errors
4. **Compare environments**: CI=Ubuntu, local=macOS, dependencies may differ
5. **Test incrementally**: Run individual test files to isolate issues
