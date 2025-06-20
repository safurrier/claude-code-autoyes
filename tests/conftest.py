"""Shared test fixtures and configuration."""

import pytest
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Iterator


@pytest.fixture
def temp_home_dir() -> Iterator[Path]:
    """Provide isolated temporary home directory for config files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        home_path = Path(temp_dir)
        yield home_path


@pytest.fixture
def uv_script_path() -> Path:
    """Path to the original UV script."""
    return Path(__file__).parent.parent / "claude_code_autoyes.py"


@pytest.fixture
def project_root() -> Path:
    """Path to project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def isolated_tmux_server():
    """Create isolated tmux server for testing."""
    # Create unique socket name for test isolation
    import uuid
    socket_name = f"test_claude_autoyes_{uuid.uuid4().hex[:8]}"
    
    # Start test tmux server
    subprocess.run(
        ["tmux", "-S", f"/tmp/{socket_name}", "new-session", "-d", "-s", "test_session"],
        check=False
    )
    
    yield socket_name
    
    # Cleanup: kill test tmux server
    subprocess.run(
        ["tmux", "-S", f"/tmp/{socket_name}", "kill-server"],
        check=False
    )


@pytest.fixture
def fake_claude_pane(isolated_tmux_server):
    """Create tmux pane with fake Claude process for testing."""
    socket_name = isolated_tmux_server
    
    # Create a pane and run a fake process that looks like Claude
    subprocess.run([
        "tmux", "-S", f"/tmp/{socket_name}", 
        "new-window", "-t", "test_session", 
        "-n", "claude_test",
        "sleep", "300"  # Long-running process to simulate Claude
    ], check=False)
    
    return socket_name


@pytest.fixture
def test_config_file(temp_home_dir) -> Path:
    """Create temporary config file for testing."""
    config_path = temp_home_dir / ".claude-autoyes-config"
    config_content = """{
    "enabled_sessions": [],
    "daemon_enabled": false,
    "refresh_interval": 3
}"""
    config_path.write_text(config_content)
    return config_path