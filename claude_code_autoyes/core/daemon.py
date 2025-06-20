"""Daemon management for claude-autoyes."""

import os
import subprocess
import time


class DaemonManager:
    """Manages the auto-yes daemon process."""

    def __init__(self):
        self.pid_file = os.path.expanduser("~/.claude-autoyes-daemon.pid")
        self.log_file = "/tmp/claude-autoyes.log"

    def is_running(self) -> bool:
        """Check if daemon is currently running."""
        if not os.path.exists(self.pid_file):
            return False

        try:
            with open(self.pid_file, "r") as f:
                pid = int(f.read().strip())

            # Check if process is actually running using ps instead of kill signal
            result = subprocess.run(
                ["ps", "-p", str(pid)], capture_output=True, text=True
            )
            if result.returncode == 0:
                # Double-check it's our daemon by looking for the script name
                ps_output = result.stdout
                if "claude-autoyes-daemon.sh" in ps_output or "bash" in ps_output:
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

    def start(self, config) -> bool:
        """Start the auto-yes daemon."""
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
            with open(script_path, "w") as f:
                f.write(daemon_script)
            os.chmod(script_path, 0o755)

            # Start daemon in background
            subprocess.Popen(
                ["/bin/bash", script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Wait a moment for startup
            time.sleep(0.5)

            return self.is_running()

        except Exception:
            return False

    def stop(self) -> bool:
        """Stop the auto-yes daemon."""
        if not self.is_running():
            return True

        try:
            with open(self.pid_file, "r") as f:
                pid = int(f.read().strip())

            os.kill(pid, 15)  # SIGTERM

            # Wait for cleanup
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
        """Get daemon status string."""
        if self.is_running():
            try:
                with open(self.pid_file, "r") as f:
                    pid = f.read().strip()
                return f"✓ Daemon: Running (PID: {pid})"
            except Exception:
                return "✓ Daemon: Running"
        else:
            return "✗ Daemon: Not running"
