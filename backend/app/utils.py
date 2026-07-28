"""
Helper functions for validation and formatting.
"""


def trim_title(title: str) -> str:
    """Strip leading/trailing whitespace from a task title.

    Args:
        title (str): The raw title string.

    Returns:
        str: The stripped title.

    [VERIFY]: This helper is not currently called anywhere in app/ —
    title stripping/validation is done inline in each
    ``field_validator`` in models.py instead. Confirm whether this is
    meant to be used there (deduplicating that logic) or is dead code.
    """
    return title.strip()
