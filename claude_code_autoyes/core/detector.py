"""Claude instance detection in tmux panes."""

import re
import subprocess
from datetime import datetime

from .models import ClaudeInstance


class ClaudeDetector:
    """Detects Claude instances in tmux panes.

    Provides methods to discover running Claude instances in tmux sessions
    by analyzing process information and pane content. Uses both process-based
    detection (preferred) and content-based detection (fallback).
    """

    def find_child_processes(self, parent_pid: str) -> list[dict[str, str]]:
        """Find child processes of a given parent PID.

        Args:
            parent_pid: The parent process ID to search for children

        Returns:
            List of dictionaries with 'pid', 'ppid', and 'command' keys
            for each child process found.
        """
        try:
            result = subprocess.run(
                ["ps", "-eo", "pid,ppid,command"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                return []

            children = []
            lines = result.stdout.strip().split("\n")

            # Skip header line
            for line in lines[1:]:
                parts = line.strip().split(None, 2)  # Split into max 3 parts
                if len(parts) >= 3:
                    pid, ppid, command = parts
                    if ppid == parent_pid:
                        children.append(
                            {
                                "pid": pid,
                                "ppid": ppid,
                                "command": command,
                            }
                        )

            return children

        except (subprocess.SubprocessError, OSError):
            return []

    def get_pane_process_info(self, pane_id: str) -> dict[str, str]:
        """Get process information for a tmux pane.

        Args:
            pane_id: Tmux pane identifier (e.g., "session:window.pane")

        Returns:
            Dictionary with 'command' and 'pid' keys, or empty dict if failed.
        """
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
        except (subprocess.SubprocessError, ValueError, OSError):
            return {}

    def is_claude_process(self, process_info: dict[str, str]) -> bool:
        """Check if a process is a Claude instance based on process info.

        Enhanced to check child processes for Claude instances that run
        as children of shell processes.

        Args:
            process_info: Dictionary with command and pid information.

        Returns:
            True if the process appears to be a Claude instance.
        """
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
                        if any(
                            indicator in full_command for indicator in claude_indicators
                        ):
                            return True
            except (subprocess.SubprocessError, OSError):
                pass

        # Enhanced: Check child processes for Claude instances
        # This handles the common case where tmux reports a shell (node)
        # but Claude actually runs as a child process
        if pid:
            try:
                children = self.find_child_processes(pid)
                for child in children:
                    child_command = child.get("command", "")
                    # Look for direct Claude command in children
                    if child_command == "claude":
                        return True
                    # Also check if child command starts with "claude" (e.g., "claude --some-flag")
                    if child_command.startswith("claude "):
                        return True
            except Exception:
                # Don't let child process discovery failures break detection
                pass

        return False

    def _has_active_claude_cursor(self, content: str) -> bool:
        """Check for active Claude interface with cursor."""
        return "│ >" in content and "╰─" in content

    def _has_claude_welcome_screen(self, content: str) -> bool:
        """Check for Claude welcome/startup screen."""
        return "Welcome to Claude Code" in content

    def _has_claude_interface_patterns(self, content: str) -> bool:
        """Check for Claude interface patterns with specific indicators."""
        # Be more specific to avoid false positives from reports/logs about Claude
        return (
            "Claude Code" in content
            and "╰─" in content
            and ("cwd:" in content or "/help for help" in content or "Tip:" in content)
        )

    def _has_claude_update_notification(self, content: str) -> bool:
        """Check for Claude update notification."""
        return "✓ Update installed" in content and "Restart to apply" in content

    def is_claude_pane(self, content: str) -> bool:
        """Detect if tmux pane content contains a Claude instance.

        This is a fallback method - prefer process detection.
        Uses multiple pattern detection methods for comprehensive coverage.
        """
        if not content:
            return False

        # Check all pattern types
        return (
            self._has_active_claude_cursor(content)
            or self._has_claude_welcome_screen(content)
            or self._has_claude_interface_patterns(content)
            or self._has_claude_update_notification(content)
        )

    def has_auto_yes_prompt(self, content: str) -> bool:
        """Check if pane has a prompt that auto-yes should respond to."""
        if not content:
            return False

        prompts = ["Do you want to", "Would you like to", "Proceed?", "❯ 1. Yes"]

        return any(prompt in content for prompt in prompts)

    def get_tmux_sessions(self) -> list[str]:
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

    def get_tmux_panes(self) -> list[str]:
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

    def find_claude_instances(self) -> list[ClaudeInstance]:
        """Find all Claude instances in tmux panes.

        Scans all tmux panes and identifies which ones contain Claude instances.
        Uses process-based detection first, falls back to content analysis.

        Returns:
            List of ClaudeInstance objects representing detected instances.
        """
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
                                    except (AttributeError, ValueError):
                                        pass
                    except (subprocess.SubprocessError, OSError, FileNotFoundError):
                        pass

                instance = ClaudeInstance(
                    session=session, pane=pane, is_claude=True, last_prompt=last_prompt
                )
                instances.append(instance)

        return instances
