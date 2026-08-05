"""
Entry point for the Smart File Organizer.

Loads configuration, initializes logging, prompts the user for a folder
to scan, runs the scanner, and prints the results. No file organizing
happens yet — this is discovery and reporting only.
"""

from pathlib import Path

from app.config import load_settings, load_rules
from app.logger import setup_logger
from app.exceptions import ConfigurationError, ScanError
from app.constants import APP_NAME, APP_VERSION
from app.scanner import scan
from app.utils import format_size
import time
from app.organizer import Organizer


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

    try:
        folder_input = input("Enter the folder path to scan: ").strip()
    except KeyboardInterrupt:
        logger.info("Scan cancelled by user")
        print("\nCancelled.")
        return

    if not folder_input:
        logger.error("No folder path provided")
        print("No folder path entered. Exiting.")
        return

    target_directory = Path(folder_input).expanduser()
    recursive = settings.get("recursive_scan", False)

    try:
        files, stats = scan(target_directory, recursive=recursive)
    except ScanError as e:
        logger.error(f"Scan failed: {e}")
        print(f"Error: {e}")
        return

    print(f"\nScanning: {target_directory}")
    print(f"Files Found: {stats.total_files}")
    print(f"Total Size: {format_size(stats.total_size)}")

    if stats.largest_file:
        print(f"\nLargest File:\n{stats.largest_file.name} ({format_size(stats.largest_file.size)})")
    if stats.smallest_file:
        print(f"\nSmallest File:\n{stats.smallest_file.name} ({format_size(stats.smallest_file.size)})")

    print(f"\nAverage File Size: {format_size(stats.average_size)}")
    logger.info("Startup complete")
    
    try:
        confirm = input("\nOrganize these files? (y/n): ").strip().lower()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return

    if confirm != "y":
        print("Exiting without organizing.")
        return
    start_time = time.time()
    org = Organizer(target_directory, rules)
    org.organize(files)
    elapsed = time.time() - start_time

    summary = org.create_summary(files, elapsed)

    print(f"\nFiles Scanned  : {summary['files_scanned']}")
    print(f"Files Moved    : {summary['files_moved']}")
    print(f"Skipped        : {summary['skipped']}")
    print(f"Errors         : {summary['errors']}")
    print(f"Folders Created: {summary['folders_created']}")
    print(f"Time Taken     : {summary['time_taken']} sec")


if __name__ == "__main__":
    main()