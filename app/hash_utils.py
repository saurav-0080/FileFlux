"""
Hashing utilities for the Smart File Organizer.

Provides SHA-256 and MD5 hash calculation for files.
Files are read in chunks to avoid loading large files into memory.
"""

import hashlib
from pathlib import Path

CHUNK_SIZE = 8192


def calculate_sha256(path: Path) -> str:
    """
    Calculate the SHA-256 hash of a file.

    Args:
        path: Path to the file.

    Returns:
        Hex string of the SHA-256 hash.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read.
    """
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()


def calculate_md5(path: Path) -> str:
    """
    Calculate the MD5 hash of a file.

    Args:
        path: Path to the file.

    Returns:
        Hex string of the MD5 hash.
    """
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_hash(path: Path, hash_value: str) -> bool:
    """
    Verify that a file's SHA-256 hash matches an expected value.

    Args:
        path: Path to the file.
        hash_value: Expected SHA-256 hex string.

    Returns:
        True if the hash matches, False otherwise.
    """
    return calculate_sha256(path) == hash_value