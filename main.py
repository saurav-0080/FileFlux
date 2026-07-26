"""
Entry point for the Smart File Organizer.

Loads configuration, initializes logging, and starts the application.
No file scanning or organizing happens yet — this just verifies the
foundation (config + logging) works end to end.
"""

from app.config import load_settings, load_rules
from app.logger import setup_logger
from app.exceptions import ConfigurationError
from app.constants import APP_NAME, APP_VERSION


def main() -> None:
    """Start the Smart File Organizer application."""
    logger = setup_logger()

    logger.info(f"{APP_NAME} v{APP_VERSION} starting up")

    try:
        settings = load_settings()
        rules = load_rules()
    except ConfigurationError as e:
        logger.error(f"Failed to load configuration: {e}")
        return

    logger.info(f"Loaded {len(rules)} category rules")
    logger.info("Startup complete")


if __name__ == "__main__":
    main()