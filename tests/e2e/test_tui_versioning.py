"""End-to-end tests for TUI launch and functionality."""

import subprocess
import pytest


@pytest.mark.e2e
def test_tui_launches_successfully(project_root):
    """Test that TUI launches without errors."""
    # Arrange: Run TUI command
    # Act: Launch TUI with short timeout
    try:
        result = subprocess.run(
            ["uv", "run", "-m", "claude_code_autoyes", "tui"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=2  # Short timeout - if TUI launches, it will timeout here
        )
        # If it exits quickly without timeout, that's also fine
        assert result.returncode in [0, 130]
    except subprocess.TimeoutExpired:
        # Timeout means TUI launched successfully and is running
        assert True


@pytest.mark.e2e
def test_tui_help(project_root):
    """Test that TUI command shows help."""
    # Arrange: Request help for tui command
    # Act: Get help output
    result = subprocess.run(
        ["uv", "run", "-m", "claude_code_autoyes", "tui", "--help"],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    # Assert: Should show help without error
    assert result.returncode == 0


@pytest.mark.e2e
def test_tui_default_behavior(project_root):
    """Test that TUI runs when no subcommand is specified."""
    # Arrange: Run main command without subcommand (should default to TUI)
    # Act: Launch default command with short timeout
    try:
        result = subprocess.run(
            ["uv", "run", "-m", "claude_code_autoyes"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=2,
            input="\x03"  # Send Ctrl+C to exit quickly
        )
        # If it completes, that's fine
        assert result.returncode in [0, 130]
    except subprocess.TimeoutExpired:
        # Timeout means TUI launched successfully (which is what we want)
        assert True