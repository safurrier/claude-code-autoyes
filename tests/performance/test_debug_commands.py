"""Tests for debug performance analysis CLI commands."""

import pytest
import subprocess
import tempfile
import os
from unittest.mock import patch


@pytest.mark.performance
class TestDebugCommands:
    """Test suite for performance debugging CLI commands."""

    def test_debug_profile_command_exists(self):
        """Debug profile command should be available."""
        result = subprocess.run(
            ["uv", "run", "python", "-m", "claude_code_autoyes", "debug", "profile", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "profile" in result.stdout.lower()

    def test_pyspy_integration_check(self):
        """Should detect if py-spy is available or provide installation guidance."""
        from claude_code_autoyes.commands.debug import DebugCommands
        debug_cmd = DebugCommands()
        pyspy_available = debug_cmd.check_pyspy_available()
        
        # Should return boolean and provide guidance if not available
        assert isinstance(pyspy_available, bool)
        
        if not pyspy_available:
            install_help = debug_cmd.get_pyspy_install_help()
            assert "pip install py-spy" in install_help or "cargo install py-spy" in install_help

    def test_profile_command_with_duration(self):
        """Profile command should accept duration parameter."""
        from claude_code_autoyes.commands.debug import DebugCommands
        debug_cmd = DebugCommands()
        
        # Skip if py-spy not available
        if not debug_cmd.check_pyspy_available():
            pytest.skip("py-spy not available for testing")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            profile_path = os.path.join(tmp_dir, "test_profile.svg")
            
            # Should be able to specify duration and output path
            result = debug_cmd.profile_tui(duration=5, output_path=profile_path)
            
            # If no TUI process is running, that's expected in test environment
            if "No running TUI process found" in result.error:
                pytest.skip("No TUI process running for profiling test")
            
            # If py-spy requires sudo (macOS), skip the test
            if "requires root" in result.error:
                pytest.skip("py-spy requires sudo on macOS")
            
            assert result.success, f"Profiling failed: {result.error}"
            assert os.path.exists(profile_path), "Profile output file should be created"


@pytest.mark.performance
class TestTUIDebugMode:
    """Test suite for TUI debug mode functionality."""

    def test_tui_debug_flag_launches(self):
        """TUI should accept --debug flag and launch successfully."""
        try:
            result = subprocess.run(
                ["uv", "run", "python", "-m", "claude_code_autoyes", "tui", "--debug"],
                timeout=3,
                capture_output=True,
                text=True
            )
            assert False, "TUI should timeout (still running) when launched successfully"
        except subprocess.TimeoutExpired:
            # Timeout means TUI is running - this is expected
            assert True, "TUI with debug flag launched successfully"

    def test_debug_mode_enables_performance_overlay(self):
        """Debug mode should show performance metrics in TUI."""
        from claude_code_autoyes.tui.app import ClaudeAutoYesApp
        
        app = ClaudeAutoYesApp(debug_mode=True)
        
        # Should have debug overlay component when in debug mode
        assert hasattr(app, 'debug_overlay'), "Debug mode should add debug_overlay attribute"
        assert app.debug_mode is True, "Debug mode should be enabled"

    def test_performance_metrics_collection_in_debug_mode(self):
        """Debug mode should collect performance metrics."""
        from claude_code_autoyes.core.performance import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        metrics = monitor.collect_current_metrics()
        
        # Should collect basic performance data
        assert hasattr(metrics, 'timestamp'), "Metrics should have timestamp"
        assert hasattr(metrics, 'memory_usage_mb'), "Metrics should track memory"
        assert hasattr(metrics, 'cpu_percent'), "Metrics should track CPU"
        assert metrics.timestamp > 0, "Timestamp should be valid"