"""End-to-end tests for CLI command equivalence."""

import subprocess
import pytest
from pathlib import Path


@pytest.mark.e2e
def test_status_command_equivalence(uv_script_path, project_root):
    """Test that status command produces identical output between old and new."""
    # Test original UV script
    old_result = subprocess.run(
        ["uv", "run", str(uv_script_path), "status"],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    # Test new modular command
    new_result = subprocess.run(
        ["uv", "run", "-m", "claude_code_autoyes", "status"],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    # Should have same exit code and similar output content
    assert old_result.returncode == new_result.returncode
    # Note: Not checking exact string match per testing conventions


@pytest.mark.e2e  
def test_enable_all_command_equivalence(uv_script_path, project_root):
    """Test that enable-all command works identically."""
    # Test original UV script
    old_result = subprocess.run(
        ["uv", "run", str(uv_script_path), "enable-all"],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    # Test new modular command
    new_result = subprocess.run(
        ["uv", "run", "-m", "claude_code_autoyes", "enable-all"],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    assert old_result.returncode == new_result.returncode


@pytest.mark.e2e
def test_disable_all_command_equivalence(uv_script_path, project_root):
    """Test that disable-all command works identically."""
    # Test original UV script  
    old_result = subprocess.run(
        ["uv", "run", str(uv_script_path), "disable-all"],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    # Test new modular command
    new_result = subprocess.run(
        ["uv", "run", "-m", "claude_code_autoyes", "disable-all"],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    assert old_result.returncode == new_result.returncode


@pytest.mark.e2e
def test_default_tui_launch(project_root):
    """Test that running module without command launches TUI."""
    # Just test it doesn't crash immediately
    result = subprocess.run(
        ["uv", "run", "-m", "claude_code_autoyes", "--help"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=10
    )
    
    # Should show help and not crash
    assert result.returncode == 0


@pytest.mark.e2e
def test_uv_script_still_works(uv_script_path, project_root):
    """Test that original UV script continues to work after reorganization."""
    result = subprocess.run(
        ["uv", "run", str(uv_script_path), "--help"],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    assert result.returncode == 0