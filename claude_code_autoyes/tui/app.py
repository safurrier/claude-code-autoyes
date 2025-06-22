"""Main TUI application for the new modular architecture."""

from typing import Any

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Button

from ..core.config import ConfigManager
from ..core.daemon import DaemonManager
from ..core.detector import ClaudeDetector
from .components import InstanceTable
from .pages import MainPage
from .themes import THEMES


class ClaudeAutoYesApp(App[None]):
    """Modular TUI application with full feature parity."""

    TITLE = "Claude Auto YES"

    BINDINGS = [
        ("up,down", "navigate", "Navigate"),
        ("enter", "select", "Toggle"),
        ("space", "toggle", "Toggle"),
        ("1,2,3,4,5,6,7,8,9", "quick_toggle", "Quick Toggle"),
        ("d", "toggle_daemon", "Toggle Daemon"),
        ("r", "refresh", "Refresh"),
        ("t", "cycle_theme", "Cycle Theme"),
        ("q", "quit", "Quit"),
    ]

    CSS = """
    App {
        background: $background;
    }
    """

    # Theme reactive - follows Bagels pattern
    app_theme: reactive[str] = reactive("dracula", init=False)

    def __init__(
        self,
        detector: ClaudeDetector | None = None,
        config: ConfigManager | None = None,
        daemon: DaemonManager | None = None,
        **kwargs: Any,
    ):
        # Set themes before super().__init__() since get_css_variables() is called during init
        self.themes = THEMES
        super().__init__(**kwargs)
        self.detector = detector or ClaudeDetector()
        self.config = config or ConfigManager()
        self.daemon = daemon or DaemonManager()

    def get_css_variables(self) -> dict[str, str]:
        """Apply theme CSS variables - Bagels pattern."""
        if self.app_theme:
            theme = self.themes.get(self.app_theme)
            if theme:
                color_system = theme.to_color_system().generate()
            else:
                color_system = {}
        else:
            color_system = {}
        return {**super().get_css_variables(), **color_system}

    def watch_app_theme(self, theme: str | None) -> None:
        """Handle theme changes - Bagels pattern."""
        self.refresh_css(animate=False)
        self.screen._update_styles()
        if theme:
            if theme in self.themes:
                self.notify(f"Theme changed to {theme}", timeout=1.5)
            else:
                self.notify(f"Theme {theme!r} not found", timeout=1.5)

    def compose(self) -> ComposeResult:
        """Compose the modular TUI interface."""
        yield MainPage(detector=self.detector, config=self.config, daemon=self.daemon)

    def on_mount(self) -> None:
        """Initialize the app and set up auto-refresh."""
        # Get the main page and initialize it
        main_page = self.query_one(MainPage)
        main_page.rebuild()

        # Set up auto-refresh intervals with performance optimization
        self.set_interval(self.config.refresh_interval, self.refresh_instances)
        self.set_interval(5, self.update_daemon_status)

        # Set initial focus to instance table for keyboard navigation
        try:
            instance_table = self.query_one(InstanceTable)
            if instance_table.table:
                self.set_focus(instance_table.table)
        except Exception:
            pass  # Table might not be mounted yet

    def refresh_instances(self) -> None:
        """Refresh the list of Claude instances."""
        main_page = self.query_one(MainPage)
        main_page.rebuild()

        # Maintain focus on table after refresh (Bagels pattern)
        try:
            instance_table = self.query_one(InstanceTable)
            if instance_table.table and not instance_table.table.has_focus:
                self.set_focus(instance_table.table)
        except Exception:
            pass

    def update_daemon_status(self) -> None:
        """Update the daemon status display."""
        main_page = self.query_one(MainPage)
        main_page.rebuild()

        # Maintain focus on table after status update
        try:
            instance_table = self.query_one(InstanceTable)
            if instance_table.table and not instance_table.table.has_focus:
                self.set_focus(instance_table.table)
        except Exception:
            pass

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        button_id = event.button.id

        if button_id == "enable-all":
            instance_table = self.query_one(InstanceTable)
            session_panes = [
                f"{inst.session}:{inst.pane}" for inst in instance_table._instances
            ]
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
            await self.action_quit()

    # Keyboard shortcuts - number keys for quick toggle
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

    async def key_q(self) -> None:
        """Quit the application."""
        await self.action_quit()

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

    def key_space(self) -> None:
        """Toggle currently highlighted instance with space bar."""
        instance_table = self.query_one(InstanceTable)
        pane_id = instance_table.toggle_selected()
        if pane_id:
            self.notify(f"Toggled {pane_id}")

    def action_cycle_theme(self) -> None:
        """Cycle through available themes."""
        theme_names = list(self.themes.keys())
        current_index = (
            theme_names.index(self.app_theme) if self.app_theme in theme_names else 0
        )
        next_index = (current_index + 1) % len(theme_names)
        self.app_theme = theme_names[next_index]

    async def action_quit(self) -> None:
        """Quit the application safely."""
        # Stop daemon before quitting
        if self.daemon.is_running():
            self.daemon.stop()
        self.exit()

    def _toggle_instance_by_index(self, index: int) -> None:
        """Helper method to toggle instance by index."""
        instance_table = self.query_one(InstanceTable)
        pane_id = instance_table.toggle_by_index(index)
        if pane_id:
            self.notify(f"Toggled {pane_id}")


def run_tui(
    detector: ClaudeDetector | None = None,
    config: ConfigManager | None = None,
    daemon: DaemonManager | None = None,
) -> None:
    """Run the modular TUI application."""
    app = ClaudeAutoYesApp(detector=detector, config=config, daemon=daemon)
    app.run()
