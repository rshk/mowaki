import secrets
import uuid

import sqlalchemy as sa


def primary_key_column(name: str = "id") -> sa.Column:
    return sa.Column(name, sa.Uuid, primary_key=True, default=generate_primary_key)


def generate_primary_key() -> uuid.UUID:
    return uuid.uuid4()


def generate_secret(nbytes=None):
    """Generate a urlsafe token, which can be used as ID or secret"""
    return secrets.token_urlsafe(nbytes)
