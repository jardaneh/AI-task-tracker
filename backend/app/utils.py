"""
Helper functions for validation and formatting.
"""


def trim_title(title: str) -> str:
    """Trim leading/trailing whitespace from a task title.

    Note: not currently called anywhere in this codebase (verified via
    project-wide search); the live validation path trims titles inline in
    the ``TaskCreate``/``TaskUpdate`` field validators in ``models.py``.
    [VERIFY] whether this function is retained for future use or should be
    removed as dead code.

    Args:
        title (str): Raw title string.

    Returns:
        str: ``title`` with leading and trailing whitespace removed.
    """
    return title.strip()
