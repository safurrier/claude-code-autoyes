"""Simple Python daemon service - direct translation of bash logic."""

import re
import subprocess
import time
import logging
from typing import Optional


class PromptDetector:
    """Detects Claude prompts in tmux pane content using regex patterns."""

    def __init__(self):
        self.patterns = [
            r"Do you want to",
            r"Would you like to",
            r"Proceed\?",
            r"❯ 1\. Yes",
        ]

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

    def __init__(self, config_manager, sleep_interval: float = 3.0):
        self.config = config_manager
        self.running = False
        self.prompt_detector = PromptDetector()
        self.sleep_interval = sleep_interval  # Dependency injection for testability

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

                time.sleep(self.sleep_interval)  # Use injected interval
            except Exception as e:
                self._log_error(f"Monitor error: {e}")

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
                        self._log_info(f"Sent Enter to {session_pane}")
                        time.sleep(2)  # Same pause as bash version

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
                ["tmux", "capture-pane", "-p", "-t", session_pane, "-S", "-10"],
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

    def _log_info(self, message: str):
        """Log info message - equivalent to bash log_msg function."""
        logging.info(f"[DaemonService] {message}")

    def _log_error(self, message: str):
        """Log error message - equivalent to bash log_msg function."""
        logging.error(f"[DaemonService] {message}")
