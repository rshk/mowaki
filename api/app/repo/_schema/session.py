import sqlalchemy as sa

from app.types.session import AuthSessionMetadata
from app.lib.database.json_with_schema import JsonWithSchema

from .metadata import metadata

SessionTable = sa.Table(
    "auth_session",
    metadata,
    sa.Column("id", sa.Text, primary_key=True),
    sa.Column("soft_expiration_date", sa.DateTime(timezone=True), nullable=True),
    sa.Column("hard_expiration_date", sa.DateTime(timezone=True), nullable=True),
    sa.Column("metadata", JsonWithSchema(AuthSessionMetadata)),
)
