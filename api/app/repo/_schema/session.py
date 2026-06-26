import sqlalchemy as sa

from app.lib.database.json_with_schema import JsonWithSchema
from app.types.session import AuthSessionData, AuthSessionMetadata

from .metadata import metadata

SessionTable = sa.Table(
    "auth_session",
    metadata,
    sa.Column("session_id", sa.Text, primary_key=True),
    # Hashed secret
    sa.Column("session_secret", sa.Text, nullable=False),
    # Dates are exposed in the main table for filtering
    sa.Column("creation_date", sa.DateTime(timezone=True), nullable=True, index=True),
    sa.Column("last_used_date", sa.DateTime(timezone=True), nullable=True, index=True),
    # User IDs are exposed in the main table to make querying easier
    sa.Column("authenticated_user_id", sa.Uuid, nullable=True, index=True),
    sa.Column("current_user_id", sa.Uuid, nullable=True, index=True),
    # Session metadata
    sa.Column("metadata", JsonWithSchema(AuthSessionMetadata)),
    # Authentication data
    sa.Column("data", JsonWithSchema(AuthSessionData)),
)
