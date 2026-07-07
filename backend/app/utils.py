"""
Helper functions for validation and formatting.
"""


def trim_title(title: str) -> str:
    """Trim leading/trailing whitespace from a task title."""
    return title.strip()
