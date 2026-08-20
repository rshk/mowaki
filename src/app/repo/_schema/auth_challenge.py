import sqlalchemy as sa

from app.lib.sql.json_with_schema import JsonWithSchema
from app.types.auth.challenges import ChallengeStateParamsTA

from .metadata import metadata

ChallengeTable = sa.Table(
    "auth_challenge",
    metadata,
    sa.Column("challenge_id", sa.UUID, primary_key=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, index=True),
    sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True, index=True),
    sa.Column("params", JsonWithSchema(ChallengeStateParamsTA)),
    sa.Column("processed", sa.Boolean, default=False),  # logical deletion
)
