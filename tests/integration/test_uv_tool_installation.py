"""Integration tests for uv tool installation."""

import pytest
import subprocess
from pathlib import Path


@pytest.mark.integration
def test_uv_tool_installation_from_local_repo_succeeds(project_root):
    """Test that repository can be installed as uv tool."""
    # First, try to uninstall if already installed
    subprocess.run(
        ["uv", "tool", "uninstall", "claude-code-autoyes"],
        capture_output=True,
        text=True
    )
    
    # Install as uv tool
    install_result = subprocess.run(
        ["uv", "tool", "install", str(project_root)],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    assert install_result.returncode == 0
    # Test behavior: installation succeeds and reports executable installation
    assert ("Installed 1 executable:" in install_result.stderr or 
            "already installed" in install_result.stderr)
    
    try:
        # Test that tool command works
        help_result = subprocess.run(
            ["claude-code-autoyes", "--help"],
            capture_output=True,
            text=True
        )
        
        assert help_result.returncode == 0
        # Test behavior: help command succeeds and produces help output
        assert len(help_result.stdout) > 100  # Substantial help content
        assert "Options:" in help_result.stdout  # Standard Click help format
        
        # Test a specific command
        status_result = subprocess.run(
            ["claude-code-autoyes", "status"],
            capture_output=True,
            text=True
        )
        
        assert status_result.returncode == 0
        # Test behavior: status command succeeds and produces status output
        assert len(status_result.stdout) > 0
        
    finally:
        # Clean up - uninstall the tool
        subprocess.run(
            ["uv", "tool", "uninstall", "claude-code-autoyes"],
            capture_output=True,
            text=True
        )


@pytest.mark.integration 
def test_package_structure_supports_git_url_installation():
    """Test installation from git URL (simulated with local path)."""
    # This would work with: uv tool install git+https://github.com/user/claude-code-autoyes.git
    # For now, just verify the package structure supports it
    
    # Check that pyproject.toml has proper entry points
    project_root = Path(__file__).parent.parent.parent
    pyproject_file = project_root / "pyproject.toml"
    
    assert pyproject_file.exists()
    
    content = pyproject_file.read_text()
    assert "[project.scripts]" in content
    assert "claude-code-autoyes = \"claude_code_autoyes.cli:cli\"" in content