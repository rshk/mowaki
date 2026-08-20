import sqlalchemy as sa

from app.lib.sql.json_with_schema import JsonWithSchema
from app.types.auth.session import AssertionsList, AuthSessionMetadata

from .metadata import metadata

SessionTable = sa.Table(
    "auth_session",
    metadata,
    sa.Column("session_id", sa.Text, primary_key=True),
    sa.Column("session_secret", sa.Text, nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, index=True),
    sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True, index=True),
    sa.Column("metadata", JsonWithSchema(AuthSessionMetadata)),
    sa.Column("assertions", JsonWithSchema(AssertionsList)),
)

# sa.Index(
#     "ix_auth_session_data__authenticated_user_id",
#     SessionTable.c.data["authenticated_user_id"],
# )
# sa.Index(
#     "ix_auth_session_data__current_user_id",
#     SessionTable.c.data["current_user_id"],
# )
