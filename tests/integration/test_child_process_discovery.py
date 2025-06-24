"""Integration tests for child process discovery functionality.

These tests are valuable because they:

1. **Test component interaction**: Verify how find_child_processes() integrates 
   with is_claude_process() without relying on real system processes
   
2. **Test complex logic paths**: The combination of subprocess calls, 
   text parsing, and process tree traversal has many edge cases
   
3. **Provide predictable test scenarios**: Mock specific process trees 
   to test detection logic that would be flaky with real processes
   
4. **Validate parsing logic**: Ensure ps command output parsing works 
   correctly with various formats and edge cases
   
5. **Catch integration bugs**: Issues that unit tests (testing methods 
   in isolation) might miss, like incorrect data flow between methods

The mocking is necessary because real process discovery would be:
- Flaky (processes come and go)
- Environment-dependent (different processes on different machines)
- Slow (actual subprocess calls)
- Non-deterministic (can't control what processes exist)

These tests complement:
- Unit tests (individual method behavior)
- E2E tests (real Claude detection in tmux)
"""

import subprocess
from unittest.mock import Mock, patch

import pytest

from claude_code_autoyes.core.detector import ClaudeDetector


class TestChildProcessDiscovery:
    """Test child process discovery for enhanced Claude detection."""

    @pytest.fixture
    def detector(self):
        """Create ClaudeDetector instance for testing."""
        return ClaudeDetector()

    @pytest.fixture
    def mock_ps_output_with_claude_child(self):
        """Mock ps command output showing Claude as child process."""
        return """  PID  PPID COMMAND
 1234     1 systemd
 5486 30843 -zsh
 6117  5486 claude
 7890  6117 node /some/path
 9999     1 other_process"""

    @pytest.fixture  
    def mock_ps_output_no_claude(self):
        """Mock ps command output with no Claude processes."""
        return """  PID  PPID COMMAND
 1234     1 systemd
 5486 30843 -zsh
 7890  5486 node /some/app
 9999     1 other_process"""

    def test_find_child_processes_discovers_claude(self, detector, mock_ps_output_with_claude_child):
        """Test that find_child_processes discovers Claude child process."""
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = mock_ps_output_with_claude_child
            mock_run.return_value = mock_result
            
            # This method doesn't exist yet - will FAIL initially
            children = detector.find_child_processes("5486")
            
            # Should find Claude child process
            claude_children = [child for child in children if child["command"] == "claude"]
            assert len(claude_children) == 1
            assert claude_children[0]["pid"] == "6117"
            assert claude_children[0]["ppid"] == "5486"

    def test_find_child_processes_handles_no_children(self, detector, mock_ps_output_no_claude):
        """Test that find_child_processes handles case with no Claude children."""
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = mock_ps_output_no_claude
            mock_run.return_value = mock_result
            
            # This method doesn't exist yet - will FAIL initially
            children = detector.find_child_processes("5486")
            
            # Should find no Claude children
            claude_children = [child for child in children if child["command"] == "claude"]
            assert len(claude_children) == 0

    def test_find_child_processes_handles_subprocess_error(self, detector):
        """Test that find_child_processes handles subprocess errors gracefully."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.SubprocessError("ps command failed")
            
            # This method doesn't exist yet - will FAIL initially
            children = detector.find_child_processes("5486")
            
            # Should return empty list on error
            assert children == []

    def test_enhanced_is_claude_process_checks_children(self, detector, mock_ps_output_with_claude_child):
        """Test that enhanced is_claude_process checks child processes."""
        # Mock the child process discovery
        with patch.object(detector, 'find_child_processes') as mock_find_children:
            mock_find_children.return_value = [
                {"pid": "6117", "ppid": "5486", "command": "claude"}
            ]
            
            # Process info for shell (what tmux reports)
            process_info = {"command": "node", "pid": "5486"}
            
            # Enhanced detection should find Claude in children
            # This will FAIL initially - current logic doesn't check children
            is_claude = detector.is_claude_process(process_info)
            
            assert is_claude is True
            mock_find_children.assert_called_once_with("5486")

    def test_enhanced_is_claude_process_direct_claude(self, detector):
        """Test that direct Claude process is still detected (backward compatibility)."""
        process_info = {"command": "claude", "pid": "1234"}
        
        # Direct Claude should still work
        is_claude = detector.is_claude_process(process_info)
        assert is_claude is True

    def test_enhanced_is_claude_process_node_with_claude_args(self, detector):
        """Test that node process with Claude in args is detected."""
        with patch('subprocess.run') as mock_run:
            # Mock ps command to return Claude path in node args
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "node /usr/local/bin/claude"
            mock_run.return_value = mock_result
            
            process_info = {"command": "node", "pid": "1234"}
            
            # Should detect node process running Claude
            is_claude = detector.is_claude_process(process_info)
            assert is_claude is True

    @pytest.mark.integration
    def test_integration_with_real_process_tree(self, detector):
        """Integration test using real process information."""
        # Get current process tree
        try:
            result = subprocess.run(
                ["ps", "-eo", "pid,ppid,command"],
                capture_output=True,
                text=True,
                check=True,
            )
            
            # Find a shell process to test with
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            shell_processes = []
            
            for line in lines:
                parts = line.strip().split(None, 2)
                if len(parts) >= 3 and ('zsh' in parts[2] or 'bash' in parts[2]):
                    shell_processes.append({
                        "pid": parts[0],
                        "ppid": parts[1], 
                        "command": parts[2].split()[0]  # Just command name
                    })
            
            if shell_processes:
                # Test child discovery with real shell process
                shell_pid = shell_processes[0]["pid"]
                children = detector.find_child_processes(shell_pid)
                
                # Should return list (may be empty, but should not error)
                assert isinstance(children, list)
                
                # Each child should have expected structure
                for child in children:
                    assert "pid" in child
                    assert "ppid" in child
                    assert "command" in child
                    assert child["ppid"] == shell_pid
            
        except subprocess.SubprocessError:
            pytest.skip("Could not run ps command for integration test")

    def test_child_process_discovery_command_format(self, detector):
        """Test that ps command is formatted correctly for child discovery."""
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "1234 5486 test_command"
            mock_run.return_value = mock_result
            
            # This will FAIL initially - method doesn't exist
            detector.find_child_processes("5486")
            
            # Verify ps command is called with correct format
            expected_cmd = ["ps", "-eo", "pid,ppid,command"]
            mock_run.assert_called_once_with(
                expected_cmd,
                capture_output=True,
                text=True,
                check=False,
            )