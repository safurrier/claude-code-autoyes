#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click>=8.1.7",
#     "textual>=0.89.0"
# ]
# ///

"""
Tool: claude-autoyes
Description: Interactive TUI for managing auto-yes across Claude instances
Author: Alex Furrier
Version: 0.1.0
"""

import json
import subprocess
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

import click
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Button, Header, Footer, Static
from textual.containers import Container, VerticalScroll


@dataclass
class ClaudeInstance:
    """Represents a detected Claude instance"""
    session: str
    pane: str
    is_claude: bool
    last_prompt: Optional[str] = None
    enabled: bool = False


class ClaudeDetector:
    """Detects Claude instances in tmux panes"""

    def get_pane_process_info(self, pane_id: str) -> Dict[str, str]:
        """Get process information for a tmux pane"""
        try:
            # Get current command and PID
            result = subprocess.run(
                ["tmux", "display-message", "-p", "-t", pane_id,
                 "-F", "#{pane_current_command}:#{pane_pid}"],
                capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                return {}

            parts = result.stdout.strip().split(':')
            if len(parts) != 2:
                return {}

            command, pid = parts
            return {"command": command, "pid": pid}
        except:
            return {}

    def is_claude_process(self, process_info: Dict[str, str]) -> bool:
        """Check if a process is a Claude instance based on process info"""
        if not process_info:
            return False

        command = process_info.get("command", "")
        pid = process_info.get("pid", "")

        # We ONLY want actual Claude instances, not the claude-squad wrapper
        # Exclude claude-squad commands
        if command in ["claude-squad", "cs"]:
            return False

        # Direct claude command (rare but possible)
        if command == "claude":
            return True

        # Most commonly, Claude runs as a node process
        if command == "node" and pid:
            try:
                # Get full process command line
                result = subprocess.run(
                    ["ps", "-p", pid, "-o", "args="],
                    capture_output=True, text=True, check=False
                )
                if result.returncode == 0:
                    full_command = result.stdout.strip()
                    # Only match actual Claude binary paths, not claude-squad
                    claude_indicators = [
                        "/bin/claude",  # npm global bin
                        "/.claude/",    # home directory install
                        "/claude.js",   # possible direct execution
                    ]
                    # Exclude claude-squad even in node processes
                    if "claude-squad" not in full_command:
                        return any(indicator in full_command for indicator in claude_indicators)
            except:
                pass

        return False

    def is_claude_pane(self, content: str) -> bool:
        """Detect if tmux pane content contains a Claude instance"""
        # This is now a fallback method - prefer process detection
        if not content:
            return False

        # Primary signature: the box pattern with cursor (active Claude)
        if "│ >" in content and "╰─" in content:
            return True

        # Secondary: Claude update notification
        if "✓ Update installed" in content and "Restart to apply" in content:
            return True

        return False

    def has_auto_yes_prompt(self, content: str) -> bool:
        """Check if pane has a prompt that auto-yes should respond to"""
        if not content:
            return False

        prompts = [
            "Do you want to",
            "Would you like to",
            "Proceed?",
            "❯ 1. Yes"
        ]

        return any(prompt in content for prompt in prompts)

    def get_tmux_sessions(self) -> List[str]:
        """Get list of tmux session names"""
        try:
            result = subprocess.run(
                ["tmux", "list-sessions"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                return []

            sessions = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    session_name = line.split(':')[0]
                    sessions.append(session_name)
            return sessions
        except (subprocess.SubprocessError, FileNotFoundError):
            return []

    def get_tmux_panes(self) -> List[str]:
        """Get list of all tmux panes in format session:window.pane"""
        try:
            result = subprocess.run(
                ["tmux", "list-panes", "-a", "-F", "#{session_name}:#{window_index}.#{pane_index}"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                return []

            return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        except (subprocess.SubprocessError, FileNotFoundError):
            return []

    def capture_pane_content(self, pane_id: str) -> str:
        """Capture content from a tmux pane"""
        try:
            result = subprocess.run(
                ["tmux", "capture-pane", "-p", "-t", pane_id, "-S", "-30"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                return ""
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    def find_claude_instances(self) -> List[ClaudeInstance]:
        """Find all Claude instances in tmux panes"""
        instances = []
        panes = self.get_tmux_panes()

        for pane_id in panes:
            # First try process-based detection
            process_info = self.get_pane_process_info(pane_id)
            command = process_info.get("command", "")

            # If it's claude-squad, skip it entirely (don't do content detection)
            if command in ["claude-squad", "cs"]:
                continue

            is_claude = self.is_claude_process(process_info)

            # If not detected by process, try content-based detection as fallback
            # But only for non-excluded processes
            if not is_claude and command not in ["nvim", "vim", "less", "more", "cat"]:
                content = self.capture_pane_content(pane_id)
                is_claude = self.is_claude_pane(content)
            else:
                # Still capture content for prompt detection
                content = self.capture_pane_content(pane_id) if is_claude else ""

            if is_claude:
                session, pane = pane_id.split(':', 1)
                last_prompt = None

                if self.has_auto_yes_prompt(content):
                    last_prompt = datetime.now().strftime("%H:%M:%S")
                else:
                    # Check if we've seen prompts recently by looking at logs
                    try:
                        log_result = subprocess.run(
                            ["tail", "-20", "/tmp/claude-autoyes.log"],
                            capture_output=True, text=True, check=False
                        )
                        if log_result.returncode == 0 and pane_id in log_result.stdout:
                            # Look for recent prompt entries for this pane
                            for line in log_result.stdout.split('\n'):
                                if f"Found prompt in {pane_id}:" in line:
                                    # Extract timestamp from log line
                                    try:
                                        import re
                                        time_match = re.search(r'(\d{2}:\d{2}:\d{2})', line)
                                        if time_match:
                                            last_prompt = time_match.group(1)
                                            break
                                    except:
                                        pass
                    except:
                        pass

                instance = ClaudeInstance(
                    session=session,
                    pane=pane,
                    is_claude=True,
                    last_prompt=last_prompt
                )
                instances.append(instance)

        return instances


class ConfigManager:
    """Manages configuration for claude-autoyes"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.path.expanduser("~/.claude-autoyes-config")
        self.enabled_sessions = set()
        self.daemon_enabled = False
        self.refresh_interval = 30
        self.load()

    def load(self) -> Dict:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.enabled_sessions = set(data.get("enabled_sessions", []))
                    self.daemon_enabled = data.get("daemon_enabled", False)
                    self.refresh_interval = data.get("refresh_interval", 30)
                    return data
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return {}

    def save(self, config: Optional[Dict] = None) -> None:
        """Save configuration to file"""
        if config is None:
            config = {
                "enabled_sessions": list(self.enabled_sessions),
                "daemon_enabled": self.daemon_enabled,
                "refresh_interval": self.refresh_interval
            }

        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except OSError:
            pass

    def toggle_session(self, session_pane: str) -> bool:
        """Toggle a session on/off. Returns new state (True=enabled)"""
        if session_pane in self.enabled_sessions:
            self.enabled_sessions.remove(session_pane)
            enabled = False
        else:
            self.enabled_sessions.add(session_pane)
            enabled = True

        self.save()
        return enabled

    def enable_all(self, sessions: List[str]) -> None:
        """Enable all provided sessions"""
        self.enabled_sessions.update(sessions)
        self.save()

    def disable_all(self) -> None:
        """Disable all sessions"""
        self.enabled_sessions.clear()
        self.save()

    def is_enabled(self, session_pane: str) -> bool:
        """Check if a session is enabled"""
        return session_pane in self.enabled_sessions


class DaemonManager:
    """Manages the auto-yes daemon process"""

    def __init__(self):
        self.pid_file = os.path.expanduser("~/.claude-autoyes-daemon.pid")
        self.log_file = "/tmp/claude-autoyes.log"

    def is_running(self) -> bool:
        """Check if daemon is currently running"""
        if not os.path.exists(self.pid_file):
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process is actually running using ps instead of kill signal
            import subprocess
            result = subprocess.run(['ps', '-p', str(pid)],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Double-check it's our daemon by looking for the script name
                ps_output = result.stdout
                if 'claude-autoyes-daemon.sh' in ps_output or 'bash' in ps_output:
                    return True

            # PID exists but process is not our daemon, clean up
            if os.path.exists(self.pid_file):
                os.unlink(self.pid_file)
            return False

        except (ValueError, FileNotFoundError, subprocess.SubprocessError):
            # Clean up stale PID file
            if os.path.exists(self.pid_file):
                os.unlink(self.pid_file)
            return False

    def start(self, config: ConfigManager) -> bool:
        """Start the auto-yes daemon"""
        if self.is_running():
            return True

        # Create a more robust daemon script
        daemon_script = f'''#!/bin/bash
LOG_FILE="{self.log_file}"
PID_FILE="{self.pid_file}"
CONFIG_FILE="{config.config_file}"

# Function to log messages
log_msg() {{
    echo "[$(date)] $1" >> "$LOG_FILE"
}}

# Function to cleanup on exit
cleanup() {{
    log_msg "Daemon shutting down"
    rm -f "$PID_FILE"
    exit 0
}}

trap cleanup SIGTERM SIGINT

echo $$ > "$PID_FILE"
log_msg "Claude auto-yes daemon started with PID $$"

# Test if Python works and config exists
if ! command -v python3 >/dev/null 2>&1; then
    log_msg "ERROR: python3 not found in PATH"
    cleanup
fi

if [ ! -f "$CONFIG_FILE" ]; then
    log_msg "WARNING: Config file not found: $CONFIG_FILE"
fi

# Simple approach - read config directly in bash
while true; do
    if [ -f "$CONFIG_FILE" ]; then
        # Parse JSON config to get enabled sessions
        enabled_sessions=$(python3 -c "
import json
import sys
try:
    with open('$CONFIG_FILE', 'r') as f:
        data = json.load(f)
        sessions = data.get('enabled_sessions', [])
        if sessions:
            for session in sessions:
                print(session)
        else:
            print('')  # Print empty line if no sessions
except Exception as e:
    print('')  # Silent fail
" 2>>"$LOG_FILE")

        if [ -n "$enabled_sessions" ]; then
            log_msg "Monitoring $(echo "$enabled_sessions" | wc -l) enabled sessions"

            echo "$enabled_sessions" | while read -r session_pane; do
                [ -z "$session_pane" ] && continue

                session_name=$(echo "$session_pane" | cut -d: -f1)

                # Check if tmux session exists
                if tmux has-session -t "$session_name" 2>/dev/null; then
                    # Capture pane content
                    content=$(tmux capture-pane -p -t "$session_pane" -S -10 2>/dev/null)

                    if [ -n "$content" ]; then
                        # Look for common Claude prompts
                        if echo "$content" | grep -q -E "(Do you want to|Would you like to|Proceed\\?|❯ 1\\. Yes)"; then
                            prompt_line=$(echo "$content" | grep -E "(Do you want to|Would you like to|Proceed\\?|❯ 1\\. Yes)" | tail -1)
                            log_msg "Found prompt in $session_pane: $prompt_line"

                            # Send Enter key
                            if tmux send-keys -t "$session_pane" Enter 2>>"$LOG_FILE"; then
                                log_msg "Sent Enter to $session_pane"
                            else
                                log_msg "ERROR: Failed to send keys to $session_pane"
                            fi

                            sleep 2  # Longer pause after responding
                        fi
                    fi
                else
                    log_msg "Session $session_name not found"
                fi
            done
        else
            log_msg "No enabled sessions found"
        fi
    else
        log_msg "Config file not found: $CONFIG_FILE"
    fi

    sleep 3  # Check every 3 seconds instead of 0.3
done
'''

        try:
            # Write and execute daemon script
            script_path = "/tmp/claude-autoyes-daemon.sh"
            with open(script_path, 'w') as f:
                f.write(daemon_script)
            os.chmod(script_path, 0o755)

            # Start daemon in background
            subprocess.Popen(["/bin/bash", script_path],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)

            # Wait a moment for startup
            import time
            time.sleep(0.5)

            return self.is_running()

        except Exception as e:
            return False

    def stop(self) -> bool:
        """Stop the auto-yes daemon"""
        if not self.is_running():
            return True

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            os.kill(pid, 15)  # SIGTERM

            # Wait for cleanup
            import time
            time.sleep(0.5)

            # Force kill if still running
            try:
                os.kill(pid, 9)  # SIGKILL
            except ProcessLookupError:
                pass

            # Clean up PID file
            if os.path.exists(self.pid_file):
                os.unlink(self.pid_file)

            return True

        except Exception:
            return False

    def get_status(self) -> str:
        """Get daemon status string"""
        if self.is_running():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = f.read().strip()
                return f"✓ Daemon: Running (PID: {pid})"
            except:
                return "✓ Daemon: Running"
        else:
            return "✗ Daemon: Not running"


class ClaudeAutoYesApp(App):
    """Main Textual TUI application"""

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

    def __init__(self):
        super().__init__()
        self.detector = ClaudeDetector()
        self.config = ConfigManager()
        self.daemon = DaemonManager()
        self.instances = []

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
            classes="button-container"
        )

        # Simple shortcuts at bottom
        yield Static("↑↓: Navigate | Enter: Toggle | Space: Toggle | 1-9: Quick Toggle | d: Toggle Daemon | r: Refresh | q: Quit", id="shortcuts")

    def on_mount(self) -> None:
        """Initialize the table and load data"""
        table = self.query_one(DataTable)
        table.add_columns("#", "Session", "Pane", "Status", "Last Prompt")
        table.cursor_type = "row"
        table.zebra_stripes = True  # Alternating row colors
        table.show_cursor = True    # Show cursor for navigation
        table.can_focus = True      # Allow keyboard focus

        self.refresh_instances()
        self.update_daemon_status()

        # Set focus to table for arrow key navigation
        self.set_focus(table)

        # Set up auto-refresh
        self.set_interval(self.config.refresh_interval, self.refresh_instances)
        self.set_interval(5, self.update_daemon_status)  # Update daemon status every 5 seconds

    def refresh_instances(self) -> None:
        """Refresh the list of Claude instances"""
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
        """Update the daemon status display"""
        status_bar = self.query_one("#status-bar")
        status_bar.update(self.daemon.get_status())

    def update_table(self) -> None:
        """Update the DataTable with current instances"""
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
                key=str(i)
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
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
        """Toggle first Claude instance"""
        self._toggle_instance_by_index(0)

    def key_2(self) -> None:
        """Toggle second Claude instance"""
        self._toggle_instance_by_index(1)

    def key_3(self) -> None:
        """Toggle third Claude instance"""
        self._toggle_instance_by_index(2)

    def key_4(self) -> None:
        """Toggle fourth Claude instance"""
        self._toggle_instance_by_index(3)

    def key_5(self) -> None:
        """Toggle fifth Claude instance"""
        self._toggle_instance_by_index(4)

    def key_6(self) -> None:
        """Toggle sixth Claude instance"""
        self._toggle_instance_by_index(5)

    def key_7(self) -> None:
        """Toggle seventh Claude instance"""
        self._toggle_instance_by_index(6)

    def key_8(self) -> None:
        """Toggle eighth Claude instance"""
        self._toggle_instance_by_index(7)

    def key_9(self) -> None:
        """Toggle ninth Claude instance"""
        self._toggle_instance_by_index(8)

    def key_q(self) -> None:
        """Quit the application"""
        # Stop daemon before quitting
        if self.daemon.is_running():
            self.daemon.stop()
        self.exit()

    def key_r(self) -> None:
        """Refresh instances"""
        self.refresh_instances()

    def key_d(self) -> None:
        """Toggle daemon start/stop"""
        if self.daemon.is_running():
            if self.daemon.stop():
                self.update_daemon_status()
                self.notify("Daemon stopped", severity="warning")
            else:
                self.notify("Failed to stop daemon", severity="error")
        else:
            if self.daemon.start(self.config):
                self.update_daemon_status()
                self.notify("Daemon started", severity="success")
            else:
                self.notify("Failed to start daemon", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection (Enter key) to toggle instance"""
        if event.row_key is not None:
            instance_index = int(event.row_key.value)
            if 0 <= instance_index < len(self.instances):
                instance = self.instances[instance_index]
                pane_id = f"{instance.session}:{instance.pane}"
                self.config.toggle_session(pane_id)
                self.refresh_instances()
                self.notify(f"Toggled {pane_id}")

    def key_space(self) -> None:
        """Toggle currently highlighted instance with space bar"""
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
        """Helper method to toggle instance by index"""
        if 0 <= index < len(self.instances):
            instance = self.instances[index]
            pane_id = f"{instance.session}:{instance.pane}"
            self.config.toggle_session(pane_id)
            self.refresh_instances()
            self.notify(f"Toggled {pane_id}")

    def on_key(self, event) -> None:
        """Handle other keyboard shortcuts"""
        # Fallback for any other keys
        pass


@click.group()
def main():
    """Interactive TUI for managing auto-yes across Claude instances in tmux."""
    pass


@main.command()
def status():
    """Show current status"""
    detector = ClaudeDetector()
    config = ConfigManager()
    instances = detector.find_claude_instances()

    click.echo(f"Found {len(instances)} Claude instances:")
    for instance in instances:
        pane_id = f"{instance.session}:{instance.pane}"
        status = "ON" if config.is_enabled(pane_id) else "OFF"
        click.echo(f"  {pane_id} - [{status}]")


@main.command()
def tui():
    """Launch interactive TUI (default)"""
    app = ClaudeAutoYesApp()
    app.run()


@main.command("enable-all")
def enable_all():
    """Enable auto-yes for all Claude instances"""
    detector = ClaudeDetector()
    config = ConfigManager()
    instances = detector.find_claude_instances()

    session_panes = [f"{inst.session}:{inst.pane}" for inst in instances]
    config.enable_all(session_panes)
    click.echo(f"Enabled auto-yes for {len(session_panes)} instances")


@main.command("disable-all")
def disable_all():
    """Disable auto-yes for all Claude instances"""
    config = ConfigManager()
    config.disable_all()
    click.echo("Disabled auto-yes for all instances")


# Make TUI the default command
@main.result_callback()
def default_command(result, **kwargs):
    """If no subcommand is specified, run TUI"""
    pass


if __name__ == "__main__":
    # If no arguments, run TUI by default
    import sys
    if len(sys.argv) == 1:
        app = ClaudeAutoYesApp()
        app.run()
    else:
        main()

