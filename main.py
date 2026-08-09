"""
Entry point for FileFlux.

Supports both CLI and GUI modes.
"""

import sys


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "gui":
        from app.gui.app import launch
        launch()
    else:
        from app.cli import run_cli
        sys.exit(run_cli())