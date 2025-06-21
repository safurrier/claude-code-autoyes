"""Constants for claude-code-autoyes."""

# Process identification
DAEMON_PROCESS_NAMES = [
    "claude_code_autoyes",
    "claude-code-autoyes",
    "claude-autoyes",
]

# File paths
DEFAULT_LOG_FILE = "/tmp/claude-autoyes.log"
PID_FILE_NAME = "~/.claude-autoyes-daemon.pid"
CONFIG_FILE_NAME = "~/.claude-autoyes-config"

# Daemon configuration
DEFAULT_SLEEP_INTERVAL = 3.0
DEFAULT_REFRESH_INTERVAL = 30
PROMPT_RESPONSE_PAUSE = 2.0  # Pause after sending Enter key

# Prompt detection patterns
CLAUDE_PROMPT_PATTERNS = [
    r"Do you want to",
    r"Would you like to",
    r"Proceed\?",
    r"❯ 1\. Yes",
]

# Tmux configuration
TMUX_CAPTURE_LINES = "-10"  # Number of lines to capture from pane history
