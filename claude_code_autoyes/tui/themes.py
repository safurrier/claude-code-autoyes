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


# Available themes - All 11 themes ported from Bagels
THEMES: dict[str, Theme] = {
    "dark": Theme(
        primary="#0178D4",
        secondary="#004578",
        accent="#ffa62b",
        warning="#ffa62b",
        error="#ba3c5b",
        success="#4EBF71",
        foreground="#e0e0e0",
        dark=True,
    ),
    "galaxy": Theme(
        primary="#8A2BE2",  # Deep Magenta (Blueviolet)
        secondary="#a684e8",
        warning="#FFD700",  # Gold
        error="#FF4500",  # OrangeRed
        success="#00FA9A",  # Medium Spring Green
        accent="#FF69B4",  # Hot Pink
        background="#0F0F1F",  # Very Dark Blue, almost black
        surface="#1E1E3F",  # Dark Blue-Purple
        panel="#2D2B55",  # Slightly Lighter Blue-Purple
        dark=True,
    ),
    "alpine": Theme(
        primary="#4A90E2",  # Clear Sky Blue
        secondary="#81A1C1",  # Misty Blue
        warning="#EBCB8B",  # Soft Sunlight
        error="#BF616A",  # Muted Red
        success="#A3BE8C",  # Alpine Meadow Green
        accent="#5E81AC",  # Mountain Lake Blue
        background="#262b35",  # Dark Slate Grey
        surface="#3B4252",  # Darker Blue-Grey
        panel="#434C5E",  # Lighter Blue-Grey
        dark=True,
    ),
    "cobalt": Theme(
        primary="#334D5C",  # Deep Cobalt Blue
        secondary="#4878A6",  # Slate Blue
        warning="#FFAA22",  # Amber
        error="#E63946",  # Red
        success="#4CAF50",  # Green
        accent="#D94E64",  # Candy Apple Red
        background="#1F262A",  # Charcoal
        surface="#27343B",  # Dark Lead
        panel="#2D3E46",  # Storm Gray
        dark=True,
    ),
    "hacker": Theme(
        primary="#00FF00",  # Bright Green (Lime)
        secondary="#32CD32",  # Lime Green
        warning="#ADFF2F",  # Green Yellow
        error="#FF4500",  # Orange Red
        success="#00FA9A",  # Medium Spring Green
        accent="#39FF14",  # Neon Green
        background="#0D0D0D",  # Almost Black
        surface="#1A1A1A",  # Very Dark Gray
        panel="#2A2A2A",  # Dark Gray
        dark=True,
    ),
    "nord": Theme(
        primary="#88C0D0",
        secondary="#81A1C1",
        accent="#B48EAD",
        foreground="#D8DEE9",
        background="#2E3440",
        success="#A3BE8C",
        warning="#EBCB8B",
        error="#BF616A",
        surface="#3B4252",
        panel="#434C5E",
        dark=True,
        variables={
            "block-cursor-background": "#88C0D0",
            "block-cursor-foreground": "#2E3440",
            "block-cursor-text-style": "none",
            "footer-key-foreground": "#88C0D0",
            "input-selection-background": "#81a1c1 35%",
            "button-color-foreground": "#2E3440",
            "button-focus-text-style": "reverse",
        },
    ),
    "gruvbox": Theme(
        primary="#85A598",
        secondary="#A89A85",
        warning="#fe8019",
        error="#fb4934",
        success="#b8bb26",
        accent="#fabd2f",
        foreground="#fbf1c7",
        background="#282828",
        surface="#3c3836",
        panel="#504945",
        dark=True,
        variables={
            "block-cursor-foreground": "#fbf1c7",
            "input-selection-background": "#689d6a40",
            "button-color-foreground": "#282828",
        },
    ),
    "catppuccin-mocha": Theme(
        primary="#F5C2E7",
        secondary="#cba6f7",
        warning="#FAE3B0",
        error="#F28FAD",
        success="#ABE9B3",
        accent="#fab387",
        foreground="#cdd6f4",
        background="#181825",
        surface="#313244",
        panel="#45475a",
        dark=True,
        variables={
            "input-cursor-foreground": "#11111b",
            "input-cursor-background": "#f5e0dc",
            "input-selection-background": "#9399b2 30%",
            "border": "#b4befe",
            "border-blurred": "#585b70",
            "footer-background": "#45475a",
            "block-cursor-foreground": "#1e1e2e",
            "block-cursor-text-style": "none",
            "button-color-foreground": "#181825",
        },
    ),
    "dracula": Theme(
        primary="#BD93F9",
        secondary="#6272A4",
        warning="#FFB86C",
        error="#FF5555",
        success="#50FA7B",
        accent="#FF79C6",
        background="#282A36",
        surface="#2B2E3B",
        panel="#313442",
        foreground="#F8F8F2",
        dark=True,
        variables={
            "button-color-foreground": "#282A36",
        },
    ),
    "tokyo-night": Theme(
        primary="#BB9AF7",
        secondary="#7AA2F7",
        warning="#E0AF68",  # Yellow
        error="#F7768E",  # Red
        success="#9ECE6A",  # Green
        accent="#FF9E64",  # Orange
        foreground="#a9b1d6",
        background="#1A1B26",  # Background
        surface="#24283B",  # Surface
        panel="#414868",  # Panel
        dark=True,
        variables={
            "button-color-foreground": "#24283B",
        },
    ),
    "flexoki": Theme(
        primary="#205EA6",  # blue
        secondary="#24837B",  # cyan
        warning="#AD8301",  # yellow
        error="#AF3029",  # red
        success="#66800B",  # green
        accent="#9B76C8",  # purple light
        background="#100F0F",  # base.black
        surface="#1C1B1A",  # base.950
        panel="#282726",  # base.900
        foreground="#FFFCF0",  # base.paper
        dark=True,
        variables={
            "input-cursor-foreground": "#5E409D",
            "input-cursor-background": "#FFFCF0",
            "input-selection-background": "#6F6E69 35%",  # base.600 with opacity
            "button-color-foreground": "#FFFCF0",
        },
    ),
}
