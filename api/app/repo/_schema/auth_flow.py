from datetime import datetime, timezone

import sqlalchemy as sa

from app.lib.database.json_with_schema import JsonWithSchema
from app.repo._schema.utils import primary_key_column
from app.types.auth.challenges import ListOfChallenges

from .metadata import metadata

AuthFlowTable = sa.Table(
    "auth_flow",
    metadata,
    primary_key_column("flow_id"),
    sa.Column("session_id", sa.Text, nullable=True),
    sa.Column("kind", sa.Text),
    sa.Column("is_completed", sa.Boolean, default=False, nullable=False),
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    ),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column(
        "challenges",
        JsonWithSchema(ListOfChallenges),
        default=list,
        nullable=False,
    ),
)
