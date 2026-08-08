"""
Command-line interface for FileFlux.

Parses user commands and delegates to the appropriate modules.
No business logic lives here — the CLI only receives input,
validates it, calls the right module, and displays the result.
"""

import sys
import time
import argparse
from pathlib import Path

from app.config import load_settings, load_rules
from app.scanner import scan
from app.organizer import Organizer
from app.duplicate_detector import DuplicateDetector
from app.undo import UndoManager
from app import database, history
from app.utils import format_size
from app.constants import APP_NAME, APP_VERSION
from app.exceptions import ConfigurationError, ScanError
from app.logger import setup_logger

logger = setup_logger()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fileflux",
        description=f"{APP_NAME} — organize your files professionally",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    # scan
    scan_parser = subparsers.add_parser("scan", help="Scan a directory")
    scan_parser.add_argument("path", help="Directory to scan")
    scan_parser.add_argument("--recursive", action="store_true", help="Scan subfolders")

    # organize
    org_parser = subparsers.add_parser("organize", help="Organize files")
    org_parser.add_argument("path", help="Directory to organize")
    org_parser.add_argument("--recursive", action="store_true", help="Scan subfolders")
    org_parser.add_argument("--dry-run", action="store_true", help="Preview without moving files")
    org_parser.add_argument("--verbose", action="store_true", help="Show detailed logs")

    # duplicates
    dup_parser = subparsers.add_parser("duplicates", help="Find duplicate files")
    dup_parser.add_argument("path", help="Directory to check")
    dup_parser.add_argument("--recursive", action="store_true", help="Scan subfolders")

    # undo
    subparsers.add_parser("undo", help="Undo latest organization session")

    # history
    subparsers.add_parser("history", help="View organization history")

    # version
    subparsers.add_parser("version", help="Show application version")

    return parser


def validate_path(path_str: str) -> Path:
    path = Path(path_str).expanduser()
    if not path.exists():
        print(f"Error: The specified directory does not exist.")
        sys.exit(3)
    if not path.is_dir():
        print(f"Error: Please provide a directory, not a file.")
        sys.exit(3)
    return path


def cmd_scan(args) -> int:
    target = validate_path(args.path)
    try:
        files, stats = scan(target, recursive=args.recursive)
    except ScanError as e:
        print(f"Error: {e}")
        return 1

    print(f"\n{APP_NAME}")
    print("─" * 40)
    print(f"\nScanning: {target}")
    print(f"\nFiles Found  : {stats.total_files}")
    print(f"Total Size   : {format_size(stats.total_size)}")
    if stats.largest_file:
        print(f"\nLargest File : {stats.largest_file.name} ({format_size(stats.largest_file.size)})")
    return 0


def cmd_organize(args) -> int:
    target = validate_path(args.path)
    try:
        rules = load_rules()
        files, stats = scan(target, recursive=args.recursive)
    except (ConfigurationError, ScanError) as e:
        print(f"Error: {e}")
        return 1

    detector = DuplicateDetector(files)
    detector.find_duplicates()

    if args.dry_run:
        from app.rule_engine import get_category
        print(f"\nDRY RUN MODE — No files will be moved.\n")
        for f in files:
            category = get_category(f.extension, rules)
            print(f"  {f.name} → {category}/")
        print(f"\n{'─' * 40}")
        print(f"{len(files)} files analyzed. 0 files modified.")
        return 0

    start = time.time()
    org = Organizer(target, rules)
    org.organize(files)
    elapsed = time.time() - start
    summary = org.create_summary(files, elapsed)

    print(f"\n{'─' * 40}")
    print(f"Files Scanned  : {summary['files_scanned']}")
    print(f"Files Moved    : {summary['files_moved']}")
    print(f"Skipped        : {summary['skipped']}")
    print(f"Errors         : {summary['errors']}")
    print(f"Folders Created: {summary['folders_created']}")
    print(f"Time Taken     : {summary['time_taken']} sec")
    return 0


def cmd_duplicates(args) -> int:
    target = validate_path(args.path)
    try:
        files, _ = scan(target, recursive=args.recursive)
    except ScanError as e:
        print(f"Error: {e}")
        return 1

    detector = DuplicateDetector(files)
    detector.find_duplicates()
    report = detector.generate_duplicate_report()
    print(f"\nDuplicate Detection")
    print("─" * 40)
    print(report)
    return 0


def cmd_undo(args) -> int:
    conn = database.connect()
    database.create_tables(conn)
    session_id = history.get_last_session(conn)

    if not session_id:
        print("No organization session found to undo.")
        database.close(conn)
        return 0

    confirm = input(f"\nUndo session {session_id}? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Undo cancelled.")
        database.close(conn)
        return 0

    manager = UndoManager(conn)
    result = manager.undo_last_session()
    print(f"\nUndo Complete")
    print(f"Restored : {result['restored']}")
    print(f"Skipped  : {result['skipped']}")
    print(f"Failed   : {result['failed']}")
    database.close(conn)
    return 0


def cmd_history(args) -> int:
    conn = database.connect()
    database.create_tables(conn)
    stats = history.get_statistics(conn)
    print(f"\nFileFlux History")
    print("─" * 40)
    print(f"Total Moves   : {stats['total_moves']}")
    print(f"Total Errors  : {stats['total_errors']}")
    print(f"Total Sessions: {stats['total_sessions']}")
    database.close(conn)
    return 0


def cmd_version(args) -> int:
    print(f"{APP_NAME} v{APP_VERSION}")
    return 0


COMMANDS = {
    "scan": cmd_scan,
    "organize": cmd_organize,
    "duplicates": cmd_duplicates,
    "undo": cmd_undo,
    "history": cmd_history,
    "version": cmd_version,
}


def run_cli() -> int:
    parser = build_parser()
    args = parser.parse_args()
    handler = COMMANDS.get(args.command)
    if handler:
        return handler(args)
    parser.print_help()
    return 1