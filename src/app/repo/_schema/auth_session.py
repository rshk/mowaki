import sqlalchemy as sa

from app.lib.sql.json_with_schema import JsonWithSchema
from app.types.auth.session import AuthSessionData, AuthSessionMetadata

from .metadata import metadata

SessionTable = sa.Table(
    "auth_session",
    metadata,
    sa.Column("session_id", sa.Text, primary_key=True),
    # Hashed secret
    sa.Column("session_secret", sa.Text, nullable=False),
    # Dates are exposed in the main table for filtering
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, index=True),
    sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True, index=True),
    # Session metadata
    sa.Column("metadata", JsonWithSchema(AuthSessionMetadata)),
    # Authentication data
    sa.Column("data", JsonWithSchema(AuthSessionData)),
)

sa.Index(
    "ix_auth_session_data__authenticated_user_id",
    SessionTable.c.data["authenticated_user_id"],
)
sa.Index(
    "ix_auth_session_data__current_user_id",
    SessionTable.c.data["current_user_id"],
)
