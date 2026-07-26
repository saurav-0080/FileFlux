"""
Application-wide constant values.

Centralizing these avoids "magic strings" scattered across the codebase —
if a folder name or filename ever needs to change, it changes here once.
"""

# App metadata
APP_NAME: str = "Smart File Organizer"
APP_VERSION: str = "0.1.0"

# Config paths
CONFIG_DIR: str = "config"
SETTINGS_FILE: str = "settings.json"
RULES_FILE: str = "rules.json"

# Logging
LOG_DIR: str = "logs"
LOG_FILE: str = "organizer.log"

# Database
DATABASE_DIR: str = "database"
DATABASE_FILE: str = "organizer.db"

# Default fallback category for unrecognized file extensions
DEFAULT_CATEGORY: str = "Others"