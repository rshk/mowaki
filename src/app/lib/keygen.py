"""
Key generation functions.

Extracted to a module to centralize configuration (such as uuid scheme
and default secret length).
"""

import secrets
import uuid

# UUID v7 provides better performance due to it being sequential, at
# the cost of leaking creation date information.
# If this is an issue, set this to False to revert to UUID v4.
USE_UUID7 = True


def generate_uuid() -> uuid.UUID:
    """Generate a UUID using the selected schema"""
    if USE_UUID7:
        return uuid.uuid7()
    return uuid.uuid4()


def generate_secret(nbytes=None) -> str:
    """Generate a urlsafe token, which can be used as ID or secret"""
    return secrets.token_urlsafe(nbytes)
