"""Tests for TUI startup performance measurement."""

import pytest
import subprocess
import time


@pytest.mark.performance
class TestStartupPerformance:
    """Test suite for TUI startup performance analysis."""

    def test_tui_startup_baseline_measurement(self):
        """Measure and establish TUI startup time baseline."""
        # This test should FAIL initially - StartupTimer doesn't exist yet
        try:
            from claude_code_autoyes.core.performance import StartupTimer
            timer = StartupTimer()
            
            startup_time = timer.measure_tui_startup()
            
            # Reasonable default: startup should be under 1000ms based on user needs
            assert startup_time < 1.0, f"TUI startup time {startup_time:.3f}s exceeds 1.0s threshold"
            assert startup_time > 0.1, f"Startup time {startup_time:.3f}s seems unrealistically fast"
        except ImportError:
            pytest.fail("StartupTimer module should exist")

    def test_tui_startup_timeout_detection(self):
        """Use timeout-based pattern to measure startup performance."""
        # Following existing TUI testing convention from codebase analysis
        start_time = time.perf_counter()
        
        try:
            result = subprocess.run(
                ["uv", "run", "python", "-m", "claude_code_autoyes", "tui"],
                timeout=2.0,  # 2 second timeout for measurement
                capture_output=True,
                text=True
            )
            # If we get here, TUI exited quickly (probably failed)
            assert result.returncode in [0, 130], f"Bad exit code: {result.returncode}"
            assert "error" not in result.stderr.lower(), f"Error in stderr: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            # Timeout = process is still running = successful launch
            elapsed = time.perf_counter() - start_time
            
            # This is where we measure startup performance
            # The timeout means TUI launched successfully
            assert elapsed >= 2.0, "Should have timed out after 2 seconds"
            
            # For actual startup measurement, we need the StartupTimer
            # This test should FAIL until we implement it
            try:
                from claude_code_autoyes.core.performance import StartupTimer
                timer = StartupTimer()
                actual_startup = timer.get_last_startup_time()
                assert actual_startup < 1.0, f"Startup took {actual_startup:.3f}s, expected < 1.0s"
            except ImportError:
                pytest.fail("StartupTimer module should exist for measuring startup time")

    def test_multiple_startup_measurements_for_stability(self):
        """Multiple startup measurements should be consistent."""
        # This test should FAIL initially - StartupTimer doesn't exist yet
        try:
            from claude_code_autoyes.core.performance import StartupTimer
            timer = StartupTimer()
            
            startup_times = []
            for _ in range(3):
                startup_time = timer.measure_tui_startup()
                startup_times.append(startup_time)
                time.sleep(0.5)  # Brief pause between measurements
            
            # Check consistency - no measurement should vary by more than 50%
            avg_time = sum(startup_times) / len(startup_times)
            for startup_time in startup_times:
                variance = abs(startup_time - avg_time) / avg_time
                assert variance < 0.5, f"Startup time variance too high: {variance:.2%}"
            
            # All measurements should meet performance threshold
            for startup_time in startup_times:
                assert startup_time < 1.0, f"Startup time {startup_time:.3f}s exceeds threshold"
        except ImportError:
            pytest.fail("StartupTimer module should exist")

    def test_startup_performance_factors_measurement(self):
        """Should measure different factors contributing to startup time."""
        # This test should FAIL initially - detailed measurement doesn't exist yet
        try:
            from claude_code_autoyes.core.performance import StartupTimer
            timer = StartupTimer()
            
            breakdown = timer.measure_startup_breakdown()
            
            # Should break down startup into components
            assert hasattr(breakdown, 'import_time'), "Should measure import time"
            assert hasattr(breakdown, 'config_load_time'), "Should measure config loading"
            assert hasattr(breakdown, 'tui_init_time'), "Should measure TUI initialization"
            assert hasattr(breakdown, 'first_render_time'), "Should measure first render"
            
            # Total should equal sum of parts (approximately)
            total_measured = (breakdown.import_time + breakdown.config_load_time + 
                             breakdown.tui_init_time + breakdown.first_render_time)
            
            assert abs(breakdown.total_time - total_measured) < 0.1, "Breakdown should sum to total"
            
            # Identify potential bottlenecks
            if breakdown.import_time > 0.3:
                pytest.fail(f"Import time too high: {breakdown.import_time:.3f}s")
            if breakdown.config_load_time > 0.1:
                pytest.fail(f"Config load time too high: {breakdown.config_load_time:.3f}s")
            if breakdown.tui_init_time > 0.4:
                pytest.fail(f"TUI init time too high: {breakdown.tui_init_time:.3f}s")
        except ImportError:
            pytest.fail("StartupTimer module should exist")


@pytest.mark.performance  
class TestNavigationPerformance:
    """Test suite for TUI navigation responsiveness."""

    def test_navigation_response_time_measurement(self):
        """Should measure navigation action response times."""
        # This test should FAIL initially - navigation measurement doesn't exist yet
        try:
            from claude_code_autoyes.core.performance import NavigationTimer
            
            nav_timer = NavigationTimer()
            
            # Should measure common navigation actions
            response_times = nav_timer.measure_navigation_actions([
                'arrow_down',
                'arrow_up', 
                'enter',
                'space',
                'tab'
            ])
            
            # Each action should be under 100ms threshold
            for action, response_time in response_times.items():
                assert response_time < 0.1, f"Navigation action '{action}' took {response_time:.3f}s"
                assert response_time > 0, f"Response time for '{action}' should be positive"
        except ImportError:
            pytest.fail("NavigationTimer module should exist")

    def test_large_dataset_navigation_performance(self):
        """Navigation should remain responsive with large datasets."""
        # This test should FAIL initially - large dataset testing doesn't exist yet
        try:
            from claude_code_autoyes.core.performance import NavigationTimer
            
            nav_timer = NavigationTimer()
            
            # Simulate large dataset (100+ items)
            large_dataset_size = 100
            response_times = nav_timer.measure_with_large_dataset(large_dataset_size)
            
            # Navigation should still be responsive even with large datasets
            assert response_times.average < 0.1, f"Average navigation with large dataset: {response_times.average:.3f}s"
            assert response_times.p95 < 0.2, f"95th percentile too slow: {response_times.p95:.3f}s"
            assert response_times.max < 0.5, f"Max response time too slow: {response_times.max:.3f}s"
        except ImportError:
            pytest.fail("NavigationTimer module should exist")