"""
Data models for the Smart File Organizer.

Uses dataclasses instead of raw dictionaries to represent scanned file
data — this gives type safety, autocomplete support, and a single
source of truth for what a "file record" contains.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class FileInfo:
    """
    Represents metadata for a single scanned file.

    Attributes:
        name: The filename including extension (e.g. "report.pdf").
        extension: The lowercase file extension including the dot (e.g. ".pdf").
        path: Full path to the file.
        parent_directory: The directory containing this file.
        size: File size in bytes.
        created_time: When the file was created.
        modified_time: When the file was last modified.
        is_hidden: Whether the file is a hidden file (starts with a dot).
    """
    name: str
    extension: str
    path: Path
    parent_directory: Path
    size: int
    created_time: datetime
    modified_time: datetime
    is_hidden: bool