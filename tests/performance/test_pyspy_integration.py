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
        # This test should FAIL initially - PySpy class doesn't exist yet
        try:
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
        except ImportError:
            pytest.fail("PySpy module should exist")

    def test_pyspy_installation_guidance(self):
        """Should provide clear installation instructions."""
        # This test should FAIL initially - installation guidance doesn't exist yet
        try:
            from claude_code_autoyes.core.performance import PySpy
            pyspy = PySpy()
            
            guidance = pyspy.get_installation_guidance()
            
            assert "py-spy" in guidance.lower()
            assert "install" in guidance.lower()
            
            # Should provide multiple installation options
            assert ("pip install" in guidance or 
                    "cargo install" in guidance or 
                    "package manager" in guidance)
        except ImportError:
            pytest.fail("PySpy module should exist")

    def test_profile_tui_process(self):
        """Should profile running TUI process with py-spy."""
        # This test should FAIL initially - profiling functionality doesn't exist yet
        try:
            from claude_code_autoyes.core.performance import PySpy
            pyspy = PySpy()
            
            # Skip if py-spy not available (don't fail test)
            if not pyspy.is_available():
                pytest.skip("py-spy not available for testing")
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                output_file = os.path.join(tmp_dir, "profile.svg")
                
                # Should be able to profile by process name
                result = pyspy.profile_process(
                    process_name="claude-code-autoyes",
                    duration=5,
                    output_file=output_file
                )
                
                # If no process is running, that's expected in test environment
                if "No process found with name" in result.error:
                    pytest.skip("No claude-code-autoyes process running for profiling test")
                
                # If py-spy requires sudo (macOS), skip the test
                if "requires root" in result.error:
                    pytest.skip("py-spy requires sudo on macOS")
                
                assert result.success, f"Profiling failed: {result.error}"
                assert os.path.exists(output_file), "Profile output should be created"
        except ImportError:
            pytest.fail("PySpy module should exist")

    def test_flame_graph_generation(self):
        """Should generate flame graphs from profiling data."""
        # This test should FAIL initially - flame graph generation doesn't exist yet
        try:
            from claude_code_autoyes.core.performance import PySpy
            pyspy = PySpy()
            
            if not pyspy.is_available():
                pytest.skip("py-spy not available for testing")
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                profile_file = os.path.join(tmp_dir, "profile.svg")
                
                # Mock a running process for testing
                mock_result = pyspy.profile_process(
                    process_name="python",  # Use python process for testing
                    duration=2,  # Short duration for testing
                    output_file=profile_file,
                    format="svg"
                )
                
                if mock_result.success:
                    assert os.path.exists(profile_file)
                    # Basic validation that it's an SVG file
                    with open(profile_file, 'r') as f:
                        content = f.read()
                        assert "<svg" in content.lower()
        except ImportError:
            pytest.fail("PySpy module should exist")

    def test_profiling_with_graceful_fallback(self):
        """Should handle py-spy not being available gracefully."""
        # This test should FAIL initially - graceful fallback doesn't exist yet  
        try:
            from claude_code_autoyes.core.performance import PySpy
            pyspy = PySpy()
            
            # Force unavailable state for testing
            with patch.object(pyspy, 'is_available', return_value=False):
                result = pyspy.profile_process(
                    process_name="any-process",
                    duration=5,
                    output_file="/tmp/test.svg"
                )
                
                # Should fail gracefully with helpful message
                assert not result.success
                assert "py-spy not available" in result.error.lower()
                assert "install" in result.error.lower()
        except ImportError:
            pytest.fail("PySpy module should exist")

    def test_profile_command_validation(self):
        """Should validate profiling command parameters."""
        # This test should FAIL initially - parameter validation doesn't exist yet
        try:
            from claude_code_autoyes.core.performance import PySpy
            pyspy = PySpy()
            
            # Test invalid duration
            result = pyspy.profile_process(
                process_name="test",
                duration=-1,  # Invalid negative duration
                output_file="/tmp/test.svg"
            )
            assert not result.success
            assert "duration" in result.error.lower()
            
            # Test invalid output path
            result = pyspy.profile_process(
                process_name="test", 
                duration=5,
                output_file="/invalid/path/test.svg"  # Invalid path
            )
            assert not result.success
            assert ("path" in result.error.lower() or 
                    "directory" in result.error.lower() or
                    "permission" in result.error.lower())
        except ImportError:
            pytest.fail("PySpy module should exist")

    def test_process_discovery_for_tui(self):
        """Should find running TUI processes for profiling."""
        # This test should FAIL initially - process discovery doesn't exist yet
        try:
            from claude_code_autoyes.core.performance import PySpy
            pyspy = PySpy()
            
            running_processes = pyspy.find_tui_processes()
            
            # Should return list of process info
            assert isinstance(running_processes, list)
            
            # Each process should have required info
            for process in running_processes:
                assert hasattr(process, 'pid'), "Process should have PID"
                assert hasattr(process, 'name'), "Process should have name"
                assert hasattr(process, 'cmdline'), "Process should have command line"
                assert process.pid > 0, "PID should be positive"
        except ImportError:
            pytest.fail("PySpy module should exist")


@pytest.mark.performance
class TestProfilingWorkflow:
    """Test suite for complete profiling workflow."""

    def test_end_to_end_profiling_workflow(self):
        """Should support complete profiling workflow from discovery to analysis."""
        # This test should FAIL initially - complete workflow doesn't exist yet
        from claude_code_autoyes.commands.debug import ProfileWorkflow
        
        workflow = ProfileWorkflow()
        
        # Step 1: Discover processes
        processes = workflow.discover_tui_processes()
        
        # Step 2: Start profiling (if processes found)
        if processes:
            profile_session = workflow.start_profiling(
                process=processes[0],
                duration=5
            )
            assert profile_session.is_active(), "Profiling session should be active"
            
            # Step 3: Generate report
            report = workflow.generate_profile_report(profile_session)
            assert report.flame_graph_path is not None
            assert os.path.exists(report.flame_graph_path)
            
            # Step 4: Analyze results
            analysis = workflow.analyze_profile(report)
            assert hasattr(analysis, 'bottlenecks'), "Analysis should identify bottlenecks"
            assert hasattr(analysis, 'recommendations'), "Analysis should provide recommendations"

    def test_profiling_output_formats(self):
        """Should support multiple profiling output formats."""
        # This test should FAIL initially - format support doesn't exist yet
        try:
            from claude_code_autoyes.core.performance import PySpy
            pyspy = PySpy()
            
            if not pyspy.is_available():
                pytest.skip("py-spy not available for testing")
            
            formats_to_test = ['svg', 'raw', 'speedscope']
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                for output_format in formats_to_test:
                    output_file = os.path.join(tmp_dir, f"profile.{output_format}")
                    
                    result = pyspy.profile_process(
                        process_name="python",
                        duration=1,  # Very short for testing
                        output_file=output_file,
                        format=output_format
                    )
                    
                    if result.success:  # Only check if profiling succeeded
                        assert os.path.exists(output_file), f"Output file should exist for format {output_format}"
        except ImportError:
            pytest.fail("PySpy module should exist")