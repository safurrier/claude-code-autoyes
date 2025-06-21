"""Theme system for claude-code-autoyes TUI."""

from dataclasses import dataclass, field

from textual.design import ColorSystem


@dataclass
class Theme:
    """Theme configuration for the TUI."""

    primary: str
    secondary: str | None = None
    warning: str | None = None
    error: str | None = None
    success: str | None = None
    accent: str | None = None
    foreground: str | None = None
    background: str | None = None
    surface: str | None = None
    panel: str | None = None
    boost: str | None = None
    dark: bool = True
    luminosity_spread: float = 0.15
    text_alpha: float = 0.95
    variables: dict[str, str] = field(default_factory=dict)

    def to_color_system(self) -> ColorSystem:
        """Convert this theme to a ColorSystem."""
        theme_dict = {
            "primary": self.primary,
            "secondary": self.secondary,
            "warning": self.warning,
            "error": self.error,
            "success": self.success,
            "accent": self.accent,
            "foreground": self.foreground,
            "background": self.background,
            "surface": self.surface,
            "panel": self.panel,
            "boost": self.boost,
            "dark": self.dark,
            "luminosity_spread": self.luminosity_spread,
            "text_alpha": self.text_alpha,
            "variables": self.variables,
        }
        # Remove None values
        theme_dict = {k: v for k, v in theme_dict.items() if v is not None}
        return ColorSystem(**theme_dict)


# Available themes
THEMES: dict[str, Theme] = {
    "default": Theme(
        primary="#fe8c69",
        secondary="#fea64b",
        accent="#ffa62b",
        warning="#ffa500",
        error="#ff4500",
        success="#00fa9a",
        foreground="#ffffff",
        background="#121212",
        surface="#1e1e1e",
        panel="#2a2a2a",
        variables={
            "button-color-foreground": "#121212",
        },
    ),
    "dark": Theme(
        primary="#0178d4",
        secondary="#004578",
        accent="#ffa62b",
        warning="#ffa62b",
        error="#ba3c5b",
        success="#4ebf71",
        foreground="#e0e0e0",
        background="#0f0f0f",
        surface="#1a1a1a",
        panel="#262626",
        variables={
            "button-color-foreground": "#0f0f0f",
        },
    ),
    "galaxy": Theme(
        primary="#8A2BE2",
        secondary="#a684e8",
        warning="#FFD700",
        error="#FF4500",
        success="#00FA9A",
        accent="#FF69B4",
        dark=True,
        background="#0F0F1F",
        surface="#1E1E3F",
        panel="#2D2B55",
        foreground="#e0e0e0",
        variables={
            "button-color-foreground": "#0F0F1F",
        },
    ),
}
