"""Status bar component for displaying daemon and system status."""

from typing import Any

from textual.widgets import Static

from ...core.daemon import DaemonManager


class StatusBar(Static):
    """Status bar component following original TUI pattern."""

    DEFAULT_CSS = """
    StatusBar {
        height: 2;
        background: $panel;
        color: $foreground;
        padding: 0 2;
        text-style: bold;
        border: solid $accent;
        margin-bottom: 1;
    }

    /* Container focus support - Bagels pattern */
    StatusBar:focus {
        border: round $accent;
    }

    StatusBar:focus-within {
        border: round $accent;
    }

    .daemon-running {
        color: $success;
        text-style: bold;
    }

    .daemon-stopped {
        color: $error;
        text-style: bold;
    }
    """

    def __init__(
        self, daemon: DaemonManager | None = None, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(
            "✗ Daemon: Not running",
            *args,
            **kwargs,
            id="status-bar",
            classes="module-container",
        )
        self.daemon = daemon or DaemonManager()

    def on_mount(self) -> None:
        """Initialize status when mounted."""
        self.rebuild()

    def rebuild(self) -> None:
        """Update status information - following original TUI pattern."""
        status_text = self.daemon.get_status()
        self.update(status_text)

    def update_daemon_status(self) -> None:
        """Update daemon status (alias for rebuild for consistency)."""
        self.rebuild()
