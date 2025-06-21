.PHONY: compile-deps setup clean-pyc clean-test clean-venv clean test mypy lint format check clean-example docs-install docs-build docs-serve docs-check docs-clean dev-env refresh-containers rebuild-images build-image push-image
.PHONY: dev-install dev-uninstall dev-test-pr dev-run dev-daemon-test dev-logs dev-daemon-stop dev-status dev-tmux-setup

# Module name - will be updated by init script
MODULE_NAME := claude_code_autoyes

help:  ## Show this help message
	@echo "📚 Available Make Commands"
	@echo "=========================="
	@echo ""
	@echo "🏗️  Setup & Dependencies:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(setup|install|compile)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🧪 Testing & Quality:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(test|mypy|lint|format|check)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📖 Documentation:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "docs-" | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔧 Development & Testing:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "dev-" | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🧹 Cleanup:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "clean" | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "💡 Quick Start for PR Testing:"
	@echo "  make dev-test-pr PR=4    # Test PR #4"
	@echo "  make dev-daemon-test     # Test daemon functionality"
	@echo "  make dev-logs           # Watch daemon logs"
	@echo "  make dev-uninstall      # Clean up"

# Development Setup
#################
compile-deps:  # Compile dependencies from pyproject.toml
	uv pip compile pyproject.toml -o requirements.txt
	uv pip compile pyproject.toml --extra dev -o requirements-dev.txt

PYTHON_VERSION ?= 3.12

ensure-uv:  # Install uv if not present
	@which uv > /dev/null || (curl -LsSf https://astral.sh/uv/install.sh | sh)

setup: ensure-uv compile-deps ensure-scripts  # Install dependencies
	UV_PYTHON_VERSION=$(PYTHON_VERSION) uv venv
	UV_PYTHON_VERSION=$(PYTHON_VERSION) uv pip sync requirements.txt requirements-dev.txt
	$(MAKE) install-hooks

install-hooks:  # Install pre-commit hooks if in a git repo with hooks configured
	@if [ -d .git ] && [ -f .pre-commit-config.yaml ]; then \
		echo "Installing pre-commit hooks..."; \
		uv run pre-commit install; \
	fi

ensure-scripts:  # Ensure scripts directory exists and files are executable
	mkdir -p scripts
	chmod +x scripts/*.py

# Cleaning
#########
clean-pyc:  # Remove Python compilation artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:  # Remove test and coverage artifacts
	rm -f .coverage
	rm -f .coverage.*

clean-venv:  # Remove virtual environment
	rm -rf .venv

clean: clean-pyc clean-test clean-venv

# Testing and Quality Checks
#########################
test: setup  # Run pytest with coverage
	uv run -m pytest tests --cov=$(MODULE_NAME) --cov-report=term-missing

test-smoke: setup  # Run smoke tests only (fast)
	uv run -m pytest tests/smoke/ -v -x

test-e2e: setup  # Run end-to-end tests
	uv run -m pytest tests/e2e/ -v

test-integration: setup  # Run integration tests  
	uv run -m pytest tests/integration/ -v

test-unit: setup  # Run unit tests
	uv run -m pytest tests/unit/ -v

mypy: setup  # Run type checking
	uv run -m mypy $(MODULE_NAME)

lint: setup  # Run ruff linter with auto-fix
	uv run -m ruff check --fix $(MODULE_NAME)

format: setup  # Run ruff formatter
	uv run -m ruff format $(MODULE_NAME)

check: setup lint format test mypy  # Run all quality checks

# Documentation
###############
DOCS_PORT ?= 8000

docs-install: setup  ## Install documentation dependencies
	@echo "Installing documentation dependencies..."
	uv sync --group dev
	@echo "Documentation dependencies installed"

docs-build: docs-install  ## Build documentation site
	@echo "Building documentation..."
	uv run mkdocs build --strict
	@echo "Documentation built successfully"
	@echo "📄 Site location: site/"
	@echo "🌐 Open site/index.html in your browser to view"

docs-serve: docs-install  ## Serve documentation locally with live reload
	@echo "Starting documentation server with live reload..."
	@echo "📍 Documentation will be available at:"
	@echo "   - Local: http://localhost:$(DOCS_PORT)"
	@echo "🔄 Changes will auto-reload (press Ctrl+C to stop)"
	@echo ""
	@echo "💡 To use a different port: make docs-serve DOCS_PORT=9999"
	uv run mkdocs serve --dev-addr 0.0.0.0:$(DOCS_PORT)

docs-check: docs-build  ## Check documentation build and links
	@echo "Checking documentation..."
	@echo "📊 Site size: $$(du -sh site/ | cut -f1)"
	@echo "📄 Pages built: $$(find site/ -name "*.html" | wc -l)"
	@echo "🔗 Checking for common issues..."
	@if grep -r "404" site/ >/dev/null 2>&1; then \
		echo "⚠️  Found potential 404 errors"; \
	else \
		echo "✅ No obvious 404 errors found"; \
	fi
	@if find site/ -name "*.html" -size 0 | grep -q .; then \
		echo "⚠️  Found empty HTML files"; \
		find site/ -name "*.html" -size 0; \
	else \
		echo "✅ No empty HTML files found"; \
	fi
	@echo "Documentation check complete"

docs-clean:  ## Clean documentation build files
	@echo "Cleaning documentation build files..."
	rm -rf site/
	rm -rf .cache/
	@echo "Documentation cleaned"

# Project Management
##################
clean-example:  # Remove example code (use this to start your own project)
	rm -rf $(MODULE_NAME)/example.py tests/test_example.py
	touch $(MODULE_NAME)/__init__.py tests/__init__.py

init: setup  # Initialize a new project
	uv run python scripts/init_project.py

# Docker
########
IMAGE_NAME = container-registry.io/python-collab-template
IMAGE_TAG = latest

dev-env: refresh-containers
	@echo "Spinning up a dev environment ."
	@docker compose -f docker/docker-compose.yml down
	@docker compose -f docker/docker-compose.yml up -d dev
	@docker exec -ti composed_dev /bin/bash

refresh-containers:
	@echo "Rebuilding containers..."
	@docker compose -f docker/docker-compose.yml build

rebuild-images:
	@echo "Rebuilding images with the --no-cache flag..."
	@docker compose -f docker/docker-compose.yml build --no-cache

build-image:
	@echo Building dev image and tagging as ${IMAGE_NAME}:${IMAGE_TAG}
	@docker compose -f docker/docker-compose.yml down
	@docker compose -f docker/docker-compose.yml up -d dev
	@docker tag dev ${IMAGE_NAME}:${IMAGE_TAG}

push-image: build-image
	@echo Pushing image to container registry
	@docker push ${IMAGE_NAME}:${IMAGE_TAG}

# Development & Testing Commands
###############################
dev-install: setup  ## Install current branch as test tool
	@echo "Installing current branch as test tool..."
	uv tool install --from . --reinstall claude-code-autoyes
	@echo "✅ Installed as claude-code-autoyes"
	@echo "💡 Usage: claude-code-autoyes --help"
	@echo "⚠️  Note: This replaces any existing claude-code-autoyes installation"

dev-uninstall:  ## Remove test tool installation
	@echo "Uninstalling claude-code-autoyes..."
	uv tool uninstall claude-code-autoyes || echo "Tool not installed"
	@echo "✅ Uninstalled claude-code-autoyes"

dev-test-pr:  ## Test a specific PR (usage: make dev-test-pr PR=4)
	@if [ -z "$(PR)" ]; then \
		echo "❌ Please specify PR number: make dev-test-pr PR=4"; \
		exit 1; \
	fi
	@echo "🔄 Fetching PR $(PR)..."
	git fetch origin pull/$(PR)/head:test-pr-$(PR)
	git checkout test-pr-$(PR)
	@echo "📦 Installing PR $(PR) as test tool..."
	$(MAKE) dev-install
	@echo "✅ PR $(PR) ready for testing"
	@echo "💡 Run: claude-code-autoyes --help"
	@echo "🧹 Clean up with: make dev-uninstall && git checkout main"

dev-run:  ## Run current code without installing
	@echo "🚀 Running current code directly..."
	uv run claude-code-autoyes.py --help
	@echo ""
	@echo "💡 Available commands:"
	@echo "  uv run claude-code-autoyes.py status"
	@echo "  uv run -m claude_code_autoyes status"

dev-status:  ## Show current development status
	@echo "📋 Development Status"
	@echo "====================="
	@echo "📂 Current branch: $$(git branch --show-current)"
	@echo "🔄 Git status:"
	@git status --porcelain | head -10
	@echo ""
	@echo "🔧 Tool installations:"
	@uv tool list | grep claude-code-autoyes || echo "  No test tools installed"
	@echo ""
	@echo "📊 Daemon status:"
	@claude-code-autoyes status 2>/dev/null || uv run claude-code-autoyes.py status

dev-tmux-setup:  ## Set up test tmux session for daemon testing
	@echo "🖥️  Setting up test tmux session..."
	@if ! command -v tmux >/dev/null 2>&1; then \
		echo "❌ tmux not found. Install with: brew install tmux"; \
		exit 1; \
	fi
	tmux kill-session -t claude-test 2>/dev/null || true
	tmux new-session -d -s claude-test -x 120 -y 30
	tmux send-keys -t claude-test 'echo "Test session ready for Claude auto-yes testing"' Enter
	@echo "✅ Test tmux session 'claude-test' created"
	@echo "💡 Attach with: tmux attach -t claude-test"
	@echo "🧹 Clean up with: tmux kill-session -t claude-test"

dev-daemon-test: dev-tmux-setup  ## Test daemon with simulated prompts
	@echo "🤖 Testing daemon with simulated prompts..."
	@echo "🚀 Starting daemon (if not running)..."
	@claude-code-autoyes enable-all || true
	@claude-code-autoyes daemon start || true
	@echo "📋 Daemon status:"
	@claude-code-autoyes daemon status
	@echo ""
	@echo "🔍 To test manually:"
	@echo "  1. tmux attach -t claude-test"
	@echo "  2. ./scripts/simulate-claude-prompt.sh"
	@echo "  3. Watch for auto-response in: make dev-logs"

dev-logs:  ## Tail daemon logs
	@echo "📄 Tailing daemon logs (Ctrl+C to stop)..."
	@if [ -f /tmp/claude-autoyes.log ]; then \
		tail -f /tmp/claude-autoyes.log; \
	else \
		echo "❌ No log file found at /tmp/claude-autoyes.log"; \
		echo "💡 Start daemon with: claude-code-autoyes daemon start"; \
	fi

dev-daemon-stop:  ## Stop daemon and clean up test session
	@echo "🛑 Stopping daemon and cleaning up..."
	@claude-code-autoyes daemon stop 2>/dev/null || echo "Daemon not running"
	@tmux kill-session -t claude-test 2>/dev/null || echo "Test session not found"
	@echo "✅ Cleanup complete"
