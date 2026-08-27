import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from ._utils import primary_key_column, primary_key_reference
from .metadata import metadata

FlowTable = sa.Table(
    "auth_flow",
    metadata,
    primary_key_column("flow_id"),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, index=True),
    sa.Column("kind", sa.Text, nullable=False),
    sa.Column("state", JSONB, nullable=False),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True, index=True),
    primary_key_reference("session_id", fk="auth_session.session_id"),
    sa.Column("is_completed", sa.Boolean, default=False),  # logical deletion
)
