"""Simple Python daemon service - direct translation of bash logic."""

import re
import subprocess
import time
from typing import Optional
from .logging_config import get_daemon_logger
from .constants import (
    DEFAULT_SLEEP_INTERVAL,
    PROMPT_RESPONSE_PAUSE,
    CLAUDE_PROMPT_PATTERNS,
    TMUX_CAPTURE_LINES,
)


class PromptDetector:
    """Detects Claude prompts in tmux pane content using regex patterns."""

    def __init__(self):
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

    def __init__(self, config_manager, sleep_interval: float = DEFAULT_SLEEP_INTERVAL):
        self.config = config_manager
        self.running = False
        self.prompt_detector = PromptDetector()
        self.sleep_interval = sleep_interval
        self.logger = get_daemon_logger()

    def start_monitoring_loop(self, max_iterations: Optional[int] = None):
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
            except Exception as e:
                self.logger.error(f"Monitor error: {e}")

    def stop(self):
        """Stop the monitoring loop."""
        self.running = False

    def _check_enabled_sessions(self):
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
