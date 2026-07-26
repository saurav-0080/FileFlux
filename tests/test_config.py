"""Unit tests for app.config"""

import pytest
from pathlib import Path

from app.config import load_settings, load_rules, get_setting, _load_json_file
from app.exceptions import ConfigurationError


def test_load_settings_returns_dict():
    """load_settings() should return a dictionary with expected keys."""
    settings = load_settings()
    assert isinstance(settings, dict)
    assert "recursive_scan" in settings


def test_load_rules_returns_dict():
    """load_rules() should return a dictionary of categories."""
    rules = load_rules()
    assert isinstance(rules, dict)
    assert "Images" in rules


def test_get_setting_returns_value():
    """get_setting() should return the correct value for an existing key."""
    settings = {"recursive_scan": True}
    assert get_setting(settings, "recursive_scan") is True


def test_get_setting_returns_default_when_missing():
    """get_setting() should return the default when the key doesn't exist."""
    settings = {}
    assert get_setting(settings, "nonexistent_key", default="fallback") == "fallback"


def test_missing_config_file_raises_error():
    """Loading a nonexistent JSON file should raise ConfigurationError."""
    with pytest.raises(ConfigurationError):
        _load_json_file(Path("config/does_not_exist.json"))