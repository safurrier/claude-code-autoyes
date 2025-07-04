"""Smoke tests for module imports and basic structure."""

import pytest
import subprocess

from claude_code_autoyes.core.models import ClaudeInstance
from claude_code_autoyes.core.detector import ClaudeDetector
from claude_code_autoyes.core.config import ConfigManager
from claude_code_autoyes.core.daemon import DaemonManager
# Import from tui package since we now have a modular structure 
from claude_code_autoyes.tui import ClaudeAutoYesApp
from claude_code_autoyes.cli import cli


@pytest.mark.smoke
def test_core_models_import():
    """Test that core models can be imported from new module structure."""
    
    # Test basic instantiation
    instance = ClaudeInstance("test_session", "0", True)
    assert instance.session == "test_session"
    assert instance.pane == "0"
    assert instance.is_claude is True


@pytest.mark.smoke
def test_core_detector_import():
    """Test that ClaudeDetector can be imported and instantiated."""
    
    detector = ClaudeDetector()
    assert detector is not None


@pytest.mark.smoke
def test_core_config_import():
    """Test that ConfigManager can be imported and instantiated."""
    
    # Should be able to create config manager
    config = ConfigManager()
    assert config is not None


@pytest.mark.smoke
def test_core_daemon_import():
    """Test that DaemonManager can be imported and instantiated."""
    
    daemon = DaemonManager()
    assert daemon is not None


@pytest.mark.smoke
def test_tui_import():
    """Test that TUI application can be imported."""
    
    # Should be able to import the TUI app class
    assert ClaudeAutoYesApp is not None


@pytest.mark.smoke
def test_cli_import():
    """Test that CLI can be imported."""
    
    # Should be able to import the main CLI function
    assert cli is not None


@pytest.mark.smoke
def test_module_execution_with_help_flag_succeeds():
    """Test that module can be executed directly."""
    
    result = subprocess.run(
        ["uv", "run", "-m", "claude_code_autoyes", "--help"],
        capture_output=True,
        text=True
    )
    
    # Should be able to run the module and get help
    assert result.returncode == 0
    # Test behavior: module execution succeeds and produces output
    assert len(result.stdout) > 0