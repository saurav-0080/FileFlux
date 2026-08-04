"""
Organizer engine for the Smart File Organizer.

Takes scanned FileInfo objects, determines each file's category via the
rule engine, creates destination folders as needed, and moves files
safely — never overwriting an existing file. This is the module that
actually changes the filesystem; scanner.py only reads.
"""

import shutil
import time
from pathlib import Path
from typing import Dict, List

from app.models import FileInfo
from app.rule_engine import get_category
from app.logger import setup_logger

logger = setup_logger()


class Organizer:
    """
    Organizes a list of scanned files into category folders.

    Attributes:
        base_directory: The root folder being organized (where category
            subfolders will be created).
        rules: The extension-to-category mapping from rules.json.
    """

    def __init__(self, base_directory: Path, rules: Dict[str, List[str]]):
        """
        Args:
            base_directory: The folder being organized.
            rules: The rules dictionary, typically from load_rules().
        """
        self.base_directory = base_directory
        self.rules = rules
        self.folders_created: set = set()

    def create_category_folder(self, category: str) -> Path:
        """
        Create a category subfolder inside base_directory if it doesn't
        already exist.

        Args:
            category: The category name (e.g. "Images").

        Returns:
            Path to the category folder.
        """
        folder_path = self.base_directory / category
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            self.folders_created.add(str(folder_path))
            logger.info(f"Folder created: {folder_path}")
        return folder_path

    def generate_destination(self, file_info: FileInfo) -> Path:
        """
        Determine where a file should be moved to, based on its category.

        Args:
            file_info: The file to generate a destination for.

        Returns:
            The planned destination path (category folder + filename).
        """
        category_folder = self.create_category_folder(file_info.category)
        return category_folder / file_info.name

    def handle_duplicate_name(self, destination: Path) -> Path:
        """
        If destination already exists, generate a non-colliding filename
        by appending (1), (2), etc.

        Args:
            destination: The originally planned destination path.

        Returns:
            A destination path guaranteed not to already exist.
        """
        if not destination.exists():
            return destination

        counter = 1
        stem = destination.stem
        suffix = destination.suffix
        parent = destination.parent

        new_destination = parent / f"{stem}({counter}){suffix}"
        while new_destination.exists():
            counter += 1
            new_destination = parent / f"{stem}({counter}){suffix}"

        logger.info(f"Duplicate filename resolved: {destination.name} -> {new_destination.name}")
        return new_destination

    def move_file(self, file_info: FileInfo) -> FileInfo:
        """
        Move a single file to its category folder, handling duplicates
        and errors safely.

        Args:
            file_info: The file to move. Must already have .category set.

        Returns:
            The same FileInfo, updated with destination_path, moved, and
            error_message reflecting the outcome.
        """
        try:
            destination = self.generate_destination(file_info)
            destination = self.handle_duplicate_name(destination)

            logger.info(f"Moving: {file_info.name} -> {destination.parent.name}/")
            shutil.move(str(file_info.path), str(destination))

            file_info.destination_path = destination
            file_info.moved = True
            file_info.error_message = None

        except (PermissionError, OSError) as e:
            file_info.moved = False
            file_info.error_message = str(e)
            logger.warning(f"Failed to move {file_info.name}: {e}")

        return file_info

    def organize(self, files: List[FileInfo]) -> List[FileInfo]:
        """
        Categorize and move a list of scanned files.

        Args:
            files: List of FileInfo objects, typically from scanner.scan().

        Returns:
            The same list, with each FileInfo updated to reflect its
            category, destination, and move outcome.
        """
        logger.info("Scanning started")
        logger.info("Rules loaded")

        for file_info in files:
            file_info.category = get_category(file_info.extension, self.rules)
            self.move_file(file_info)

        logger.info(f"Files moved: {sum(1 for f in files if f.moved)}")
        return files

    def create_summary(self, files: List[FileInfo], elapsed_seconds: float) -> Dict:
        """
        Build a summary report of an organize() run.

        Args:
            files: The list of FileInfo objects after organize() has run.
            elapsed_seconds: Total time taken for the operation.

        Returns:
            A dictionary with counts of scanned/moved/skipped/errored
            files, folders created, and elapsed time.
        """
        moved = sum(1 for f in files if f.moved)
        errors = sum(1 for f in files if f.error_message is not None)
        skipped = len(files) - moved - errors

        return {
            "files_scanned": len(files),
            "files_moved": moved,
            "skipped": skipped,
            "errors": errors,
            "folders_created": len(self.folders_created),
            "time_taken": round(elapsed_seconds, 2),
        }