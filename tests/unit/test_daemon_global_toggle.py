"""Unit tests for DaemonService global toggle functionality."""

import pytest
from typing import Set

from claude_code_autoyes.core.daemon_service import DaemonService


class FakeConfigManager:
    """Test double for ConfigManager with controllable auto_yes_enabled."""
    
    def __init__(self, auto_yes_enabled: bool = True):
        self.enabled_sessions: Set[str] = set()
        self.auto_yes_enabled = auto_yes_enabled
        self.daemon_enabled = False
        self.refresh_interval = 1.0


@pytest.mark.unit
def test_daemon_should_process_session_when_globally_enabled():
    """Daemon processes sessions when auto_yes_enabled=True."""
    config = FakeConfigManager(auto_yes_enabled=True)
    config.enabled_sessions.add("test:0")
    
    daemon = DaemonService(config)
    assert daemon.should_process_session("test:0") is True


@pytest.mark.unit
def test_daemon_skips_session_when_globally_disabled():
    """Daemon ignores sessions when auto_yes_enabled=False."""
    config = FakeConfigManager(auto_yes_enabled=False)
    config.enabled_sessions.add("test:0")
    
    daemon = DaemonService(config)
    assert daemon.should_process_session("test:0") is False