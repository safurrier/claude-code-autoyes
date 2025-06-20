"""Unit tests for data models."""

import pytest


@pytest.mark.unit
def test_claude_instance_creation():
    """Test ClaudeInstance model creation and attributes."""
    from claude_code_autoyes.core.models import ClaudeInstance
    
    instance = ClaudeInstance(
        session="main",
        pane="0", 
        is_claude=True,
        last_prompt="2024-01-01 12:00:00",
        enabled=True
    )
    
    assert instance.session == "main"
    assert instance.pane == "0"
    assert instance.is_claude is True
    assert instance.last_prompt == "2024-01-01 12:00:00"
    assert instance.enabled is True


@pytest.mark.unit
def test_claude_instance_defaults():
    """Test ClaudeInstance default values."""
    from claude_code_autoyes.core.models import ClaudeInstance
    
    instance = ClaudeInstance("session", "1", False)
    
    assert instance.last_prompt is None
    assert instance.enabled is False


@pytest.mark.unit
def test_claude_instance_equality():
    """Test ClaudeInstance equality comparison."""
    from claude_code_autoyes.core.models import ClaudeInstance
    
    instance1 = ClaudeInstance("session", "0", True)
    instance2 = ClaudeInstance("session", "0", True)
    instance3 = ClaudeInstance("session", "1", True)
    
    assert instance1 == instance2
    assert instance1 != instance3