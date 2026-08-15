"""
Filesystem safety and path validation for FileFlux.
"""

from __future__ import annotations

import os
from pathlib import Path

PROTECTED_EXACT: list[str] = [
    "/",
    "/bin",
    "/sbin",
    "/usr",
    "/etc",
    "/System",
    "/Library",
    str(Path.home() / "Library"),
    str(Path(__file__).resolve().parent.parent),
]

PROTECTED_PREFIXES: list[str] = [
    str(Path.home() / "Library"),
    str(Path(__file__).resolve().parent.parent),
]


def is_protected(path: Path) -> bool:
    resolved = path.resolve()
    for p in PROTECTED_EXACT:
        if resolved == Path(p).resolve():
            return True
    for p in PROTECTED_PREFIXES:
        try:
            resolved.relative_to(Path(p).resolve())
            return True
        except ValueError:
            continue
    return False


def validate_source_directory(path: Path) -> Path:
    if not path.exists():
        raise ValueError(f"Directory does not exist: {path}")
    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")
    if not os.access(path, os.R_OK):
        raise ValueError(f"Permission denied: {path}")
    if path.is_symlink():
        raise ValueError(f"Symbolic links are not supported as source: {path}")
    if is_protected(path):
        raise ValueError(f"Protected directory, cannot organize: {path}")
    return path.resolve()


def safe_destination(root: Path, destination: Path) -> Path:
    resolved_root = root.resolve()
    resolved_dest = destination.resolve()
    try:
        resolved_dest.relative_to(resolved_root)
    except ValueError:
        raise ValueError(f"Destination {destination} escapes root {root}")
    return resolved_dest


def resolve_conflict(destination: Path) -> Path:
    if not destination.exists():
        return destination
    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    counter = 1
    while True:
        new_path = parent / f"{stem} ({counter}){suffix}"
        if not new_path.exists():
            return new_path
        counter += 1
