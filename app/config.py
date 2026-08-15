"""
Configuration loader for the Smart File Organizer.

Handles reading settings.json and rules.json from the config/ directory,
with validation and clear error messages if files are missing or malformed.
"""

import json
from pathlib import Path
from typing import Any, Dict

from app.constants import CONFIG_DIR, RULES_FILE, SETTINGS_FILE
from app.exceptions import ConfigurationError
from app.logger import setup_logger


def _load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Load and parse a JSON file, raising a clear error if it fails.

    Args:
        file_path: Path to the JSON file to load.

    Returns:
        The parsed JSON content as a dictionary.

    Raises:
        ConfigurationError: If the file doesn't exist or isn't valid JSON.
    """
    if not file_path.exists():
        raise ConfigurationError(f"Configuration file not found: {file_path}")

    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON in {file_path}: {e}")


def load_settings() -> Dict[str, Any]:
    """
    Load settings.json from the config directory.

    Returns:
        Dictionary of application settings.
    """
    path = Path(CONFIG_DIR) / SETTINGS_FILE
    return _load_json_file(path)


def load_rules() -> Dict[str, Any]:
    """
    Load rules.json from the config directory.

    Returns:
        Dictionary mapping category names to lists of file extensions.
    """
    path = Path(CONFIG_DIR) / RULES_FILE
    return _load_json_file(path)


def get_setting(settings: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely retrieve a single setting value, with an optional fallback.

    Args:
        settings: The settings dictionary (from load_settings()).
        key: The setting key to look up.
        default: Value to return if the key doesn't exist.

    Returns:
        The setting value, or the default if not found.
    """
    return settings.get(key, default)


VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def validate_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate settings values and return sanitized settings.
    Raises ConfigurationError on invalid values.
    """
    log_level = settings.get("log_level", "INFO")
    if log_level not in VALID_LOG_LEVELS:
        raise ConfigurationError(
            f"Invalid log_level '{log_level}'. Must be one of: {', '.join(VALID_LOG_LEVELS)}"
        )

    if "max_file_size_mb" in settings:
        val = settings["max_file_size_mb"]
        if not isinstance(val, (int, float)) or val <= 0:
            raise ConfigurationError(
                f"Invalid max_file_size_mb '{val}'. Must be a positive number."
            )

    return settings


def load_settings_safe() -> Dict[str, Any]:
    """
    Load and validate settings, falling back to defaults on failure.
    Never crashes the application.
    """
    defaults = {
        "recursive": False,
        "detect_duplicates": True,
        "log_level": "INFO",
    }
    try:
        settings = load_settings()
        return validate_settings(settings)
    except ConfigurationError as e:
        logger = setup_logger("config")
        logger.warning(f"Configuration error: {e}. Using defaults.")
        return defaults
