"""
Progress tracking for long-running operations in the Smart File Organizer.

This module is completely independent of Tkinter or any GUI framework.
Core modules (scanner, organizer, duplicate detector) report progress
through this structure — the GUI layer reads it and updates the UI.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Progress:
    """
    Tracks the state of a long-running operation.

    Attributes:
        operation: Human-readable name of the current operation.
        current: Number of items processed so far.
        total: Total number of items to process.
        message: Optional detail message for the current step.
    """
    operation: str
    current: int = 0
    total: int = 0
    message: str = ""

    @property
    def percentage(self) -> float:
        """Return completion percentage, or 0.0 if total is unknown."""
        if self.total == 0:
            return 0.0
        return round((self.current / self.total) * 100, 1)

    @property
    def is_complete(self) -> bool:
        """Return True if current has reached total."""
        return self.total > 0 and self.current >= self.total

    def update(self, current: int, message: str = "") -> None:
        """
        Update progress state.

        Args:
            current: New current count.
            message: Optional status message.
        """
        self.current = current
        self.message = message

    def __str__(self) -> str:
        return f"{self.operation}: {self.current}/{self.total} ({self.percentage}%)"