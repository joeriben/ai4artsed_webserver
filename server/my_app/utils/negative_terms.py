"""Utilities for handling negative terms."""


def normalize_negative_terms(value: str | list | None) -> str:
    """Normalize negative terms to a comma-separated string.

    Args:
        value: Negative terms provided as a string, list, or None.

    Returns:
        A string with comma-separated negative terms. Returns an empty string
        if the input is None or empty.
    """
    if value is None:
        return ""

    if isinstance(value, list):
        return ", ".join(str(v).strip() for v in value if str(v).strip())

    return str(value).strip()
