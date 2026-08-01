"""
Directory scanning engine for the Smart File Organizer.

Discovers files in a directory (optionally recursive), extracts metadata
for each one, and returns structured FileInfo objects. Does not move,
rename, or modify any files — this module only reads and reports.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.models import FileInfo
from app.exceptions import ScanError
from app.utils import is_hidden
from app.logger import setup_logger
from dataclasses import dataclass

logger = setup_logger()


def get_file_info(file_path: Path) -> FileInfo:
    """
    Extract metadata for a single file and return it as a FileInfo object.

    Args:
        file_path: Path to the file to inspect.

    Returns:
        A FileInfo object containing the file's metadata.

    Raises:
        ScanError: If the file's metadata can't be read (e.g. permission denied).
    """
    try:
        stat = file_path.stat()
        return FileInfo(
            name=file_path.name,
            extension=file_path.suffix.lower(),
            path=file_path,
            parent_directory=file_path.parent,
            size=stat.st_size,
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            is_hidden=is_hidden(file_path),
        )
    except (PermissionError, OSError) as e:
        raise ScanError(f"Could not read metadata for {file_path}: {e}")
    
def scan_directory(directory: Path, recursive: bool = False) -> List[FileInfo]:
    """
    Scan a directory for files and return their metadata.

    Args:
        directory: Path to the directory to scan.
        recursive: If True, scan subdirectories too. If False, scan only
            the top-level directory.

    Returns:
        A list of FileInfo objects for every non-hidden file found,
        excluding files inside hidden directories (e.g. .venv, .git).

    Raises:
        ScanError: If the directory doesn't exist or isn't a directory.
    """
    if not directory.exists():
        raise ScanError(f"Directory does not exist: {directory}")
    if not directory.is_dir():
        raise ScanError(f"Path is not a directory: {directory}")

    logger.info(f"Scanning directory: {directory}")

    entries = directory.rglob("*") if recursive else directory.iterdir()
    results: List[FileInfo] = []

    for entry in entries:
        if entry.is_dir():
            continue

        if is_hidden(entry) or _has_hidden_parent(entry, directory):
            logger.debug(f"Skipping hidden file: {entry}")
            continue

        try:
            file_info = get_file_info(entry)
            results.append(file_info)
            logger.debug(f"Found file: {entry}")
        except ScanError as e:
            logger.warning(f"Permission denied or read error: {e}")
            continue

    logger.info(f"Scan completed. Total files: {len(results)}")
    return results


def _has_hidden_parent(entry: Path, root: Path) -> bool:
    """
    Check whether any parent folder of entry (up to root) is hidden.

    Args:
        entry: The file being checked.
        root: The top-level directory the scan started from — stops
            checking once we reach this level, so parent folders outside
            the scan itself don't cause false positives.

    Returns:
        True if any directory between entry and root starts with a dot.
    """
    for parent in entry.relative_to(root).parents:
        if str(parent) != "." and parent.name.startswith("."):
            return True
    return False

@dataclass
@dataclass
class ScanStatistics:
    """
    Summary statistics for a completed directory scan.

    Attributes:
        total_files: Number of files found.
        total_size: Combined size of all files, in bytes.
        largest_file: The FileInfo of the largest file found, or None if empty.
        smallest_file: The FileInfo of the smallest file found, or None if empty.
        average_size: Average file size in bytes, or 0.0 if empty.
    """
    total_files: int
    total_size: int
    largest_file: Optional[FileInfo]
    smallest_file: Optional[FileInfo]
    average_size: float


def collect_statistics(files: List[FileInfo]) -> ScanStatistics:
    """
    Compute summary statistics from a list of scanned files.

    Args:
        files: List of FileInfo objects, typically from scan_directory().

    Returns:
        A ScanStatistics object summarizing the scan.
    """
    if not files:
        return ScanStatistics(
            total_files=0,
            total_size=0,
            largest_file=None,
            smallest_file=None,
            average_size=0.0,
        )

    total_size = sum(f.size for f in files)
    largest = max(files, key=lambda f: f.size)
    smallest = min(files, key=lambda f: f.size)

    return ScanStatistics(
        total_files=len(files),
        total_size=total_size,
        largest_file=largest,
        smallest_file=smallest,
        average_size=total_size / len(files),
    )
    
def scan(directory: Path, recursive: bool = False) -> tuple[List[FileInfo], ScanStatistics]:
    """
    Perform a full scan of a directory and return both the file list and statistics.

    This is the main entry point for the scanner module — combines
    scan_directory() and collect_statistics() into a single call.

    Args:
        directory: Path to the directory to scan.
        recursive: If True, scan subdirectories too.

    Returns:
        A tuple of (list of FileInfo objects, ScanStatistics summary).

    Raises:
        ScanError: If the directory doesn't exist or isn't a directory.
    """
    files = scan_directory(directory, recursive=recursive)
    stats = collect_statistics(files)
    return files, stats