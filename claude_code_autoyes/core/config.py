"""Configuration management for claude-autoyes."""

import json
import os
from typing import Any, cast

from .constants import CONFIG_FILE_NAME, DEFAULT_REFRESH_INTERVAL


class ConfigManager:
    """Manages configuration for claude-autoyes.

    Handles loading, saving, and managing configuration settings including
    enabled sessions, daemon state, and refresh intervals.

    Args:
        config_file: Optional path to config file. Defaults to ~/.claude-autoyes.json

    Attributes:
        enabled_sessions: Set of enabled tmux session:pane identifiers
        daemon_enabled: Whether the daemon is enabled
        refresh_interval: How often to check for prompts (seconds)
        auto_yes_enabled: Global toggle for auto-yes functionality
    """

    def __init__(self, config_file: str | None = None):
        self.config_file = config_file or os.path.expanduser(CONFIG_FILE_NAME)
        self.enabled_sessions: set[str] = set()
        self.daemon_enabled = False
        self.refresh_interval = DEFAULT_REFRESH_INTERVAL
        self.auto_yes_enabled = True  # Default enabled
        self.load()

    def load(self) -> dict[str, Any]:
        """Load configuration from file.

        Reads configuration from the config file and updates instance attributes.
        Creates default configuration if file doesn't exist.

        Returns:
            Dictionary containing the loaded configuration data.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file) as f:
                    data = cast(dict[str, Any], json.load(f))
                    self.enabled_sessions = set(data.get("enabled_sessions", []))
                    self.daemon_enabled = data.get("daemon_enabled", False)
                    self.refresh_interval = data.get(
                        "refresh_interval", DEFAULT_REFRESH_INTERVAL
                    )
                    self.auto_yes_enabled = data.get("auto_yes_enabled", True)
                    return data
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return {}

    def save(self, config: dict[str, Any] | None = None) -> None:
        """Save configuration to file.

        Args:
            config: Optional configuration dict. If None, uses current instance state.
        """
        if config is None:
            config = {
                "enabled_sessions": list(self.enabled_sessions),
                "daemon_enabled": self.daemon_enabled,
                "refresh_interval": self.refresh_interval,
                "auto_yes_enabled": self.auto_yes_enabled,
            }

        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except OSError:
            pass

    def toggle_session(self, session_pane: str) -> bool:
        """Toggle a session on/off.

        Args:
            session_pane: Session:pane identifier (e.g., "dev:0.1")

        Returns:
            True if session is now enabled, False if disabled.
        """
        if session_pane in self.enabled_sessions:
            self.enabled_sessions.remove(session_pane)
            enabled = False
        else:
            self.enabled_sessions.add(session_pane)
            enabled = True

        self.save()
        return enabled

    def enable_all(self, sessions: list[str]) -> None:
        """Enable all provided sessions.

        Args:
            sessions: List of session:pane identifiers to enable.
        """
        self.enabled_sessions.update(sessions)
        self.save()

    def disable_all(self) -> None:
        """Disable all sessions."""
        self.enabled_sessions.clear()
        self.save()

    def is_enabled(self, session_pane: str) -> bool:
        """Check if a session is enabled.

        Args:
            session_pane: Session:pane identifier to check.

        Returns:
            True if the session is enabled for auto-yes.
        """
        return session_pane in self.enabled_sessions
