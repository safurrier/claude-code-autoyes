"""Main page component following Bagels architecture patterns."""

from typing import Any

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Footer, Header

from ...core.config import ConfigManager
from ...core.daemon import DaemonManager
from ...core.detector import ClaudeDetector
from ..components import ButtonControls, InstanceTable, StatusBar


class MainPage(Container):
    """Main page that combines all components with full TUI functionality."""

    DEFAULT_CSS = """
    MainPage {
        background: $background;
    }

    #main-content {
        height: 1fr;
        padding: 1 2;
        overflow-y: auto;
    }
    """

    def __init__(
        self,
        detector: ClaudeDetector | None = None,
        config: ConfigManager | None = None,
        daemon: DaemonManager | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.detector = detector or ClaudeDetector()
        self.config = config or ConfigManager()
        self.daemon = daemon or DaemonManager()

    def compose(self) -> ComposeResult:
        """Compose the main page layout with full functionality."""
        # Header
        yield Header()

        # Main content container (scrollable)
        with Container(id="main-content"):
            # Status bar
            yield StatusBar(daemon=self.daemon)

            # Data table
            yield InstanceTable(detector=self.detector, config=self.config)

            # Button controls
            yield ButtonControls(config=self.config, daemon=self.daemon)

        # Standard Footer widget for shortcuts
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the page when mounted."""
        # Set focus to the table for keyboard navigation
        instance_table = self.query_one(InstanceTable)
        instance_table.table.focus()

    def rebuild(self) -> None:
        """Rebuild all child components."""
        # Rebuild status bar
        status_bar = self.query_one(StatusBar)
        status_bar.rebuild()

        # Rebuild instance table
        instance_table = self.query_one(InstanceTable)
        instance_table.rebuild()

        # Ensure table keeps focus after refresh
        if not instance_table.table.has_focus:
            instance_table.table.focus()
