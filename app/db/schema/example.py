from sqlalchemy import BigInteger, Column, DateTime, Table, Text

from app.utils.dates import utcnow

from ._metadata import metadata

NotesTable = Table(
    'notes', metadata,

    Column('id', BigInteger, primary_key=True),

    Column('title', Text, nullable=False),
    Column('text', Text, nullable=True),

    Column('date_created',
           DateTime(timezone=True), default=utcnow, nullable=False),

    Column('date_updated',
           DateTime(timezone=True), default=utcnow, onupdate=utcnow,
           nullable=False),
)
