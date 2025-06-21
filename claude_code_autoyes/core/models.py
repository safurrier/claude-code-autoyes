"""Data models for claude-code-autoyes."""

from dataclasses import dataclass


@dataclass
class ClaudeInstance:
    """Represents a detected Claude instance."""

    session: str
    pane: str
    is_claude: bool
    last_prompt: str | None = None
    enabled: bool = False
