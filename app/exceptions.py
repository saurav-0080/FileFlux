"""
Application exception hierarchy for FileFlux.
"""


class FileFluxError(Exception):
    """Base exception for all FileFlux errors."""


class ScanError(FileFluxError):
    """Raised when directory scanning fails."""


class OrganizerError(FileFluxError):
    """Raised when file organization fails."""


class ConfigurationError(FileFluxError):
    """Raised when configuration is invalid or corrupt."""


class DatabaseError(FileFluxError):
    """Raised when database operations fail."""


class ValidationError(FileFluxError):
    """Raised when path or input validation fails."""


class PermissionError(FileFluxError):
    """Raised when file system permission is denied."""


class SafetyError(FileFluxError):
    """Raised when a safety check blocks an operation."""
