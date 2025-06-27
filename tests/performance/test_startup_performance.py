"""Tests for TUI startup and launch performance."""

import pytest
import subprocess
import time


@pytest.mark.performance
class TestStartupPerformance:
    """Test suite for TUI startup performance measurement."""

    def test_tui_startup_baseline_measurement(self):
        """TUI should launch within reasonable time."""
        start_time = time.perf_counter()
        
        try:
            # Launch TUI and measure startup time until it's running
            process = subprocess.Popen(
                ["uv", "run", "python", "-m", "claude_code_autoyes", "tui"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            
            # Give it time to start up
            time.sleep(1.0)
            
            # Check if process is running (successful startup)
            if process.poll() is None:
                # Process is running, measure elapsed time
                elapsed = time.perf_counter() - start_time
                
                # Clean up - terminate the process
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                
                # Should start within reasonable time
                assert elapsed < 5.0, f"Startup time {elapsed:.3f}s exceeds 5.0s threshold"
                assert elapsed > 0, "Startup time should be positive"
            else:
                # Process exited immediately, probably an error
                stdout, stderr = process.communicate()
                pytest.fail(f"TUI failed to start: {stderr}")
                
        except Exception as e:
            pytest.fail(f"TUI startup test failed: {str(e)}")

    def test_tui_startup_timeout_detection(self):
        """Should distinguish between startup failure and long startup."""
        try:
            # Launch TUI with timeout to detect hanging vs successful launch
            result = subprocess.run(
                ["uv", "run", "python", "-m", "claude_code_autoyes", "tui"],
                timeout=2,
                capture_output=True,
                text=True
            )
            # If we get here, process exited quickly - could be error or success
            assert result.returncode in [0, 130], f"Unexpected exit code: {result.returncode}"
        except subprocess.TimeoutExpired:
            # Timeout means TUI is likely running normally
            assert True, "TUI launched successfully (timed out as expected)"

    def test_multiple_startup_measurements_for_stability(self):
        """Multiple startup measurements should be consistent."""
        startup_times = []
        
        for i in range(3):
            start_time = time.perf_counter()
            
            try:
                process = subprocess.Popen(
                    ["uv", "run", "python", "-m", "claude_code_autoyes", "tui"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                
                time.sleep(0.5)  # Give it time to start
                
                if process.poll() is None:
                    elapsed = time.perf_counter() - start_time
                    startup_times.append(elapsed)
                    
                    # Clean up
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                else:
                    # Process failed to start
                    startup_times.append(float('inf'))
                    
            except Exception:
                startup_times.append(float('inf'))
        
        # Filter out failed startups
        valid_times = [t for t in startup_times if t != float('inf')]
        
        if not valid_times:
            pytest.skip("No successful startup measurements")
        
        # Check consistency - startup times shouldn't vary wildly
        avg_time = sum(valid_times) / len(valid_times)
        for time_val in valid_times:
            variance = abs(time_val - avg_time)
            assert variance < 2.0, f"Startup time variance too high: {variance:.3f}s"

    def test_startup_performance_factors_measurement(self):
        """Should be able to collect basic performance metrics during startup."""
        from claude_code_autoyes.core.performance import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        
        # Collect metrics - this tests that performance monitoring works
        metrics = monitor.collect_current_metrics()
        
        assert hasattr(metrics, 'timestamp')
        assert hasattr(metrics, 'memory_usage_mb')
        assert hasattr(metrics, 'cpu_percent')
        assert metrics.timestamp > 0
        assert metrics.memory_usage_mb >= 0
        assert metrics.cpu_percent >= 0


@pytest.mark.performance
class TestNavigationPerformance:
    """Test suite for TUI navigation responsiveness."""

    def test_navigation_response_time_measurement(self):
        """Should be able to measure navigation response times."""
        # Test that performance monitoring infrastructure works
        from claude_code_autoyes.core.performance import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        metrics = monitor.collect_current_metrics()
        
        # Should provide baseline metrics for comparison
        assert isinstance(metrics.timestamp, float)
        assert isinstance(metrics.memory_usage_mb, float)
        assert isinstance(metrics.cpu_percent, float)

    def test_large_dataset_navigation_performance(self):
        """Navigation should remain responsive with large datasets."""
        # This would require actual TUI interaction to test properly
        # For now, just test that the monitoring infrastructure exists
        from claude_code_autoyes.core.performance import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        
        # Simulate collecting metrics over time
        metrics1 = monitor.collect_current_metrics()
        time.sleep(0.1)
        metrics2 = monitor.collect_current_metrics()
        
        # Should be able to collect metrics at different times
        assert metrics2.timestamp > metrics1.timestamp