"""Daemon management for claude-autoyes."""

import os
import subprocess
import time
import threading
import logging
from .daemon_service import DaemonService


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
                # Double-check it's our daemon by looking for Python process
                ps_output = result.stdout
                if "python" in ps_output.lower():
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
        """Start the auto-yes daemon using Python service."""
        if self.is_running():
            return True

        try:
            # Configure logging to file (equivalent to bash LOG_FILE)
            logging.basicConfig(
                filename=self.log_file,
                level=logging.INFO,
                format="[%(asctime)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

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

        except Exception as e:
            logging.error(f"Failed to start daemon: {e}")
            return False

    def _run_daemon_with_pid_management(self, daemon_service):
        """Run daemon service with PID file management."""
        try:
            # Write PID file (equivalent to bash echo $$ > "$PID_FILE")
            with open(self.pid_file, "w") as f:
                f.write(str(os.getpid()))

            logging.info(f"Claude auto-yes daemon started with PID {os.getpid()}")

            # Start monitoring loop
            daemon_service.start_monitoring_loop()

        except Exception as e:
            logging.error(f"Daemon error: {e}")
        finally:
            # Cleanup PID file on exit (equivalent to bash cleanup function)
            if os.path.exists(self.pid_file):
                os.unlink(self.pid_file)
            logging.info("Daemon shutting down")

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
