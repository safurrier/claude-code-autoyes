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
        from typing import Any

        # Build kwargs for ColorSystem with proper types
        kwargs: dict[str, Any] = {}

        # Add string fields if not None
        if self.primary is not None:
            kwargs["primary"] = self.primary
        if self.secondary is not None:
            kwargs["secondary"] = self.secondary
        if self.warning is not None:
            kwargs["warning"] = self.warning
        if self.error is not None:
            kwargs["error"] = self.error
        if self.success is not None:
            kwargs["success"] = self.success
        if self.accent is not None:
            kwargs["accent"] = self.accent
        if self.foreground is not None:
            kwargs["foreground"] = self.foreground
        if self.background is not None:
            kwargs["background"] = self.background
        if self.surface is not None:
            kwargs["surface"] = self.surface
        if self.panel is not None:
            kwargs["panel"] = self.panel
        if self.boost is not None:
            kwargs["boost"] = self.boost

        # Add other typed fields
        kwargs["dark"] = self.dark
        kwargs["luminosity_spread"] = self.luminosity_spread
        kwargs["text_alpha"] = self.text_alpha

        # Add variables if present
        if self.variables:
            kwargs["variables"] = self.variables

        return ColorSystem(**kwargs)


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
