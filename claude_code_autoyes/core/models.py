"""Data models for claude-code-autoyes."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClaudeInstance:
    """Represents a detected Claude instance."""

    session: str
    pane: str
    is_claude: bool
    last_prompt: Optional[str] = None
    enabled: bool = False
