import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from webauthn.helpers.structs import CredentialDeviceType

from ._utils import primary_key_column
from .metadata import metadata

AuthUserPasskeyTable = sa.Table(
    "auth_user_passkey",
    metadata,
    primary_key_column("passkey_id"),
    sa.Column("user_id", sa.UUID, sa.ForeignKey("user.id"), nullable=False, index=True),
    # Custom display name for the passkey
    sa.Column("display_name", sa.Text, nullable=True),
    # Creation date, informative
    sa.Column(
        "created_at",
        sa.DateTime(timezone=True),
        nullable=False,
        index=True,
    ),
    # Last used date, informative
    sa.Column(
        "last_used_at",
        sa.DateTime(timezone=True),
        nullable=True,
        index=True,
    ),
    # Webauthn params ------------------------------------------------
    sa.Column("credential_id", sa.LargeBinary, nullable=False),
    sa.Column("credential_public_key", sa.LargeBinary, nullable=False),
    sa.Column("sign_count", sa.Integer, nullable=False, default=0),
    sa.Column(
        "credential_device_type",
        sa.Enum(
            # Native ENUMs are annoying to manipulate with migrations.
            # Just use a VARCHAR(64) field to store enum values, and
            # do all the validation on the app side instead.
            CredentialDeviceType,
            native_enum=False,  # Use VARCHAR
            create_constraint=False,  # Do not create CHECK constraint
            length=64,  # VARCHAR length
            validate_strings=True,  # Validate input values
        ),
    ),
    sa.Column("credential_backed_up", sa.Boolean),
    sa.Column("transports", JSONB),  # list of strings
)
