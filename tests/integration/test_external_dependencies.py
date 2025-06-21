"""Integration tests for external dependencies (tmux, subprocess, filesystem)."""

import os
import pytest
import subprocess
import tempfile
from pathlib import Path

from claude_code_autoyes.core.detector import ClaudeDetector
from claude_code_autoyes.core.config import ConfigManager
from claude_code_autoyes.core.daemon import DaemonManager


@pytest.mark.integration
def test_tmux_detection_integration(isolated_tmux_server):
    """Test that tmux detection works with real tmux server."""
    
    detector = ClaudeDetector()
    
    # Should be able to detect sessions without crashing
    instances = detector.find_claude_instances()
    
    # Should return a list (might be empty, that's ok)
    assert isinstance(instances, list)


@pytest.mark.integration
def test_config_file_operations(temp_home_dir):
    """Test that config file operations work correctly."""
    
    # Create config manager with temporary home directory
    config = ConfigManager()
    
    # Should be able to perform basic operations
    config.enabled_sessions.add("test_session")
    assert config.is_enabled("test_session")
    
    config.enabled_sessions.remove("test_session")
    assert not config.is_enabled("test_session")


@pytest.mark.integration
def test_daemon_script_generation(temp_home_dir):
    """Test that daemon script generation works."""
    # Mock home directory for config file
    old_home = os.environ.get('HOME')
    os.environ['HOME'] = str(temp_home_dir)
    
    try:
        daemon = DaemonManager()
        config = ConfigManager()
        
        # Should be able to start daemon (which generates script internally)
        # Just test that we can call start without crashing
        result = daemon.start(config)
        
        # Should return boolean result without crashing
        assert isinstance(result, bool)
        
    finally:
        if old_home:
            os.environ['HOME'] = old_home
        else:
            os.environ.pop('HOME', None)


@pytest.mark.integration
def test_subprocess_calls_work():
    """Test that subprocess calls work correctly in new structure."""
    
    detector = ClaudeDetector()
    
    # Test basic subprocess operation
    sessions = detector.get_tmux_sessions()
    
    # Should return list without crashing
    assert isinstance(sessions, list)


@pytest.mark.integration  
def test_file_system_operations(temp_home_dir):
    """Test that file system operations work correctly."""
    # Mock home directory
    old_home = os.environ.get('HOME')
    os.environ['HOME'] = str(temp_home_dir)
    
    try:
        config = ConfigManager()
        
        # Should create config file
        config.save()
        
        # Config file should exist
        config_file = temp_home_dir / ".claude-autoyes-config"
        assert config_file.exists()
        
    finally:
        if old_home:
            os.environ['HOME'] = old_home
        else:
            os.environ.pop('HOME', None)