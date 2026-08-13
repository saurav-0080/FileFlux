"""
Rule engine for the Smart File Organizer.

Answers a single question: given a file extension, which category does
it belong to? Categories and their extensions come from rules.json —
nothing here is hardcoded, so adding a new file type only ever requires
editing rules.json, never this module.
"""

from typing import Dict, List

from app.constants import DEFAULT_CATEGORY


def get_category(extension: str, rules: Dict[str, List[str]]) -> str:
    """
    Determine which category a file extension belongs to.

    Args:
        extension: The file extension, including the dot (e.g. ".pdf").
        rules: The rules dictionary, typically from load_rules().

    Returns:
        The category name (e.g. "Documents"), or DEFAULT_CATEGORY
        ("Others") if the extension isn't found in any category.
    """
    extension = extension.lower()
    for category, extensions in rules.items():
        if extension in extensions:
            return category
    return DEFAULT_CATEGORY


def is_supported(extension: str, rules: Dict[str, List[str]]) -> bool:
    """
    Check whether a file extension is explicitly covered by any rule.

    Args:
        extension: The file extension, including the dot.
        rules: The rules dictionary, typically from load_rules().

    Returns:
        True if the extension is found in rules.json, False if it would
        fall back to DEFAULT_CATEGORY.
    """
    return get_category(extension, rules) != DEFAULT_CATEGORY


def get_all_categories(rules: Dict[str, List[str]]) -> List[str]:
    """
    Get the list of all category names defined in the rules.

    Args:
        rules: The rules dictionary, typically from load_rules().

    Returns:
        A list of category names (e.g. ["Images", "Videos", "Documents"]).
    """
    return list(rules.keys())
