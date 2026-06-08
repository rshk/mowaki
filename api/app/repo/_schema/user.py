import sqlalchemy as sa

from app.lib.database.json_with_schema import JsonWithSchema
from app.types.user import UserMetadata

from .metadata import metadata
from .utils import primary_key_column

sa.Table(
    "user",
    metadata,
    primary_key_column(),
    sa.Column("email", sa.Text, nullable=False, unique=True, index=True),
    sa.Column("metadata", JsonWithSchema(UserMetadata), nullable=False, default=dict),
)
