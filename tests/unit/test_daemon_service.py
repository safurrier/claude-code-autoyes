"""Unit tests for Python daemon service."""

import pytest
import re
from unittest.mock import Mock, patch

from claude_code_autoyes.core.daemon_service import DaemonService, PromptDetector


@pytest.mark.unit
def test_prompt_detector_identifies_claude_prompts():
    """Test that PromptDetector correctly identifies Claude prompt patterns."""
    detector = PromptDetector()
    
    # Test cases that should match Claude prompts
    prompt_cases = [
        "Do you want to continue with this operation?",
        "Would you like to proceed with the changes?",
        "Proceed? (y/n)",
        "❯ 1. Yes\n❯ 2. No",
        "Multiple lines\nDo you want to continue?\nMore text"
    ]
    
    for case in prompt_cases:
        assert detector.detect_claude_prompt(case), f"Should detect prompt in: {case}"
    
    # Test cases that should NOT match
    non_prompt_cases = [
        "Regular terminal output",
        "Some random text",
        "Error: command not found",
        ""
    ]
    
    for case in non_prompt_cases:
        assert not detector.detect_claude_prompt(case), f"Should NOT detect prompt in: {case}"


@pytest.mark.unit
def test_daemon_service_session_exists_check():
    """Test that DaemonService correctly checks if tmux sessions exist."""
    config = Mock()
    service = DaemonService(config)
    
    with patch('subprocess.run') as mock_run:
        # Test session exists
        mock_run.return_value = Mock(returncode=0)
        assert service._session_exists("test_session:0")
        mock_run.assert_called_with(
            ["tmux", "has-session", "-t", "test_session"],
            capture_output=True
        )
        
        # Test session does not exist
        mock_run.return_value = Mock(returncode=1)
        assert not service._session_exists("nonexistent:0")


@pytest.mark.unit
def test_daemon_service_capture_pane_content():
    """Test that DaemonService can capture tmux pane content."""
    config = Mock()
    service = DaemonService(config)
    
    with patch('subprocess.run') as mock_run:
        # Test successful capture
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Sample pane content\nDo you want to continue?"
        )
        
        content = service._capture_pane_content("session:0")
        assert content == "Sample pane content\nDo you want to continue?"
        mock_run.assert_called_with(
            ["tmux", "capture-pane", "-p", "-t", "session:0", "-S", "-10"],
            capture_output=True,
            text=True
        )
        
        # Test capture failure
        mock_run.return_value = Mock(returncode=1, stdout="")
        content = service._capture_pane_content("bad_session:0")
        assert content == ""


@pytest.mark.unit
def test_daemon_service_send_enter_key():
    """Test that DaemonService can send Enter key to tmux pane."""
    config = Mock()
    service = DaemonService(config)
    
    with patch('subprocess.run') as mock_run:
        # Test successful key send
        mock_run.return_value = Mock(returncode=0)
        result = service._send_enter_key("session:0")
        assert result is True
        mock_run.assert_called_with(
            ["tmux", "send-keys", "-t", "session:0", "Enter"],
            capture_output=True
        )
        
        # Test send failure
        mock_run.return_value = Mock(returncode=1)
        result = service._send_enter_key("bad_session:0")
        assert result is False


@pytest.mark.unit
def test_daemon_service_check_enabled_sessions():
    """Test that DaemonService correctly processes enabled sessions."""
    config = Mock()
    config.enabled_sessions = {"session1:0", "session2:1"}
    
    service = DaemonService(config)
    
    with patch.object(service, '_session_exists') as mock_exists, \
         patch.object(service, '_capture_pane_content') as mock_capture, \
         patch.object(service, '_send_enter_key') as mock_send:
        
        # Setup mocks
        mock_exists.return_value = True
        mock_capture.return_value = "Do you want to continue?"
        mock_send.return_value = True
        
        # Test check sessions
        service._check_enabled_sessions()
        
        # Verify interactions
        assert mock_exists.call_count == 2
        assert mock_capture.call_count == 2  
        assert mock_send.call_count == 2


@pytest.mark.unit
def test_daemon_service_monitoring_loop_stops_after_max_iterations():
    """Test that monitoring loop respects max_iterations parameter."""
    config = Mock()
    config.enabled_sessions = set()
    
    # Create service with very short sleep interval for faster tests
    service = DaemonService(config, sleep_interval=0.001)
    
    # Run only 2 iterations
    service.start_monitoring_loop(max_iterations=2)
    
    # Should have stopped after 2 iterations
    assert service.running is False


@pytest.mark.unit
def test_prompt_detector_patterns_are_case_insensitive():
    """Test that prompt detection works regardless of case."""
    detector = PromptDetector()
    
    # Test various cases
    cases = [
        "do you want to continue?",
        "DO YOU WANT TO CONTINUE?", 
        "Do You Want To Continue?",
        "would you like to proceed?",
        "WOULD YOU LIKE TO PROCEED?"
    ]
    
    for case in cases:
        assert detector.detect_claude_prompt(case), f"Should detect prompt in: {case}"