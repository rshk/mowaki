from sqlalchemy import BigInteger, Boolean, Column, DateTime, Table, Text

from app.lib.dates import utcnow

from .metadata import metadata

UsersTable = Table(
    "users",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("email", Text, index=True, unique=True, nullable=False),
    Column("password", Text, nullable=True),
    Column("date_created", DateTime(timezone=True), default=utcnow, nullable=False),
)
