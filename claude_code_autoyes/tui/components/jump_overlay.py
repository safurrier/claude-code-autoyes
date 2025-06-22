"""Jump navigation overlay modal."""

from textual import events
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Label, Static

from .jumper import Jumper


class JumpOverlay(ModalScreen[str | Widget | None]):
    """Modal overlay for jump navigation."""

    DEFAULT_CSS = """
    JumpOverlay {
        background: $background 50%;
    }

    .textual-jump-label {
        layer: textual-jump;
        text-style: bold;
        color: $foreground;
        background: $accent;
        border: round $accent;
        padding: 0 1;
        width: auto;
        height: auto;
    }

    #textual-jump-info {
        dock: bottom;
        height: 1;
        width: 1fr;
        background: $accent;
        color: $background;
        text-align: center;
        text-style: bold;
    }

    #textual-jump-message {
        dock: top;
        height: 1;
        width: 1fr;
        background: $panel;
        color: $foreground;
        text-align: center;
        text-style: bold;
    }
    """

    def __init__(self, jumper: Jumper) -> None:
        """Initialize jump overlay with jumper instance.

        Args:
            jumper: The jumper instance to use for navigation
        """
        super().__init__()
        self.jumper = jumper

    def compose(self) -> ComposeResult:
        """Compose the jump overlay interface."""
        # Get current jump targets
        overlays = self.jumper.get_overlays()

        # Create instruction messages
        yield Static("Press a key to jump to target", id="textual-jump-message")
        yield Static("ESC to dismiss", id="textual-jump-info")

        # Create jump labels at widget positions
        for offset, jump_info in overlays.items():
            key, _widget = jump_info
            label = Label(key, classes="textual-jump-label")
            label.styles.offset = offset
            yield label

    def on_key(self, event: events.Key) -> None:
        """Handle key press for jump navigation.

        Args:
            event: The key event
        """
        # Prevent event propagation to avoid focus conflicts
        event.prevent_default()
        event.stop()

        if event.key == "escape":
            # Dismiss overlay without selection
            self.dismiss(None)
        else:
            # Check if key corresponds to a jump target
            target = self.jumper.get_target_by_key(event.key)
            if target:
                # Dismiss with selected target
                self.dismiss(target)
            # Note: Invalid keys are ignored, overlay stays open
