"""Button controls component for bulk operations."""

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button

from ...core.config import ConfigManager
from ...core.daemon import DaemonManager


class ButtonControls(Container):
    """Button controls component following original TUI pattern."""

    DEFAULT_CSS = """
    ButtonControls {
        layout: horizontal;
        height: auto;
        padding: 1;
        align: center middle;
        background: $surface;
        border: solid $panel;
        margin-bottom: 1;
    }

    /* Container focus support - Bagels pattern */
    ButtonControls:focus {
        border: round $accent;
    }

    ButtonControls:focus-within {
        border: round $accent;
    }

    ButtonControls > Button {
        margin: 0 1;
        width: 1fr;
        height: 3;
        border: solid $panel;
        background: $panel;
        color: $foreground;
        text-style: bold;
        text-align: center;
    }

    ButtonControls > Button:hover {
        background: $panel-lighten-1;
        color: $foreground;
        border: solid $accent;
        text-style: bold;
    }

    /* Improved focus styling - Bagels pattern */
    ButtonControls > Button:focus {
        text-style: bold reverse;
        background: $accent 10%;
        border: solid $accent;
        color: $foreground;
    }

    ButtonControls > Button.-success {
        background: $success;
        color: $background;
        border: solid $success;
    }

    ButtonControls > Button.-success:hover {
        background: $success;
        color: $background;
        border: solid $accent;
        text-style: bold;
    }

    ButtonControls > Button.-success:focus {
        text-style: bold reverse;
        background: $success 20%;
        border: solid $success;
        color: $foreground;
    }

    ButtonControls > Button.-error {
        background: $error;
        color: $background;
        border: solid $error;
    }

    ButtonControls > Button.-error:hover {
        background: $error;
        color: $background;
        border: solid $accent;
        text-style: bold;
    }

    ButtonControls > Button.-error:focus {
        text-style: bold reverse;
        background: $error 20%;
        border: solid $error;
        color: $foreground;
    }

    ButtonControls > Button.-primary {
        background: $primary;
        color: $background;
        border: solid $primary;
    }

    ButtonControls > Button.-primary:hover {
        background: $primary;
        color: $background;
        border: solid $accent;
        text-style: bold;
    }

    ButtonControls > Button.-primary:focus {
        text-style: bold reverse;
        background: $primary 20%;
        border: solid $primary;
        color: $foreground;
    }
    """

    def __init__(
        self,
        config: ConfigManager | None = None,
        daemon: DaemonManager | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            *args, **kwargs, id="button-controls", classes="button-container"
        )
        self.config = config or ConfigManager()
        self.daemon = daemon or DaemonManager()

    def compose(self) -> ComposeResult:
        """Compose the button controls."""
        yield Button("Enable All", id="enable-all", variant="success")
        yield Button("Disable All", id="disable-all", variant="error")
        yield Button("Refresh", id="refresh", variant="primary")
        yield Button("Quit", id="quit")


class ButtonPressed:
    """Message for when a button is pressed."""

    def __init__(self, button_id: str) -> None:
        self.button_id = button_id
