from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from webauthn.helpers.structs import CredentialDeviceType

from app.lib.keygen import generate_uuid
from app.lib.sql.table_helper import TableHelper, UpdateHelper
from app.repo._schema.auth_user_passkey import AuthUserPasskeyTable
from app.resources import get_database
from app.types.auth.auth_user_passkey import (
    AuthUserPasskey,
    PasskeyCredentialID,
    PasskeyPublicKeyData,
)
from app.types.auth.passkey_data import PasskeyID
from app.types.user import UserID

_th = TableHelper[AuthUserPasskey, PasskeyID](
    AuthUserPasskeyTable,
    model=AuthUserPasskey,
    get_engine=get_database,
)


async def create(
    user_id: UserID,
    credential_id: PasskeyCredentialID,
    public_key: PasskeyPublicKeyData,
    display_name: str | None = None,
    device_type: CredentialDeviceType | None = None,
    backed_up: bool = False,
    transports: list[str] | None = None,
) -> PasskeyID:
    if device_type is None:
        device_type = CredentialDeviceType.SINGLE_DEVICE
    if transports is None:
        transports = []

    return await _th.insert(
        passkey_id=generate_uuid(),
        user_id=user_id,
        display_name=display_name,
        created_at=datetime.now(UTC),
        last_used_at=None,
        credential_id=credential_id,
        credential_public_key=public_key,
        sign_count=0,
        credential_device_type=device_type,
        credential_backed_up=backed_up,
        transports=transports,
    )


async def get(passkey_id: PasskeyID) -> AuthUserPasskey:
    return await _th.get_by_pk(passkey_id)


@asynccontextmanager
async def for_update(
    passkey_id: PasskeyID,
) -> AsyncGenerator[UpdateHelper[AuthUserPasskey]]:
    async with _th.for_update(passkey_id) as upd:
        yield upd


async def delete(passkey_id: PasskeyID):
    await _th.delete(passkey_id)
