"""Jump navigation system for rapid UI navigation."""

from typing import Any, NamedTuple, Protocol, runtime_checkable

from textual.geometry import Offset
from textual.screen import Screen
from textual.widget import Widget


@runtime_checkable
class Jumpable(Protocol):
    """Protocol for widgets that can be jumped to."""

    jump_key: str


class JumpInfo(NamedTuple):
    """Information about a jump target."""

    key: str
    widget: Widget


class Jumper:
    """Manages jump navigation targets and key mappings."""

    def __init__(self, ids_to_keys: dict[str, str], screen: Screen[Any]) -> None:
        """Initialize jumper with ID to key mappings.

        Args:
            ids_to_keys: Mapping of widget IDs to jump keys
            screen: The screen to scan for jump targets
        """
        self.ids_to_keys = ids_to_keys
        self.keys_to_ids = {v: k for k, v in ids_to_keys.items()}
        self.screen = screen
        self.overlays: dict[Offset, JumpInfo] = {}

    def get_overlays(self) -> dict[Offset, JumpInfo]:
        """Get jump overlays for current screen state.

        Returns:
            Dictionary mapping screen offsets to jump info
        """
        overlays: dict[Offset, JumpInfo] = {}

        # Walk all widgets on the screen
        for node in self.screen.walk_children():
            # Only process actual widgets
            if not isinstance(node, Widget):
                continue

            widget = node
            jump_key = None

            # Check if widget has an ID in our mapping
            if widget.id in self.ids_to_keys:
                jump_key = self.ids_to_keys[widget.id]
            # Check if widget implements Jumpable protocol
            elif isinstance(widget, Jumpable):
                jump_key = widget.jump_key

            if jump_key and hasattr(widget, "region") and widget.region:
                # Get widget's screen position
                offset = widget.region.offset
                overlays[offset] = JumpInfo(jump_key, widget)

        self.overlays = overlays
        return overlays

    def get_target_by_key(self, key: str) -> Widget | None:
        """Get jump target widget by key.

        Args:
            key: The jump key pressed

        Returns:
            Target widget or None if not found
        """
        for jump_info in self.overlays.values():
            if jump_info.key == key:
                return jump_info.widget
        return None
