"""End-to-end tests for TUI functionality and integration."""

import subprocess
import pytest


@pytest.mark.e2e
def test_tui_launches_successfully(project_root):
    """Test that TUI can launch without conflicts."""
    # Test TUI launch
    tui_launched = False
    try:
        result = subprocess.run(
            ["uv", "run", "-m", "claude_code_autoyes", "tui"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=2,
            input="\x03"  # Quick exit with Ctrl+C
        )
        tui_launched = result.returncode in [0, 130]
    except subprocess.TimeoutExpired:
        # Timeout means TUI launched successfully
        tui_launched = True
    
    # TUI should launch successfully
    assert tui_launched


@pytest.mark.e2e
def test_tui_integration_with_core_services(project_root):
    """Test that TUI properly integrates with existing core services."""
    # This test verifies the TUI can import and use core services
    # without causing import errors or circular dependencies
    
    result = subprocess.run(
        ["uv", "run", "python", "-c", 
         "from claude_code_autoyes.tui.app import ClaudeAutoYesApp; print('Import successful')"],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    # Should be able to import TUI app without errors
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