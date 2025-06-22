"""Instance table component for displaying Claude instances."""

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import DataTable

from ...core.config import ConfigManager
from ...core.detector import ClaudeDetector
from ...core.models import ClaudeInstance


class InstanceTable(Container):
    """Table component for displaying Claude instances with full functionality."""

    DEFAULT_CSS = """
    InstanceTable {
        height: auto;
        min-height: 10;
        border: solid $panel;
        background: $surface;
        margin-bottom: 1;
    }

    /* Container focus support - Bagels pattern */
    InstanceTable:focus {
        border: round $accent;
    }

    InstanceTable:focus-within {
        border: round $accent;
    }

    InstanceTable > DataTable {
        background: $surface;
    }

    InstanceTable > DataTable > .datatable--header {
        background: $panel;
        color: $foreground;
        text-style: bold;
        border-bottom: solid $accent;
    }

    InstanceTable > DataTable > .datatable--cursor {
        background: $accent;
        color: $background;
        text-style: bold;
        border: thick $foreground;
    }

    InstanceTable > DataTable > .datatable--hover {
        background: $panel;
    }

    .status-on {
        color: $success;
        text-style: bold;
    }

    .status-off {
        color: $error;
        text-style: bold;
    }

    .session-name {
        color: $accent;
        text-style: bold;
    }

    .pane-info {
        color: $panel-lighten-1;
    }

    .index-number {
        color: $accent;
        text-style: bold;
    }

    .prompt-time {
        color: $accent;
        text-style: italic;
    }
    """

    def __init__(
        self,
        detector: ClaudeDetector | None = None,
        config: ConfigManager | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            *args, **kwargs, id="instance-table-container", classes="module-container"
        )
        self.detector = detector or ClaudeDetector()
        self.config = config or ConfigManager()
        self._instances: list[ClaudeInstance] = []

    def compose(self) -> ComposeResult:
        """Compose the instance table."""
        self.table: DataTable[str] = DataTable(
            id="instances-table",
            zebra_stripes=True,
            cursor_type="row",
            show_cursor=True,
        )
        self.table.add_columns("#", "Session", "Pane", "Status", "Last Prompt")
        yield self.table

    def on_mount(self) -> None:
        """Initialize the table when mounted."""
        self.table.can_focus = True
        self.rebuild()

    def rebuild(self) -> None:
        """Rebuild table data with current instances and config."""
        self._instances = self.detector.find_claude_instances()

        # Update each instance with enabled status from config
        for instance in self._instances:
            pane_id = f"{instance.session}:{instance.pane}"
            instance.enabled = self.config.is_enabled(pane_id)

        self.update_table()

    def update_table(self) -> None:
        """Update the DataTable with current instances."""
        self.table.clear()

        for i, instance in enumerate(self._instances):
            # Style the status with clean indicators
            if instance.enabled:
                status = "✓ ENABLED"
                status_class = "status-on"
            else:
                status = "✗ DISABLED"
                status_class = "status-off"

            last_prompt = instance.last_prompt or "Never"

            # Add row with index and styled content
            index_display = str(i + 1) if i < 9 else "-"
            self.table.add_row(
                f"[class=index-number]{index_display}[/]",
                f"[class=session-name]{instance.session}[/]",
                f"[class=pane-info]{instance.pane}[/]",
                f"[class={status_class}]{status}[/]",
                f"[class=prompt-time]{last_prompt}[/]",
                key=str(i),
            )

    def get_selected_instance(self) -> ClaudeInstance | None:
        """Get currently selected instance."""
        if self.table.cursor_row < len(self._instances):
            return self._instances[self.table.cursor_row]
        return None

    def get_instance_by_index(self, index: int) -> ClaudeInstance | None:
        """Get instance by index."""
        if 0 <= index < len(self._instances):
            return self._instances[index]
        return None

    def toggle_selected(self) -> str | None:
        """Toggle the currently selected instance."""
        if self.table.cursor_coordinate is not None:
            row, _ = self.table.cursor_coordinate
            if 0 <= row < len(self._instances):
                instance = self._instances[row]
                pane_id = f"{instance.session}:{instance.pane}"
                self.config.toggle_session(pane_id)
                self.rebuild()
                return pane_id
        return None

    def toggle_by_index(self, index: int) -> str | None:
        """Toggle instance by index (for number key shortcuts)."""
        if 0 <= index < len(self._instances):
            instance = self._instances[index]
            pane_id = f"{instance.session}:{instance.pane}"
            self.config.toggle_session(pane_id)
            self.rebuild()
            return pane_id
        return None

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection (Enter key) to toggle instance."""
        if event.row_key is not None:
            instance_index = int(str(event.row_key.value))
            if 0 <= instance_index < len(self._instances):
                instance = self._instances[instance_index]
                pane_id = f"{instance.session}:{instance.pane}"
                self.config.toggle_session(pane_id)
                self.rebuild()
                self.post_message(InstanceToggled(pane_id))


class InstanceToggled(Message):
    """Message for when an instance is toggled."""

    def __init__(self, pane_id: str) -> None:
        super().__init__()
        self.pane_id = pane_id
