"""
Reusable utility/helper functions for the Smart File Organizer.

These functions have no dependency on the rest of the app's logic —
they're pure, general-purpose helpers reused across multiple modules.
"""

import shutil
from datetime import datetime
from pathlib import Path


def format_size(size_in_bytes: int) -> str:
    """
    Convert a file size in bytes into a human-readable string.

    Args:
        size_in_bytes: Size of the file in bytes.

    Returns:
        A formatted string such as "2.5 MB".
    """
    size = float(size_in_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def get_file_extension(file_path: Path) -> str:
    """
    Extract the lowercase file extension from a path, including the dot.

    Args:
        file_path: Path to the file.

    Returns:
        The extension (e.g. ".pdf"), or an empty string if there is none.
    """
    return file_path.suffix.lower()


def create_directory(dir_path: Path) -> None:
    """
    Create a directory if it doesn't already exist.

    Args:
        dir_path: Path to the directory to create.
    """
    dir_path.mkdir(parents=True, exist_ok=True)


def is_hidden(file_path: Path) -> bool:
    """
    Check whether a file or folder is hidden (starts with a dot).

    Args:
        file_path: Path to check.

    Returns:
        True if the file/folder name starts with a dot.
    """
    return file_path.name.startswith(".")


def safe_move(source: Path, destination: Path) -> Path:
    """
    Move a file to a destination, renaming it if a file already exists there.

    Args:
        source: Path to the file being moved.
        destination: Target path to move the file to.

    Returns:
        The actual path the file was moved to (may differ from destination
        if a naming conflict was resolved).
    """
    if destination.exists():
        counter = 1
        stem = destination.stem
        suffix = destination.suffix
        parent = destination.parent
        while destination.exists():
            destination = parent / f"{stem} ({counter}){suffix}"
            counter += 1

    shutil.move(str(source), str(destination))
    return destination


def current_timestamp() -> str:
    """
    Get the current timestamp as a formatted string.

    Returns:
        A string like "2026-07-26 15:55:20".
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")