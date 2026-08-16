#!/usr/bin/env python3
"""
FileFlux entry point.
Launches CLI if arguments are provided, otherwise opens the GUI.
"""
import sys


def main():
    if len(sys.argv) > 1:
        from app.cli import run_cli
        run_cli()
    else:
        from app.gui.app import launch
        launch()


if __name__ == "__main__":
    main()
