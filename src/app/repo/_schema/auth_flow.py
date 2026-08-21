import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from .metadata import metadata

FlowTable = sa.Table(
    "auth_flow",
    metadata,
    sa.Column("flow_id", sa.UUID, primary_key=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, index=True),
    sa.Column("kind", sa.Text, nullable=False),
    sa.Column("state", JSONB, nullable=False),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True, index=True),
    sa.Column("session_id", sa.Text, nullable=True, index=True),
    sa.Column("is_completed", sa.Boolean, default=False),  # logical deletion
)
