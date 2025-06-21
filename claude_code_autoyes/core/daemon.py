"""Daemon management for claude-autoyes."""

import os
import subprocess
import threading
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import ConfigManager

from .constants import DAEMON_PROCESS_NAMES, DEFAULT_LOG_FILE, PID_FILE_NAME
from .daemon_service import DaemonService
from .logging_config import get_daemon_logger


class DaemonManager:
    """Manages the auto-yes daemon process.

    Provides functionality to start, stop, and monitor the daemon that
    automatically responds to Claude prompts in enabled tmux sessions.
    Handles PID file management and process lifecycle.
    """

    def __init__(self) -> None:
        self.pid_file = os.path.expanduser(PID_FILE_NAME)
        self.log_file = DEFAULT_LOG_FILE

    def is_running(self) -> bool:
        """Check if daemon is currently running.

        Returns:
            True if the daemon process is running and verified.
        """
        if not os.path.exists(self.pid_file):
            return False

        try:
            with open(self.pid_file) as f:
                pid = int(f.read().strip())

            # Check if process is actually running using ps instead of kill signal
            result = subprocess.run(
                ["ps", "-p", str(pid)], capture_output=True, text=True
            )
            if result.returncode == 0:
                # Double-check it's our daemon by looking for specific process signature
                ps_output = result.stdout
                if any(name in ps_output for name in DAEMON_PROCESS_NAMES):
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

    def start(self, config: "ConfigManager") -> bool:
        """Start the auto-yes daemon using Python service.

        Args:
            config: ConfigManager instance with daemon settings.

        Returns:
            True if daemon started successfully, False otherwise.
        """
        if self.is_running():
            return True

        try:
            # Set up centralized logging for daemon
            logger = get_daemon_logger(self.log_file)

            # Start Python daemon service in background thread
            daemon_service = DaemonService(config)
            daemon_thread = threading.Thread(
                target=self._run_daemon_with_pid_management,
                args=(daemon_service,),
                daemon=True,
            )
            daemon_thread.start()

            # Wait a moment for startup
            time.sleep(0.5)

            return self.is_running()

        except (OSError, RuntimeError, threading.ThreadError) as e:
            logger = get_daemon_logger(self.log_file)
            logger.error(f"Failed to start daemon: {e}")
            return False

    def _run_daemon_with_pid_management(self, daemon_service: DaemonService) -> None:
        """Run daemon service with PID file management."""
        logger = get_daemon_logger(self.log_file)

        try:
            # Write PID file (equivalent to bash echo $$ > "$PID_FILE")
            with open(self.pid_file, "w") as f:
                f.write(str(os.getpid()))

            logger.info(f"Claude auto-yes daemon started with PID {os.getpid()}")

            # Start monitoring loop
            daemon_service.start_monitoring_loop()

        except (OSError, subprocess.SubprocessError, RuntimeError) as e:
            logger.error(f"Daemon error: {e}")
        except KeyboardInterrupt:
            logger.info("Daemon stopped by user")
        finally:
            # Cleanup PID file on exit (equivalent to bash cleanup function)
            if os.path.exists(self.pid_file):
                os.unlink(self.pid_file)
            logger.info("Daemon shutting down")

    def stop(self) -> bool:
        """Stop the auto-yes daemon.

        Sends SIGTERM to the daemon process and cleans up PID file.

        Returns:
            True if daemon stopped successfully, False otherwise.
        """
        if not self.is_running():
            return True

        try:
            with open(self.pid_file) as f:
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

        except (OSError, ValueError, FileNotFoundError):
            return False

    def get_status(self) -> str:
        """Get daemon status string.

        Returns:
            Human-readable status message with PID if running.
        """
        if self.is_running():
            try:
                with open(self.pid_file) as f:
                    pid = f.read().strip()
                return f"✓ Daemon: Running (PID: {pid})"
            except (OSError, ValueError):
                return "✓ Daemon: Running"
        else:
            return "✗ Daemon: Not running"
