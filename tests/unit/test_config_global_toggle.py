"""Unit tests for ConfigManager global auto-yes toggle functionality."""

import os
import tempfile
import pytest

from claude_code_autoyes.core.config import ConfigManager


@pytest.mark.unit
def test_config_has_global_auto_yes_toggle():
    """ConfigManager supports global auto_yes_enabled boolean."""
    config = ConfigManager()
    assert hasattr(config, 'auto_yes_enabled')
    assert isinstance(config.auto_yes_enabled, bool)


@pytest.mark.unit
def test_config_toggle_auto_yes_persists():
    """Global toggle state persists to file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_config_file = f.name
    
    try:
        # First config: set to False and save
        config1 = ConfigManager(config_file=temp_config_file)
        config1.auto_yes_enabled = False
        config1.save()
        
        # Second config: load and verify
        config2 = ConfigManager(config_file=temp_config_file)
        assert config2.auto_yes_enabled is False
    finally:
        if os.path.exists(temp_config_file):
            os.unlink(temp_config_file)