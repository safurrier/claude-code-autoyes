"""Unit tests for Python daemon service."""

import pytest
from dataclasses import dataclass
from typing import Set, Dict

from claude_code_autoyes.core.daemon_service import DaemonService, PromptDetector


@dataclass
class PromptTestCase:
    """Test case for prompt detection."""
    name: str
    content: str
    should_detect: bool


class FakeTmuxService:
    """Test double for tmux operations."""
    
    def __init__(self):
        self.existing_sessions: Set[str] = set()
        self.pane_content: Dict[str, str] = {}
        self.keys_sent: list = []
        self.command_failures: Set[str] = set()
    
    def session_exists(self, session_name: str) -> bool:
        return session_name in self.existing_sessions
    
    def capture_pane_content(self, session_pane: str) -> str:
        if session_pane in self.command_failures:
            return ""
        return self.pane_content.get(session_pane, "")
    
    def send_enter_key(self, session_pane: str) -> bool:
        if session_pane in self.command_failures:
            return False
        self.keys_sent.append(session_pane)
        return True


class StubConfig:
    """Test double for configuration."""
    
    def __init__(self, enabled_sessions: Set[str] = None):
        self.enabled_sessions = enabled_sessions or set()


class DaemonServiceWithFakes(DaemonService):
    """Testable version of DaemonService with injected dependencies."""
    
    def __init__(self, config, tmux_service: FakeTmuxService, sleep_interval: float = 0.001):
        super().__init__(config, sleep_interval)
        self.tmux_service = tmux_service
    
    def _session_exists(self, session_pane: str) -> bool:
        session_name = session_pane.split(':')[0]
        return self.tmux_service.session_exists(session_name)
    
    def _capture_pane_content(self, session_pane: str) -> str:
        return self.tmux_service.capture_pane_content(session_pane)
    
    def _send_enter_key(self, session_pane: str) -> bool:
        return self.tmux_service.send_enter_key(session_pane)


# Table-driven test data
PROMPT_TEST_CASES = [
    PromptTestCase("confirmation_question", "Do you want to continue?", True),
    PromptTestCase("preference_question", "Would you like to proceed?", True),
    PromptTestCase("proceed_question", "Proceed? (y/n)", True),
    PromptTestCase("menu_option", "❯ 1. Yes\n❯ 2. No", True),
    PromptTestCase("multiline_prompt", "Multiple lines\nDo you want to continue?\nMore text", True),
    PromptTestCase("case_insensitive_lower", "do you want to continue?", True),
    PromptTestCase("case_insensitive_upper", "DO YOU WANT TO CONTINUE?", True),
    PromptTestCase("regular_output", "Regular terminal output", False),
    PromptTestCase("error_message", "Error: command not found", False),
    PromptTestCase("empty_content", "", False),
    PromptTestCase("random_text", "Some random text", False),
]


@pytest.mark.parametrize("case", PROMPT_TEST_CASES)
def test_prompt_detector_identifies_patterns(case: PromptTestCase):
    """Test prompt detection with various input scenarios."""
    detector = PromptDetector()
    result = detector.detect_claude_prompt(case.content)
    assert result == case.should_detect, f"Failed for {case.name}: '{case.content}'"


@pytest.mark.unit
def test_daemon_skips_nonexistent_sessions():
    """Test that daemon skips sessions that don't exist."""
    config = StubConfig(enabled_sessions={"nonexistent:0"})
    tmux_service = FakeTmuxService()
    service = DaemonServiceWithFakes(config, tmux_service)
    
    # Session doesn't exist
    service._check_enabled_sessions()
    
    # No keys should be sent
    assert len(tmux_service.keys_sent) == 0


@pytest.mark.unit  
def test_daemon_processes_active_sessions_with_prompts():
    """Test that daemon responds to prompts in active sessions."""
    config = StubConfig(enabled_sessions={"active_session:0"})
    tmux_service = FakeTmuxService()
    
    # Set up session with prompt content
    tmux_service.existing_sessions.add("active_session")
    tmux_service.pane_content["active_session:0"] = "Do you want to continue?"
    
    service = DaemonServiceWithFakes(config, tmux_service)
    service._check_enabled_sessions()
    
    # Should have sent Enter key
    assert "active_session:0" in tmux_service.keys_sent


@pytest.mark.unit
def test_daemon_ignores_sessions_without_prompts():
    """Test that daemon ignores sessions with no prompt content."""
    config = StubConfig(enabled_sessions={"quiet_session:0"})
    tmux_service = FakeTmuxService()
    
    # Set up session with regular content (no prompts)
    tmux_service.existing_sessions.add("quiet_session")
    tmux_service.pane_content["quiet_session:0"] = "Regular command output"
    
    service = DaemonServiceWithFakes(config, tmux_service)
    service._check_enabled_sessions()
    
    # No keys should be sent
    assert len(tmux_service.keys_sent) == 0


@pytest.mark.unit
def test_daemon_handles_multiple_sessions():
    """Test that daemon processes multiple enabled sessions."""
    config = StubConfig(enabled_sessions={"session1:0", "session2:1"})
    tmux_service = FakeTmuxService()
    
    # Set up multiple sessions
    tmux_service.existing_sessions.update(["session1", "session2"])
    tmux_service.pane_content["session1:0"] = "Would you like to proceed?"
    tmux_service.pane_content["session2:1"] = "Regular output"
    
    service = DaemonServiceWithFakes(config, tmux_service)
    service._check_enabled_sessions()
    
    # Only session with prompt should get response
    assert "session1:0" in tmux_service.keys_sent
    assert "session2:1" not in tmux_service.keys_sent
    assert len(tmux_service.keys_sent) == 1


@pytest.mark.unit
def test_daemon_handles_command_failures():
    """Test that daemon gracefully handles tmux command failures."""
    config = StubConfig(enabled_sessions={"failing_session:0"})
    tmux_service = FakeTmuxService()
    
    # Set up session that exists but has command failures
    tmux_service.existing_sessions.add("failing_session")
    tmux_service.command_failures.add("failing_session:0")
    
    service = DaemonServiceWithFakes(config, tmux_service)
    service._check_enabled_sessions()
    
    # Should not crash and no keys sent
    assert len(tmux_service.keys_sent) == 0


@pytest.mark.unit
def test_monitoring_loop_stops_after_max_iterations():
    """Test that monitoring loop respects max_iterations parameter."""
    config = StubConfig()
    tmux_service = FakeTmuxService()
    service = DaemonServiceWithFakes(config, tmux_service)
    
    # Run only 2 iterations
    service.start_monitoring_loop(max_iterations=2)
    
    # Should have stopped after 2 iterations
    assert service.running is False


@pytest.mark.unit
def test_monitoring_loop_can_be_stopped():
    """Test that monitoring loop can be stopped externally."""
    config = StubConfig()
    tmux_service = FakeTmuxService()
    service = DaemonServiceWithFakes(config, tmux_service)
    
    # Start and immediately stop
    service.running = True
    service.stop()
    
    assert service.running is False