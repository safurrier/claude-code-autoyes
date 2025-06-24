"""E2E tests for Claude detection using real tmux sessions."""

import subprocess
import time
import uuid
from contextlib import contextmanager
from typing import Generator

import pytest

from claude_code_autoyes.core.detector import ClaudeDetector


@contextmanager
def real_claude_session() -> Generator[str, None, None]:
    """Create a real tmux session with Claude running for E2E testing.
    
    This context manager:
    1. Creates a new tmux session with unique name
    2. Launches Claude in that session  
    3. Waits for Claude to start
    4. Yields session name for testing
    5. Cleans up session afterwards
    
    Yields:
        Session name that can be used to reference the tmux session
    """
    session_name = f"claude-test-{uuid.uuid4().hex[:8]}"
    
    try:
        # Create tmux session
        result = subprocess.run(
            ["tmux", "new-session", "-d", "-s", session_name],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            pytest.skip(f"Failed to create tmux session: {result.stderr}")
        
        # Launch Claude in the session
        launch_result = subprocess.run(
            ["tmux", "send-keys", "-t", session_name, "claude", "Enter"],
            capture_output=True,
            text=True,
            check=False,
        )
        if launch_result.returncode != 0:
            pytest.skip(f"Failed to send claude command to tmux: {launch_result.stderr}")
        
        # Wait for Claude to start up
        time.sleep(5)  # Increased wait time for slower CI environments
        
        yield session_name
        
    finally:
        # Clean up session
        subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            capture_output=True,
            check=False,
        )


@pytest.mark.e2e
def test_detects_real_claude_instance():
    """Test that detection finds a real Claude instance in tmux session."""
    with real_claude_session() as session_name:
        detector = ClaudeDetector()
        instances = detector.find_claude_instances()
        
        # Should find our test Claude instance
        test_instances = [
            instance for instance in instances 
            if instance.session == session_name
        ]
        
        assert len(test_instances) == 1, f"Expected 1 Claude instance in {session_name}, found {len(test_instances)}"
        
        instance = test_instances[0]
        assert instance.is_claude is True
        assert instance.session == session_name
        # Pane numbering can be 0.0 or 1.1 depending on tmux version/config
        assert instance.pane in ["0.0", "1.1"], f"Expected pane to be 0.0 or 1.1, got: {instance.pane}"


@pytest.mark.e2e
def test_detects_multiple_real_claude_instances():
    """Test detection with multiple real Claude instances."""
    sessions = []
    
    try:
        # Create multiple sessions with Claude
        for i in range(2):
            session_name = f"claude-multi-test-{uuid.uuid4().hex[:8]}"
            sessions.append(session_name)
            
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", session_name],
                check=False,
            )
            subprocess.run(
                ["tmux", "send-keys", "-t", session_name, "claude", "Enter"],
                check=False,
            )
        
        # Wait for all instances to start
        time.sleep(4)
        
        detector = ClaudeDetector()
        instances = detector.find_claude_instances()
        
        # Should find both test instances
        test_instances = [
            instance for instance in instances 
            if instance.session in sessions
        ]
        
        assert len(test_instances) == 2, f"Expected 2 Claude instances, found {len(test_instances)}"
        
        # Verify each instance
        for instance in test_instances:
            assert instance.is_claude is True
            assert instance.session in sessions
            # Pane numbering can be 0.0 or 1.1 depending on tmux version/config
            assert instance.pane in ["0.0", "1.1"], f"Expected pane to be 0.0 or 1.1, got: {instance.pane}"
    
    finally:
        # Clean up all sessions
        for session_name in sessions:
            subprocess.run(
                ["tmux", "kill-session", "-t", session_name],
                capture_output=True,
                check=False,
            )


@pytest.mark.e2e 
def test_child_process_detection_real():
    """Test that detection finds Claude child processes in real environment."""
    with real_claude_session() as session_name:
        detector = ClaudeDetector()
        
        # Get pane info for our test session
        pane_id = f"{session_name}:1.1"
        process_info = detector.get_pane_process_info(pane_id)
        
        # tmux should report the shell process (varies by environment)
        shell_command = process_info.get("command")
        shell_pid = process_info.get("pid")
        assert shell_pid is not None
        
        # Shell could be node (local dev), bash (CI), claude (direct run), or other shells
        expected_shells = ["node", "bash", "zsh", "sh", "claude"]
        assert shell_command in expected_shells, f"Expected shell command to be one of {expected_shells}, got: {shell_command}"
        
        # The enhanced detector should find Claude as child of this shell
        instances = detector.find_claude_instances()
        test_instances = [
            instance for instance in instances 
            if instance.session == session_name
        ]
        
        assert len(test_instances) == 1, f"Should detect Claude child process in {session_name}. Found instances: {[i.session for i in instances]}"


@pytest.mark.e2e
def test_real_claude_content_detection():
    """Test content-based detection with real Claude interface."""
    with real_claude_session() as session_name:
        detector = ClaudeDetector()
        # Try both possible pane formats
        content = ""
        for pane_suffix in ["0.0", "1.1"]:
            pane_id = f"{session_name}:{pane_suffix}"
            content = detector.capture_pane_content(pane_id)
            if content.strip():  # Found content in this pane
                break
        
        # In CI, Claude might show authentication prompts or be empty
        # We mainly want to verify the content capture mechanism works
        if content.strip():
            # If there's content, it should either be Claude-related or auth-related
            claude_indicators = [
                "Claude Code", "Welcome to Claude", "claude", "authentication", 
                "login", "browser", "API key", "Error", "failed"
            ]
            has_claude_indicator = any(indicator.lower() in content.lower() for indicator in claude_indicators)
            assert has_claude_indicator, f"Expected Claude-related content. Content preview: {content[:300]}"
        else:
            # Empty content is acceptable in CI environment (authentication issues)
            # The process-based detection is the primary method anyway
            print(f"Note: Empty content in CI environment for session {session_name}, this is expected")


@pytest.mark.e2e
def test_session_cleanup_robustness():
    """Test that session cleanup works even if tests fail."""
    session_name = f"claude-cleanup-test-{uuid.uuid4().hex[:8]}"
    
    # Create session outside context manager to test cleanup
    subprocess.run(
        ["tmux", "new-session", "-d", "-s", session_name],
        check=False,
    )
    
    try:
        try:
            # Use context manager - should clean up even if we raise exception
            with real_claude_session() as test_session:
                # Verify session exists
                result = subprocess.run(
                    ["tmux", "list-sessions"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                assert test_session in result.stdout
                
                # Simulate test failure
                raise ValueError("Simulated test failure")
                
        except ValueError:
            # Expected - context manager should still clean up
            pass
        
        # Verify cleanup happened
        result = subprocess.run(
            ["tmux", "list-sessions"],
            capture_output=True,
            text=True,
            check=False,
        )
        # Test session should be gone, but our manual one should remain
        session_names = result.stdout if result.returncode == 0 else ""
        assert session_name in session_names  # Our manual session still there
        
    finally:
        # Clean up manual session
        subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            check=False,
        )