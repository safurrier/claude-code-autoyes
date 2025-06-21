"""End-to-end tests for TUI feature parity between versions."""

import subprocess
import pytest
from pathlib import Path


@pytest.mark.e2e
def test_both_tui_versions_launch(project_root):
    """Test that both TUI versions can launch without conflicts."""
    # Test original TUI
    original_launched = False
    try:
        original_result = subprocess.run(
            ["uv", "run", "-m", "claude_code_autoyes", "tui"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=2,
            input="\x03"  # Quick exit with Ctrl+C
        )
        original_launched = original_result.returncode in [0, 130]
    except subprocess.TimeoutExpired:
        # Timeout means TUI launched successfully
        original_launched = True
    
    # Test new TUI
    new_launched = False
    try:
        new_result = subprocess.run(
            ["uv", "run", "-m", "claude_code_autoyes", "tui", "--version=new"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=2,
            input="\x03"  # Quick exit with Ctrl+C
        )
        new_launched = new_result.returncode in [0, 130]
    except subprocess.TimeoutExpired:
        # Timeout means TUI launched successfully
        new_launched = True
    
    # Both should launch successfully
    assert original_launched
    assert new_launched


@pytest.mark.e2e
def test_tui_integration_with_core_services(project_root):
    """Test that new TUI properly integrates with existing core services."""
    # This test verifies the new TUI can import and use core services
    # without causing import errors or circular dependencies
    
    result = subprocess.run(
        ["uv", "run", "python", "-c", 
         "from claude_code_autoyes.tui.app import ClaudeAutoYesNewApp; print('Import successful')"],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    # Should be able to import new TUI app without errors
    assert result.returncode == 0


@pytest.mark.e2e 
def test_theme_system_loads_without_errors(project_root):
    """Test that theme system can be imported and initialized."""
    result = subprocess.run(
        ["uv", "run", "python", "-c",
         "from claude_code_autoyes.tui.themes import THEMES; print(f'Theme system OK: {list(THEMES.keys())}')"],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    # Should load theme system without errors
    assert result.returncode == 0