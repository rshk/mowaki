from __future__ import annotations

import uuid
from datetime import datetime
from typing import NewType

from webauthn.helpers.structs import CredentialDeviceType

from app.lib.models import BaseModel
from app.types.user import UserID

PasskeyID = NewType("PasskeyID", uuid.UUID)
PasskeyCredentialID = NewType("PasskeyCredentialID", bytes)
PasskeyPublicKeyData = NewType("PasskeyPublicKeyData", bytes)


class AuthUserPasskey(BaseModel):
    passkey_id: PasskeyID
    user_id: UserID
    display_name: str | None
    created_at: datetime
    last_used_at: datetime | None

    # Webauthn params ------------------------------------------------
    credential_id: PasskeyCredentialID
    credential_public_key: PasskeyPublicKeyData
    sign_count: int
    credential_device_type: CredentialDeviceType
    credential_backed_up: bool
    transports: list[str]
