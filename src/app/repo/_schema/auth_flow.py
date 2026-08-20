import sqlalchemy as sa

from app.lib.sql.json_with_schema import JsonWithSchema
from app.types.auth.auth_flow import FlowStateTA

from .metadata import metadata

FlowTable = sa.Table(
    "auth_flow",
    metadata,
    sa.Column("flow_id", sa.UUID, primary_key=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, index=True),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True, index=True),
    sa.Column("session_id", sa.Text, nullable=True, index=True),
    sa.Column("state", JsonWithSchema(FlowStateTA)),
    sa.Column("is_completed", sa.Boolean, default=False),  # logical deletion
)
