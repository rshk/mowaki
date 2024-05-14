from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, Table, Text

from .metadata import metadata

UsersTable = Table(
    "users",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("email", Text, index=True, unique=True, nullable=False),
    Column("password", Text, nullable=True),
    Column(
        "date_created",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    ),
)
