"""
Operation reporting for the Smart File Organizer.

Generates structured reports after scan or organize operations.
Reports can be exported as JSON or CSV.
"""

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.logger import setup_logger

logger = setup_logger()

REPORTS_DIR = Path("reports")


@dataclass
class FileOperation:
    """
    Records the result of a single file operation.

    Attributes:
        original_path: Where the file was before the operation.
        destination_path: Where the file was moved to, if applicable.
        status: One of MOVED, SKIPPED, ERROR, DUPLICATE.
        error: Error message if the operation failed.
    """

    original_path: str
    destination_path: str = ""
    status: str = "MOVED"
    error: str = ""


@dataclass
class OperationReport:
    """
    Summary report for a completed operation.

    Attributes:
        operation: Type of operation — 'scan' or 'organization'.
        started_at: When the operation began.
        completed_at: When the operation finished.
        files_scanned: Total files found during scan.
        files_moved: Number of files successfully moved.
        duplicates: Number of duplicate files detected.
        skipped: Number of files skipped.
        errors: Number of files that failed.
        space_processed: Total bytes processed.
        duration_seconds: How long the operation took.
        status: Final status — COMPLETED or FAILED.
        file_operations: Per-file operation records (for CSV export).
    """

    operation: str
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    files_scanned: int = 0
    files_moved: int = 0
    duplicates: int = 0
    skipped: int = 0
    errors: int = 0
    space_processed: int = 0
    duration_seconds: float = 0.0
    status: str = "COMPLETED"
    file_operations: List[FileOperation] = field(default_factory=list)

    def finish(self) -> None:
        """Mark the operation as complete and calculate duration."""
        self.completed_at = datetime.now()
        self.duration_seconds = round(
            (self.completed_at - self.started_at).total_seconds(), 2
        )

    def add_file_operation(
        self,
        original_path: str,
        destination_path: str = "",
        status: str = "MOVED",
        error: str = "",
    ) -> None:
        """Record the result of a single file operation."""
        self.file_operations.append(
            FileOperation(
                original_path=original_path,
                destination_path=destination_path,
                status=status,
                error=error,
            )
        )

    def to_dict(self) -> dict:
        """Convert report to a JSON-serializable dictionary."""
        return {
            "operation": self.operation,
            "started_at": self.started_at.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": self.completed_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.completed_at
            else None,
            "files_scanned": self.files_scanned,
            "files_moved": self.files_moved,
            "duplicates": self.duplicates,
            "skipped": self.skipped,
            "errors": self.errors,
            "space_processed_bytes": self.space_processed,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
        }

    def format_summary(self) -> str:
        """Return a human-readable text summary of the report."""
        started = self.started_at.strftime("%d %b %Y %H:%M:%S")
        completed = (
            self.completed_at.strftime("%d %b %Y %H:%M:%S")
            if self.completed_at
            else "N/A"
        )
        size_gb = self.space_processed / (1024**3)

        return (
            f"\nSmart File Organizer\n"
            f"{'─' * 40}\n"
            f"Operation       : {self.operation.title()}\n"
            f"Started         : {started}\n"
            f"Completed       : {completed}\n"
            f"{'─' * 40}\n"
            f"Files Scanned   : {self.files_scanned}\n"
            f"Files Moved     : {self.files_moved}\n"
            f"Duplicates      : {self.duplicates}\n"
            f"Skipped         : {self.skipped}\n"
            f"Errors          : {self.errors}\n"
            f"{'─' * 40}\n"
            f"Space Processed : {size_gb:.2f} GB\n"
            f"Duration        : {self.duration_seconds} seconds\n"
            f"Status          : {self.status}\n"
        )


def save_json_report(report: OperationReport) -> Path:
    """
    Save a report as a JSON file in the reports/ directory.

    Args:
        report: The completed OperationReport to save.

    Returns:
        Path to the saved JSON file.
    """
    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = REPORTS_DIR / f"report_{timestamp}.json"

    with open(file_path, "w") as f:
        json.dump(report.to_dict(), f, indent=4)

    logger.info(f"JSON report saved: {file_path}")
    return file_path


def save_csv_report(report: OperationReport) -> Path:
    """
    Save per-file operation details as a CSV file in the reports/ directory.

    Args:
        report: The completed OperationReport containing file operations.

    Returns:
        Path to the saved CSV file.
    """
    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = REPORTS_DIR / f"report_{timestamp}.csv"

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["original_path", "destination_path", "status", "error"])
        for op in report.file_operations:
            writer.writerow(
                [op.original_path, op.destination_path, op.status, op.error]
            )

    logger.info(f"CSV report saved: {file_path}")
    return file_path


def load_latest_report() -> Optional[dict]:
    """
    Load the most recent JSON report from the reports/ directory.

    Returns:
        Parsed report dictionary, or None if no reports exist.
    """
    if not REPORTS_DIR.exists():
        return None

    reports = sorted(REPORTS_DIR.glob("report_*.json"), reverse=True)
    if not reports:
        return None

    with open(reports[0]) as f:
        return json.load(f)
