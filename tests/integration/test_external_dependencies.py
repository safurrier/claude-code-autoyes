"""Integration tests for external dependencies (tmux, subprocess, filesystem)."""

import pytest
import subprocess
import tempfile
from pathlib import Path


@pytest.mark.integration
def test_tmux_detection_integration(isolated_tmux_server):
    """Test that tmux detection works with real tmux server."""
    from claude_code_autoyes.core.detector import ClaudeDetector
    
    detector = ClaudeDetector()
    
    # Should be able to detect sessions without crashing
    instances = detector.find_claude_instances()
    
    # Should return a list (might be empty, that's ok)
    assert isinstance(instances, list)


@pytest.mark.integration
def test_config_file_operations(temp_home_dir):
    """Test that config file operations work correctly."""
    from claude_code_autoyes.core.config import ConfigManager
    
    # Create config manager with temporary home directory
    config = ConfigManager()
    
    # Should be able to perform basic operations
    config.enable_session("test_session")
    assert config.is_session_enabled("test_session")
    
    config.disable_session("test_session")
    assert not config.is_session_enabled("test_session")


@pytest.mark.integration
def test_daemon_script_generation():
    """Test that daemon script generation works."""
    from claude_code_autoyes.core.daemon import DaemonManager
    
    daemon = DaemonManager()
    
    # Should be able to generate daemon script
    script_content = daemon._generate_daemon_script(["test_session"])
    
    # Basic validation - should contain bash and python
    assert "#!/bin/bash" in script_content
    assert "python3" in script_content


@pytest.mark.integration
def test_subprocess_calls_work():
    """Test that subprocess calls work correctly in new structure."""
    from claude_code_autoyes.core.detector import ClaudeDetector
    
    detector = ClaudeDetector()
    
    # Test basic subprocess operation
    sessions = detector._get_tmux_sessions()
    
    # Should return list without crashing
    assert isinstance(sessions, list)


@pytest.mark.integration  
def test_file_system_operations(temp_home_dir):
    """Test that file system operations work correctly."""
    from claude_code_autoyes.core.config import ConfigManager
    
    # Mock home directory
    import os
    old_home = os.environ.get('HOME')
    os.environ['HOME'] = str(temp_home_dir)
    
    try:
        config = ConfigManager()
        
        # Should create config file
        config.save_config()
        
        # Config file should exist
        config_file = temp_home_dir / ".claude-autoyes-config"
        assert config_file.exists()
        
    finally:
        if old_home:
            os.environ['HOME'] = old_home
        else:
            os.environ.pop('HOME', None)