"""Claude instance detection in tmux panes."""

import re
import subprocess
from datetime import datetime
from typing import Dict, List

from .models import ClaudeInstance


class ClaudeDetector:
    """Detects Claude instances in tmux panes."""

    def get_pane_process_info(self, pane_id: str) -> Dict[str, str]:
        """Get process information for a tmux pane."""
        try:
            # Get current command and PID
            result = subprocess.run(
                [
                    "tmux",
                    "display-message",
                    "-p",
                    "-t",
                    pane_id,
                    "-F",
                    "#{pane_current_command}:#{pane_pid}",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return {}

            parts = result.stdout.strip().split(":")
            if len(parts) != 2:
                return {}

            command, pid = parts
            return {"command": command, "pid": pid}
        except:
            return {}

    def is_claude_process(self, process_info: Dict[str, str]) -> bool:
        """Check if a process is a Claude instance based on process info."""
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
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    full_command = result.stdout.strip()
                    # Only match actual Claude binary paths, not claude-squad
                    claude_indicators = [
                        "/bin/claude",  # npm global bin
                        "/.claude/",  # home directory install
                        "/claude.js",  # possible direct execution
                    ]
                    # Exclude claude-squad even in node processes
                    if "claude-squad" not in full_command:
                        return any(
                            indicator in full_command for indicator in claude_indicators
                        )
            except:
                pass

        return False

    def is_claude_pane(self, content: str) -> bool:
        """Detect if tmux pane content contains a Claude instance."""
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
        """Check if pane has a prompt that auto-yes should respond to."""
        if not content:
            return False

        prompts = ["Do you want to", "Would you like to", "Proceed?", "❯ 1. Yes"]

        return any(prompt in content for prompt in prompts)

    def get_tmux_sessions(self) -> List[str]:
        """Get list of tmux session names."""
        try:
            result = subprocess.run(
                ["tmux", "list-sessions"], capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                return []

            sessions = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    session_name = line.split(":")[0]
                    sessions.append(session_name)
            return sessions
        except (subprocess.SubprocessError, FileNotFoundError):
            return []

    def get_tmux_panes(self) -> List[str]:
        """Get list of all tmux panes in format session:window.pane."""
        try:
            result = subprocess.run(
                [
                    "tmux",
                    "list-panes",
                    "-a",
                    "-F",
                    "#{session_name}:#{window_index}.#{pane_index}",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return []

            return [
                line.strip()
                for line in result.stdout.strip().split("\n")
                if line.strip()
            ]
        except (subprocess.SubprocessError, FileNotFoundError):
            return []

    def capture_pane_content(self, pane_id: str) -> str:
        """Capture content from a tmux pane."""
        try:
            result = subprocess.run(
                ["tmux", "capture-pane", "-p", "-t", pane_id, "-S", "-30"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return ""
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    def find_claude_instances(self) -> List[ClaudeInstance]:
        """Find all Claude instances in tmux panes."""
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
                session, pane = pane_id.split(":", 1)
                last_prompt = None

                if self.has_auto_yes_prompt(content):
                    last_prompt = datetime.now().strftime("%H:%M:%S")
                else:
                    # Check if we've seen prompts recently by looking at logs
                    try:
                        log_result = subprocess.run(
                            ["tail", "-20", "/tmp/claude-autoyes.log"],
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                        if log_result.returncode == 0 and pane_id in log_result.stdout:
                            # Look for recent prompt entries for this pane
                            for line in log_result.stdout.split("\n"):
                                if f"Found prompt in {pane_id}:" in line:
                                    # Extract timestamp from log line
                                    try:
                                        time_match = re.search(
                                            r"(\d{2}:\d{2}:\d{2})", line
                                        )
                                        if time_match:
                                            last_prompt = time_match.group(1)
                                            break
                                    except:
                                        pass
                    except:
                        pass

                instance = ClaudeInstance(
                    session=session, pane=pane, is_claude=True, last_prompt=last_prompt
                )
                instances.append(instance)

        return instances
