"""
Duplicate detection engine for the Smart File Organizer.

Detects duplicate files using SHA-256 hashing. Files are grouped by
size first — only files sharing the same size are hashed, which avoids
unnecessary computation on large directories.
"""

from typing import Dict, List

from app.hash_utils import calculate_sha256
from app.logger import setup_logger
from app.models import FileInfo
from app.utils import format_size

logger = setup_logger()


class DuplicateDetector:
    """Detects duplicate files in a list of FileInfo objects."""

    def __init__(self, files: List[FileInfo]):
        self.files = files
        self.duplicate_groups: List[List[FileInfo]] = []

    def find_duplicates(self) -> List[FileInfo]:
        """
        Hash all files and mark duplicates.

        Returns:
            The same file list with sha256_hash, is_duplicate,
            and duplicate_of fields populated.
        """
        logger.info("Duplicate detection started")

        # Group by size first — skip hashing files with unique sizes
        size_groups: Dict[int, List[FileInfo]] = {}
        for f in self.files:
            size_groups.setdefault(f.size, []).append(f)

        hash_map: Dict[str, FileInfo] = {}

        for group in size_groups.values():
            if len(group) < 2:
                continue  # unique size — cannot be a duplicate

            for file_info in group:
                try:
                    file_hash = calculate_sha256(file_info.path)
                    file_info.sha256_hash = file_hash
                    logger.info(f"Calculating SHA256: {file_info.name}")

                    if file_hash in hash_map:
                        file_info.is_duplicate = True
                        file_info.duplicate_of = hash_map[file_hash].name
                        logger.warning(
                            f"Duplicate found: {file_info.name} -> {hash_map[file_hash].name}"
                        )
                    else:
                        hash_map[file_hash] = file_info

                except (PermissionError, OSError) as e:
                    logger.warning(f"Could not hash {file_info.name}: {e}")

        logger.info(
            f"Detection finished. Duplicates: {sum(1 for f in self.files if f.is_duplicate)}"
        )
        return self.files

    def group_duplicates(self) -> List[List[FileInfo]]:
        """
        Group duplicate files together with their originals.

        Returns:
            List of groups, each group being a list of FileInfo
            objects sharing the same SHA-256 hash.
        """
        groups: Dict[str, List[FileInfo]] = {}
        for f in self.files:
            if f.sha256_hash:
                groups.setdefault(f.sha256_hash, []).append(f)
        return [g for g in groups.values() if len(g) > 1]

    def generate_duplicate_report(self) -> str:
        """
        Generate a human-readable duplicate report.

        Returns:
            A formatted string report.
        """
        groups = self.group_duplicates()
        if not groups:
            return "No duplicates found."

        lines = ["Duplicate Files Report", "=" * 40]
        total_duplicates = 0
        space_wasted = 0

        for group in groups:
            original = group[0]
            duplicates = group[1:]
            lines.append(f"\nOriginal: {original.name}")
            lines.append("Duplicates:")
            for d in duplicates:
                lines.append(f"  - {d.name}")
                space_wasted += d.size
                total_duplicates += 1
            lines.append("-" * 40)

        lines.append(f"\nTotal Duplicate Groups : {len(groups)}")
        lines.append(f"Duplicate Files        : {total_duplicates}")
        lines.append(f"Space Wasted           : {format_size(space_wasted)}")
        return "\n".join(lines)

    def mark_duplicate_files(self) -> List[FileInfo]:
        """
        Run find_duplicates and return only the duplicate files.

        Returns:
            List of FileInfo objects marked as duplicates.
        """
        self.find_duplicates()
        return [f for f in self.files if f.is_duplicate]
