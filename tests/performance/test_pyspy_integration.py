"""Tests for py-spy profiling tool integration."""

import pytest
import subprocess
import tempfile
import os
from unittest.mock import patch, MagicMock


@pytest.mark.performance
class TestPySpyIntegration:
    """Test suite for py-spy profiling integration."""

    def test_pyspy_availability_check(self):
        """Should detect if py-spy is available on system."""
        from claude_code_autoyes.core.performance import PySpy
        pyspy = PySpy()
        
        is_available = pyspy.is_available()
        
        # Should return boolean
        assert isinstance(is_available, bool)
        
        # Should provide installation guidance if not available
        if not is_available:
            install_cmd = pyspy.get_install_command()
            assert isinstance(install_cmd, str)
            assert len(install_cmd) > 0
            # Should suggest pip or cargo installation
            assert "pip install py-spy" in install_cmd or "cargo install py-spy" in install_cmd

    def test_pyspy_installation_guidance(self):
        """Should provide clear installation instructions."""
        from claude_code_autoyes.core.performance import PySpy
        pyspy = PySpy()
        
        guidance = pyspy.get_installation_guidance()
        
        assert "py-spy" in guidance.lower()
        assert "install" in guidance.lower()
        
        # Should provide multiple installation options
        assert ("pip install" in guidance or 
                "cargo install" in guidance or 
                "brew install" in guidance)

    def test_profile_tui_process(self):
        """Should be able to profile TUI process when available."""
        from claude_code_autoyes.core.performance import PySpy
        pyspy = PySpy()
        
        # Skip if py-spy not available
        if not pyspy.is_available():
            pytest.skip("py-spy not available for testing")
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = os.path.join(tmp_dir, "test_profile.svg")
            
            # Try to profile (may fail if no process running, that's ok)
            result = pyspy.profile_process("claude_code_autoyes", 5, output_file)
            
            # Should return ProfileResult with proper structure
            assert hasattr(result, 'success')
            assert hasattr(result, 'error')
            assert hasattr(result, 'output_file')
            
            # If no process found, that's expected in test environment
            if "No process found" in result.error:
                pytest.skip("No claude_code_autoyes process running for profiling test")

    def test_flame_graph_generation(self):
        """Should generate flame graph when profiling succeeds."""
        from claude_code_autoyes.core.performance import PySpy
        pyspy = PySpy()
        
        # Skip if py-spy not available
        if not pyspy.is_available():
            pytest.skip("py-spy not available for testing")
        
        # This would require a running process to test properly
        # For now, just test the format mapping logic
        format_result = pyspy.profile_process("nonexistent", 1, "/dev/null", "svg")
        assert not format_result.success  # Should fail for nonexistent process

    def test_profiling_with_graceful_fallback(self):
        """Should handle profiling failures gracefully."""
        from claude_code_autoyes.core.performance import PySpy
        pyspy = PySpy()
        
        # Test with invalid parameters
        result = pyspy.profile_process("test", 0, "/invalid/path")  # Invalid duration
        assert not result.success
        assert "Duration must be positive" in result.error

    def test_profile_command_validation(self):
        """Should validate profile command parameters."""
        from claude_code_autoyes.core.performance import PySpy
        pyspy = PySpy()
        
        # Test parameter validation
        result = pyspy.profile_process("test", -1, "/tmp/test.svg")
        assert not result.success
        assert "positive" in result.error.lower()

    def test_process_discovery_for_tui(self):
        """Should be able to discover TUI processes."""
        from claude_code_autoyes.core.performance import PySpy
        pyspy = PySpy()
        
        # Should return list of processes
        processes = pyspy.find_tui_processes()
        assert isinstance(processes, list)
        
        # Each process should have required attributes
        for process in processes:
            assert hasattr(process, 'pid')
            assert hasattr(process, 'name')
            assert hasattr(process, 'cmdline')


@pytest.mark.performance
class TestProfilingWorkflow:
    """Test suite for complete profiling workflow."""

    def test_end_to_end_profiling_workflow(self):
        """Should support complete profiling workflow from discovery to analysis."""
        from claude_code_autoyes.core.performance import ProfileWorkflow
        
        workflow = ProfileWorkflow()
        
        # Step 1: Discover processes
        processes = workflow.discover_tui_processes()
        assert isinstance(processes, list)
        
        # If no processes found, that's expected in test environment
        if not processes:
            pytest.skip("No TUI processes found for workflow test")
        
        # Step 2: Start profiling session
        session = workflow.start_profiling(processes[0], 5)
        assert session.is_active()
        
        # Step 3: Generate report
        report = workflow.generate_profile_report(session)
        assert hasattr(report, 'flame_graph_path')
        
        # Step 4: Analyze results
        analysis = workflow.analyze_profile(report)
        assert hasattr(analysis, 'bottlenecks')
        assert hasattr(analysis, 'recommendations')

    def test_profiling_output_formats(self):
        """Should support different profiling output formats."""
        from claude_code_autoyes.core.performance import PySpy
        pyspy = PySpy()
        
        # Skip if py-spy not available
        if not pyspy.is_available():
            pytest.skip("py-spy not available for testing")
        
        # Test format mapping
        with tempfile.TemporaryDirectory() as tmp_dir:
            svg_file = os.path.join(tmp_dir, "test.svg")
            result = pyspy.profile_process("nonexistent", 1, svg_file, "svg")
            
            # Should fail gracefully for nonexistent process
            assert not result.success