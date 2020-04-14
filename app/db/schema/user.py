from sqlalchemy import BigInteger, Column, DateTime, Table, Text

from app.utils.dates import utcnow

from ._metadata import metadata

UsersTable = Table(
    "users",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("email", Text, index=True, unique=True, nullable=False),
    Column("password", Text, nullable=False),
    Column("display_name", Text),
    Column(
        "date_created",
        DateTime(timezone=True),
        default=utcnow,
        nullable=False),
    Column(
        "date_updated",
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    ),
    Column("last_login_date", DateTime(timezone=True)),
)
