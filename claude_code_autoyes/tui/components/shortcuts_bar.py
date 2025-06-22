"""Shortcuts bar component for displaying keyboard shortcuts."""

from typing import Any

from textual.widgets import Static


class ShortcutsBar(Static):
    """Shortcuts bar component showing available keyboard shortcuts."""

    DEFAULT_CSS = """
    ShortcutsBar {
        height: 3;
        background: $surface;
        color: $foreground;
        text-align: center;
        padding: 1;
        border: solid $panel;
    }
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        shortcuts_text = (
            "↑↓: Navigate | Enter: Toggle | Space: Toggle | "
            "1-9: Quick Toggle | d: Toggle Daemon | r: Refresh | q: Quit"
        )
        super().__init__(
            shortcuts_text, *args, **kwargs, id="shortcuts", classes="shortcuts-bar"
        )
