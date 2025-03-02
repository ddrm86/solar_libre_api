"""
This module provides functions to manage database IDs.

UUIDs in string format are used as IDs, since the default database of choice is SQLite, which
currently does not support UUIDs natively.
"""
import uuid


def generate_uuid():
    """
    Generate a new UUID.

    Returns:
        str: A new UUID as a string.
    """
    return str(uuid.uuid4())
