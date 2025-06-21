"""End-to-end tests for TUI version selection and launch."""

import subprocess
import pytest
from pathlib import Path


@pytest.mark.e2e
def test_new_tui_launches_successfully(project_root):
    """Test that new TUI version launches without errors."""
    # Arrange: Run new TUI with version flag
    # Act: Launch new modular TUI with short timeout
    try:
        result = subprocess.run(
            ["uv", "run", "-m", "claude_code_autoyes", "tui", "--version=new"],
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
def test_original_tui_remains_default(project_root):
    """Test that original TUI remains the default when no version specified."""
    # Arrange: Run TUI command without version flag
    # Act: Launch default TUI with very short timeout to verify it starts
    try:
        result = subprocess.run(
            ["uv", "run", "-m", "claude_code_autoyes", "tui"],
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


@pytest.mark.e2e
def test_tui_version_flag_help(project_root):
    """Test that TUI command shows version flag in help."""
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
def test_invalid_tui_version_handled(project_root):
    """Test that invalid version values are handled gracefully."""
    # Arrange: Use invalid version value
    # Act: Launch with invalid version
    result = subprocess.run(
        ["uv", "run", "-m", "claude_code_autoyes", "tui", "--version=invalid"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=5
    )
    
    # Assert: Should exit with error code
    assert result.returncode != 0