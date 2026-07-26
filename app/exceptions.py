"""
Custom exception classes for the Smart File Organizer.

Using specific exception types instead of generic ones makes error
handling clearer — callers can catch exactly the failure they expect,
and error messages describe what actually went wrong.
"""


class OrganizerError(Exception):
    """Base exception for all Smart File Organizer errors."""
    pass


class ConfigurationError(OrganizerError):
    """Raised when a configuration file is missing, unreadable, or invalid."""
    pass


class InvalidRuleError(OrganizerError):
    """Raised when a rule in rules.json is malformed or conflicting."""
    pass


class DuplicateFileError(OrganizerError):
    """Raised when a duplicate file conflict can't be resolved automatically."""
    pass