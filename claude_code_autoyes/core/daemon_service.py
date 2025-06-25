"""Simple Python daemon service - direct translation of bash logic."""

import re
import subprocess
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import ConfigManager

from .constants import (
    CLAUDE_PROMPT_PATTERNS,
    DEFAULT_SLEEP_INTERVAL,
    PROMPT_RESPONSE_PAUSE,
    TMUX_CAPTURE_LINES,
)
from .logging_config import get_daemon_logger


class PromptDetector:
    """Detects Claude prompts in tmux pane content using regex patterns."""

    def __init__(self) -> None:
        self.patterns = CLAUDE_PROMPT_PATTERNS

    def detect_claude_prompt(self, content: str) -> bool:
        """Check if content contains Claude prompt patterns."""
        if not content:
            return False

        # Case insensitive matching
        for pattern in self.patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False


class DaemonService:
    """Simple synchronous daemon service - direct Python translation of bash logic."""

    def __init__(
        self,
        config_manager: "ConfigManager",
        sleep_interval: float = DEFAULT_SLEEP_INTERVAL,
    ) -> None:
        self.config = config_manager
        self.running = False
        self.prompt_detector = PromptDetector()
        self.sleep_interval = sleep_interval
        self.logger = get_daemon_logger()

    def start_monitoring_loop(self, max_iterations: int | None = None) -> None:
        """Simple synchronous monitoring loop - equivalent to bash while loop.

        Args:
            max_iterations: Maximum iterations before stopping (None for infinite).
                           Useful for testing.
        """
        self.running = True
        iterations = 0

        while self.running:
            try:
                self._check_enabled_sessions()

                iterations += 1
                if max_iterations and iterations >= max_iterations:
                    self.stop()
                    break

                time.sleep(self.sleep_interval)
            except (OSError, subprocess.SubprocessError, ValueError) as e:
                self.logger.error(f"Monitor error: {e}")
            except KeyboardInterrupt:
                self.logger.info("Daemon interrupted by user")
                self.stop()
                break

    def stop(self) -> None:
        """Stop the monitoring loop."""
        self.running = False

    def should_process_session(self, session_pane: str) -> bool:
        """Check if a session should be processed for auto-yes.

        Args:
            session_pane: Session:pane identifier to check

        Returns:
            True if session should be processed (both enabled and global toggle on)
        """
        # Session must be in enabled_sessions AND global toggle must be on
        session_enabled = session_pane in self.config.enabled_sessions
        global_enabled = getattr(self.config, "auto_yes_enabled", True)

        return session_enabled and global_enabled

    def _check_enabled_sessions(self) -> None:
        """Check all enabled sessions for prompts - equivalent to bash for loop."""
        for session_pane in self.config.enabled_sessions:
            if self._session_exists(session_pane):
                content = self._capture_pane_content(session_pane)
                if self.prompt_detector.detect_claude_prompt(content):
                    if self._send_enter_key(session_pane):
                        self.logger.info(f"Sent Enter to {session_pane}")
                        time.sleep(PROMPT_RESPONSE_PAUSE)

    def _session_exists(self, session_pane: str) -> bool:
        """Check if tmux session exists - equivalent to tmux has-session."""
        session_name = session_pane.split(":")[0]
        try:
            result = subprocess.run(
                ["tmux", "has-session", "-t", session_name], capture_output=True
            )
            return result.returncode == 0
        except subprocess.SubprocessError:
            return False

    def _capture_pane_content(self, session_pane: str) -> str:
        """Capture tmux pane content - equivalent to tmux capture-pane."""
        try:
            result = subprocess.run(
                [
                    "tmux",
                    "capture-pane",
                    "-p",
                    "-t",
                    session_pane,
                    "-S",
                    TMUX_CAPTURE_LINES,
                ],
                capture_output=True,
                text=True,
            )
            return result.stdout if result.returncode == 0 else ""
        except subprocess.SubprocessError:
            return ""

    def _send_enter_key(self, session_pane: str) -> bool:
        """Send Enter key to tmux pane - equivalent to tmux send-keys."""
        try:
            result = subprocess.run(
                ["tmux", "send-keys", "-t", session_pane, "Enter"], capture_output=True
            )
            return result.returncode == 0
        except subprocess.SubprocessError:
            return False
