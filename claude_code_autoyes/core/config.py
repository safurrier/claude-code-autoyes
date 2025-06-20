"""Configuration management for claude-autoyes."""

import json
import os
from typing import Dict, List, Optional, Set


class ConfigManager:
    """Manages configuration for claude-autoyes."""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.path.expanduser("~/.claude-autoyes-config")
        self.enabled_sessions: Set[str] = set()
        self.daemon_enabled = False
        self.refresh_interval = 30
        self.load()

    def load(self) -> Dict:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.enabled_sessions = set(data.get("enabled_sessions", []))
                    self.daemon_enabled = data.get("daemon_enabled", False)
                    self.refresh_interval = data.get("refresh_interval", 30)
                    return data
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return {}

    def save(self, config: Optional[Dict] = None) -> None:
        """Save configuration to file."""
        if config is None:
            config = {
                "enabled_sessions": list(self.enabled_sessions),
                "daemon_enabled": self.daemon_enabled,
                "refresh_interval": self.refresh_interval,
            }

        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except OSError:
            pass

    def toggle_session(self, session_pane: str) -> bool:
        """Toggle a session on/off. Returns new state (True=enabled)."""
        if session_pane in self.enabled_sessions:
            self.enabled_sessions.remove(session_pane)
            enabled = False
        else:
            self.enabled_sessions.add(session_pane)
            enabled = True

        self.save()
        return enabled

    def enable_all(self, sessions: List[str]) -> None:
        """Enable all provided sessions."""
        self.enabled_sessions.update(sessions)
        self.save()

    def disable_all(self) -> None:
        """Disable all sessions."""
        self.enabled_sessions.clear()
        self.save()

    def is_enabled(self, session_pane: str) -> bool:
        """Check if a session is enabled."""
        return session_pane in self.enabled_sessions
