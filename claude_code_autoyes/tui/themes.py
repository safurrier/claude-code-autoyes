"""Theme system for the modular TUI."""

from dataclasses import dataclass, field


@dataclass
class Theme:
    """Theme configuration with semantic color names and CSS variables."""

    # Core semantic colors
    primary: str = "#fe8c69"  # Orange accent (galaxy theme inspired)
    secondary: str | None = None
    accent: str = "#fea64b"  # Orange accent
    background: str = "#121212"  # Dark background
    surface: str = "#1e1e1e"  # Slightly lighter surface
    panel: str = "#2a2a2a"  # Panel background
    foreground: str = "#ffffff"  # Text color

    # Status colors
    success: str = "#4ade80"
    warning: str = "#fbbf24"
    error: str = "#f87171"

    # Theme metadata
    name: str = "default"
    dark: bool = True

    # Additional CSS variables
    variables: dict[str, str] = field(default_factory=dict)

    @classmethod
    def get_default(cls) -> "Theme":
        """Get the default Bagels-inspired theme."""
        return cls(
            name="bagels_default",
            primary="#fe8c69",
            accent="#fea64b",
            background="#121212",
            surface="#1e1e1e",
            panel="#2a2a2a",
            foreground="#ffffff",
            success="#4ade80",
            warning="#fbbf24",
            error="#f87171",
            variables={
                "accent-lighten-1": "#feb676",
                "accent-darken-1": "#fd8020",
                "surface-lighten-1": "#2a2a2a",
                "surface-darken-1": "#161616",
                "panel-lighten-1": "#363636",
                "panel-darken-1": "#1e1e1e",
            },
        )

    def to_css_variables(self) -> dict[str, str]:
        """Convert theme to CSS variable dictionary."""
        css_vars = {
            "primary": self.primary,
            "accent": self.accent,
            "background": self.background,
            "surface": self.surface,
            "panel": self.panel,
            "foreground": self.foreground,
            "success": self.success,
            "warning": self.warning,
            "error": self.error,
        }

        # Add optional colors if defined
        if self.secondary:
            css_vars["secondary"] = self.secondary

        # Add custom variables
        css_vars.update(self.variables)

        return css_vars
