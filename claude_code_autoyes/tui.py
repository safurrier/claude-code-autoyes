"""Textual TUI application for claude-code-autoyes."""

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.events import Key
from textual.widgets import Button, DataTable, Header, Static

from .core import ClaudeDetector, ConfigManager, DaemonManager
from .core.models import ClaudeInstance


class ClaudeAutoYesApp(App[None]):
    """Main Textual TUI application."""

    TITLE = "Claude Auto YES"

    BINDINGS = [
        ("up,down", "navigate", "Navigate"),
        ("enter", "select", "Toggle"),
        ("space", "toggle", "Toggle"),
        ("1,2,3,4,5,6,7,8,9", "quick_toggle", "Quick Toggle"),
        ("d", "toggle_daemon", "Toggle Daemon"),
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    CSS = """
    /* Galaxy-inspired theme with proper Textual layout structure */
    Screen {
        background: #0f0f1f;
        color: #e6e6e6;
    }

    /* Header - Docked at top (fixed position) */
    Header {
        dock: top;
        height: 3;
        background: #44386b;
        color: #ffffff;
        content-align: center middle;
        text-style: bold;
        border-bottom: solid #ec7d10;
    }

    /* Main scrollable content area - takes remaining space */
    #main-content {
        height: 1fr;
        padding: 1 2;
        overflow-y: auto;
    }

    /* Status bar - auto height within scroll container */
    #status-bar {
        height: 2;
        background: #662d90;
        color: #ffffff;
        padding: 0 2;
        text-style: bold;
        border: solid #ec7d10;
        margin-bottom: 1;
    }

    /* Data table - auto height within scroll container */
    #instances-table {
        height: auto;
        min-height: 10;
        border: solid #6e8898;
        background: #1e1e3f;
        margin-bottom: 1;
    }

    DataTable > .datatable--header {
        background: #44386b;
        color: #ffffff;
        text-style: bold;
        border-bottom: solid #ec7d10;
    }

    DataTable > .datatable--cursor {
        background: #ec7d10;
        color: #000000;
        text-style: bold;
        border: thick #ffffff;
    }

    DataTable > .datatable--hover {
        background: #2d2b55;
    }

    /* Button container - auto height within scroll container */
    .button-container {
        layout: horizontal;
        height: auto;
        padding: 1;
        align: center middle;
        background: #1e1e3f;
        border: solid #6e8898;
        margin-bottom: 1;
    }

    Button {
        margin: 0 1;
        width: 1fr;
        height: 3;
        border: solid #6e8898;
        background: #44386b;
        color: #ffffff;
        text-style: bold;
        text-align: center;
    }

    Button:hover {
        background: #662d90;
        color: #ffffff;
        border: solid #ec7d10;
        text-style: bold;
    }

    Button:focus {
        background: #ec7d10;
        border: thick #ffffff;
        color: #000000;
        text-style: bold;
    }

    Button.-success {
        background: #004f2d;
        color: #ffffff;
        border: solid #00fa9a;
    }

    Button.-success:hover {
        background: #00fa9a;
        color: #000000;
        border: solid #ec7d10;
        text-style: bold;
    }

    Button.-error {
        background: #bf1a2f;
        color: #ffffff;
        border: solid #ff4500;
    }

    Button.-error:hover {
        background: #ff4500;
        color: #000000;
        border: solid #ec7d10;
        text-style: bold;
    }

    Button.-primary {
        background: #6e8898;
        color: #ffffff;
        border: solid #a684e8;
    }

    Button.-primary:hover {
        background: #a684e8;
        color: #000000;
        border: solid #ec7d10;
        text-style: bold;
    }

    /* Footer - Automatically docked at bottom */
    Footer {
        background: #1e1e3f;
        color: #a684e8;
        border-top: solid #ec7d10;
    }

    /* Status indicators with vibrant Galaxy colors */
    .status-on {
        color: #00fa9a;
        text-style: bold;
    }

    .status-off {
        color: #ff4500;
        text-style: bold;
    }

    .session-name {
        color: #a684e8;
        text-style: bold;
    }

    .pane-info {
        color: #6e8898;
    }

    .index-number {
        color: #ec7d10;
        text-style: bold;
    }

    .prompt-time {
        color: #ec7d10;
        text-style: italic;
    }

    /* Daemon status colors */
    .daemon-running {
        color: #00fa9a;
        text-style: bold;
    }

    .daemon-stopped {
        color: #ff4500;
        text-style: bold;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.detector = ClaudeDetector()
        self.config = ConfigManager()
        self.daemon = DaemonManager()
        self.instances: list[ClaudeInstance] = []

    def compose(self) -> ComposeResult:
        # Header
        yield Header()

        # Status bar
        yield Static("✗ Daemon: Not running", id="status-bar")

        # Data table with limited height to leave space for buttons
        yield DataTable(id="instances-table")

        # Button container
        yield Container(
            Button("Enable All", id="enable-all", variant="success"),
            Button("Disable All", id="disable-all", variant="error"),
            Button("Start Daemon", id="start-daemon", variant="primary"),
            Button("Stop Daemon", id="stop-daemon", variant="primary"),
            Button("Refresh", id="refresh", variant="primary"),
            Button("Quit", id="quit"),
            classes="button-container",
        )

        # Simple shortcuts at bottom
        yield Static(
            "↑↓: Navigate | Enter: Toggle | Space: Toggle | 1-9: Quick Toggle | d: Toggle Daemon | r: Refresh | q: Quit",
            id="shortcuts",
        )

    def on_mount(self) -> None:
        """Initialize the table and load data."""
        table = self.query_one(DataTable)
        table.add_columns("#", "Session", "Pane", "Status", "Last Prompt")
        table.cursor_type = "row"
        table.zebra_stripes = True  # Alternating row colors
        table.show_cursor = True  # Show cursor for navigation
        table.can_focus = True  # Allow keyboard focus

        self.refresh_instances()
        self.update_daemon_status()

        # Set focus to table for arrow key navigation
        self.set_focus(table)

        # Set up auto-refresh
        self.set_interval(self.config.refresh_interval, self.refresh_instances)
        self.set_interval(
            5, self.update_daemon_status
        )  # Update daemon status every 5 seconds

    def refresh_instances(self) -> None:
        """Refresh the list of Claude instances."""
        self.instances = self.detector.find_claude_instances()

        # Update each instance with enabled status from config
        for instance in self.instances:
            pane_id = f"{instance.session}:{instance.pane}"
            instance.enabled = self.config.is_enabled(pane_id)

        self.update_table()

        # Ensure table keeps focus after refresh
        table = self.query_one(DataTable)
        if not table.has_focus:
            self.set_focus(table)

    def update_daemon_status(self) -> None:
        """Update the daemon status display."""
        status_bar = self.query_one("#status-bar", Static)
        status_bar.update(self.daemon.get_status())

    def update_table(self) -> None:
        """Update the DataTable with current instances."""
        table = self.query_one(DataTable)
        table.clear()

        for i, instance in enumerate(self.instances):
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
            table.add_row(
                f"[class=index-number]{index_display}[/]",
                f"[class=session-name]{instance.session}[/]",
                f"[class=pane-info]{instance.pane}[/]",
                f"[class={status_class}]{status}[/]",
                f"[class=prompt-time]{last_prompt}[/]",
                key=str(i),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        button_id = event.button.id

        if button_id == "enable-all":
            session_panes = [f"{inst.session}:{inst.pane}" for inst in self.instances]
            self.config.enable_all(session_panes)
            self.refresh_instances()

        elif button_id == "disable-all":
            self.config.disable_all()
            self.refresh_instances()

        elif button_id == "refresh":
            self.refresh_instances()

        elif button_id == "start-daemon":
            if self.daemon.start(self.config):
                self.update_daemon_status()
            else:
                self.notify("Failed to start daemon", severity="error")

        elif button_id == "stop-daemon":
            if self.daemon.stop():
                self.update_daemon_status()
            else:
                self.notify("Failed to stop daemon", severity="error")

        elif button_id == "quit":
            # Stop daemon before quitting
            if self.daemon.is_running():
                self.daemon.stop()
            self.exit()

    def key_1(self) -> None:
        """Toggle first Claude instance."""
        self._toggle_instance_by_index(0)

    def key_2(self) -> None:
        """Toggle second Claude instance."""
        self._toggle_instance_by_index(1)

    def key_3(self) -> None:
        """Toggle third Claude instance."""
        self._toggle_instance_by_index(2)

    def key_4(self) -> None:
        """Toggle fourth Claude instance."""
        self._toggle_instance_by_index(3)

    def key_5(self) -> None:
        """Toggle fifth Claude instance."""
        self._toggle_instance_by_index(4)

    def key_6(self) -> None:
        """Toggle sixth Claude instance."""
        self._toggle_instance_by_index(5)

    def key_7(self) -> None:
        """Toggle seventh Claude instance."""
        self._toggle_instance_by_index(6)

    def key_8(self) -> None:
        """Toggle eighth Claude instance."""
        self._toggle_instance_by_index(7)

    def key_9(self) -> None:
        """Toggle ninth Claude instance."""
        self._toggle_instance_by_index(8)

    def key_q(self) -> None:
        """Quit the application."""
        # Stop daemon before quitting
        if self.daemon.is_running():
            self.daemon.stop()
        self.exit()

    def key_r(self) -> None:
        """Refresh instances."""
        self.refresh_instances()

    def key_d(self) -> None:
        """Toggle daemon start/stop."""
        if self.daemon.is_running():
            if self.daemon.stop():
                self.update_daemon_status()
                self.notify("Daemon stopped", severity="warning")
            else:
                self.notify("Failed to stop daemon", severity="error")
        else:
            if self.daemon.start(self.config):
                self.update_daemon_status()
                self.notify("Daemon started")
            else:
                self.notify("Failed to start daemon", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection (Enter key) to toggle instance."""
        if event.row_key is not None:
            instance_index = int(str(event.row_key.value))
            if 0 <= instance_index < len(self.instances):
                instance = self.instances[instance_index]
                pane_id = f"{instance.session}:{instance.pane}"
                self.config.toggle_session(pane_id)
                self.refresh_instances()
                self.notify(f"Toggled {pane_id}")

    def key_space(self) -> None:
        """Toggle currently highlighted instance with space bar."""
        table = self.query_one(DataTable)
        if table.cursor_coordinate is not None:
            row, _ = table.cursor_coordinate
            if 0 <= row < len(self.instances):
                instance = self.instances[row]
                pane_id = f"{instance.session}:{instance.pane}"
                self.config.toggle_session(pane_id)
                self.refresh_instances()
                self.notify(f"Toggled {pane_id}")

    def _toggle_instance_by_index(self, index: int) -> None:
        """Helper method to toggle instance by index."""
        if 0 <= index < len(self.instances):
            instance = self.instances[index]
            pane_id = f"{instance.session}:{instance.pane}"
            self.config.toggle_session(pane_id)
            self.refresh_instances()
            self.notify(f"Toggled {pane_id}")

    def on_key(self, event: Key) -> None:
        """Handle other keyboard shortcuts."""
        # Fallback for any other keys
        pass
