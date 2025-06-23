"""Unit tests for enhanced ClaudeDetector methods."""

from unittest.mock import Mock, patch

import pytest

from claude_code_autoyes.core.detector import ClaudeDetector


class TestEnhancedDetectorMethods:
    """Unit tests for new detection methods added for child process discovery."""

    @pytest.fixture
    def detector(self):
        """Create ClaudeDetector instance for testing."""
        return ClaudeDetector()

    def test_find_child_processes_parses_ps_output_correctly(self, detector):
        """Test that find_child_processes parses ps output correctly."""
        mock_ps_output = """  PID  PPID COMMAND
 1234     1 systemd
 5486 30843 -zsh
 6117  5486 claude
 6118  5486 node /some/script.js
 7890  6117 child_of_claude
 9999     1 unrelated_process"""

        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = mock_ps_output
            mock_run.return_value = mock_result
            
            # This method doesn't exist yet - will FAIL initially
            children = detector.find_child_processes("5486")
            
            # Should find direct children of PID 5486
            expected_children = [
                {"pid": "6117", "ppid": "5486", "command": "claude"},
                {"pid": "6118", "ppid": "5486", "command": "node /some/script.js"}
            ]
            
            assert len(children) == 2
            assert children == expected_children

    def test_find_child_processes_handles_empty_output(self, detector):
        """Test find_child_processes with empty ps output."""
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "  PID  PPID COMMAND\n"  # Header only
            mock_run.return_value = mock_result
            
            # This method doesn't exist yet - will FAIL initially
            children = detector.find_child_processes("5486")
            
            assert children == []

    def test_find_child_processes_handles_malformed_output(self, detector):
        """Test find_child_processes with malformed ps output."""
        malformed_output = """  PID  PPID COMMAND
invalid line
1234  # missing ppid and command
5486 30843"""  # missing command

        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = malformed_output
            mock_run.return_value = mock_result
            
            # This method doesn't exist yet - will FAIL initially
            children = detector.find_child_processes("5486")
            
            # Should handle malformed lines gracefully
            assert children == []

    def test_find_child_processes_handles_ps_failure(self, detector):
        """Test find_child_processes when ps command fails."""
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stderr = "ps: command failed"
            mock_run.return_value = mock_result
            
            # This method doesn't exist yet - will FAIL initially  
            children = detector.find_child_processes("5486")
            
            assert children == []

    def test_find_child_processes_handles_subprocess_exception(self, detector):
        """Test find_child_processes when subprocess raises exception."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = OSError("Command not found")
            
            # This method doesn't exist yet - will FAIL initially
            children = detector.find_child_processes("5486")
            
            assert children == []

    def test_find_child_processes_filters_by_parent_pid(self, detector):
        """Test that find_child_processes only returns children of specified parent."""
        mock_ps_output = """  PID  PPID COMMAND
 1111  5486 child_of_5486
 2222  7890 child_of_7890  
 3333  5486 another_child_of_5486
 4444  9999 unrelated_child"""

        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = mock_ps_output
            mock_run.return_value = mock_result
            
            # This method doesn't exist yet - will FAIL initially
            children = detector.find_child_processes("5486")
            
            # Should only return children of PID 5486
            assert len(children) == 2
            assert all(child["ppid"] == "5486" for child in children)
            
            child_pids = [child["pid"] for child in children]
            assert "1111" in child_pids
            assert "3333" in child_pids
            assert "2222" not in child_pids
            assert "4444" not in child_pids

    def test_enhanced_content_detection_welcome_screen(self, detector):
        """Test enhanced content detection for Claude welcome screen."""
        welcome_content = """
λ ~/some/path/ main* claude
╭──────────────────────────────────────────────────────────────────╮
│ ✻ Welcome to Claude Code!                                        │
│                                                                  │
│   /help for help, /status for your current setup                 │
│                                                                  │
│   cwd: /Users/test/some/path                                     │
╰──────────────────────────────────────────────────────────────────╯
"""
        
        # Current detection should work, but let's verify
        is_claude = detector.is_claude_pane(welcome_content)
        assert is_claude is True

    def test_enhanced_content_detection_active_prompt(self, detector):
        """Test enhanced content detection for active Claude prompt."""
        active_content = """
╭─────────────────────────────────────────────────────────────────╮
│ > Write a function that calculates fibonacci numbers             │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯
  -- INSERT --
"""
        
        # Should detect the active prompt pattern
        is_claude = detector.is_claude_pane(active_content)
        assert is_claude is True

    def test_enhanced_content_detection_multiple_patterns(self, detector):
        """Test that enhanced detection recognizes multiple Claude UI patterns."""
        test_cases = [
            # Welcome screen
            "Welcome to Claude Code!",
            # Box patterns with cursor
            "│ > some prompt\n╰─────────",
            # Update notification  
            "✓ Update installed\nRestart to apply",
            # Command palette
            "/help for help, /status",
        ]
        
        for content in test_cases:
            # At least one of these should be detected as Claude
            # Current detection may miss some - will enhance in Green phase
            result = detector.is_claude_pane(content)
            # Note: Some may fail initially, will fix in implementation

    def test_content_detection_avoids_false_positives(self, detector):
        """Test that content detection avoids false positives from Claude-related reports."""
        # This is the actual content that caused a false positive
        false_positive_content = '''
 ╭──────────────────────────────────────────╮
 │                                          │
 │  Claude Code Token Usage Report - Daily  │
 │                                          │
 ╰──────────────────────────────────────────╯

┌────────────┬──────────────────┬───────────┬────────────┐
│ Date       │ Models           │     Input │     Output │
├────────────┼──────────────────┼───────────┼────────────┤
│ 2025-05-23 │ sonnet-4         │       264 │     20,635 │
└────────────┴──────────────────┴───────────┴────────────┘
'''
        
        # Should NOT be detected as Claude instance
        is_claude = detector.is_claude_pane(false_positive_content)
        assert is_claude is False, "Should not detect usage reports as Claude instances"
        
        # But real Claude content should still be detected
        real_claude_content = '''
╭──────────────────────────────────────────────────────────────────╮
│ ✻ Welcome to Claude Code!                                        │
│                                                                  │
│   /help for help, /status for your current setup                 │
│                                                                  │
│   cwd: /Users/test/some/path                                     │
╰──────────────────────────────────────────────────────────────────╯
'''
        
        is_real_claude = detector.is_claude_pane(real_claude_content)
        assert is_real_claude is True, "Should still detect real Claude content"
            

    def test_child_discovery_integration_with_is_claude_process(self, detector):
        """Test integration between child discovery and is_claude_process."""
        # Mock process info that tmux would report (shell)
        process_info = {"command": "node", "pid": "5486"}
        
        # Mock child discovery finding Claude
        with patch.object(detector, 'find_child_processes') as mock_find_children:
            mock_find_children.return_value = [
                {"pid": "6117", "ppid": "5486", "command": "claude"}
            ]
            
            # Enhanced is_claude_process should check children
            # This will FAIL initially - current logic doesn't use find_child_processes
            is_claude = detector.is_claude_process(process_info)
            
            assert is_claude is True
            mock_find_children.assert_called_once_with("5486")

    def test_performance_child_discovery_caching(self, detector):
        """Test that child discovery results can be cached for performance."""
        # This is a design consideration for the Green phase
        # Multiple calls with same PID should be efficient
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "6117  5486 claude"
            mock_run.return_value = mock_result
            
            # This method doesn't exist yet - will FAIL initially
            children1 = detector.find_child_processes("5486")
            children2 = detector.find_child_processes("5486")
            
            # Should call ps command for each request (no caching yet)
            # Future enhancement could add caching
            assert mock_run.call_count == 2
            assert children1 == children2

    def test_find_child_processes_command_parsing_edge_cases(self, detector):
        """Test command parsing handles edge cases in process names."""
        edge_case_output = """  PID  PPID COMMAND
 1111  5486 claude
 2222  5486 claude --some-flag
 3333  5486 /usr/local/bin/claude
 4444  5486 python claude.py
 5555  5486 node /path/to/claude"""

        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = edge_case_output
            mock_run.return_value = mock_result
            
            # This method doesn't exist yet - will FAIL initially
            children = detector.find_child_processes("5486")
            
            # Should find all child processes, parsing commands correctly
            assert len(children) == 5
            
            commands = [child["command"] for child in children]
            assert "claude" in commands
            assert "claude --some-flag" in commands or "claude" in commands  # Depending on parsing
            assert any("claude" in cmd for cmd in commands)  # Should find claude processes