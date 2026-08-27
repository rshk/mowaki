from datetime import datetime

import pytest
from app.core.authn.session import (
    create_session,
    get_or_create_session_from_token,
    get_session_from_token,
)
from app.types.auth.session import AuthSession, AuthSessionMetadata

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("database_schema"),
]


async def test_create_and_retrieve_session(subtests):
    with subtests.test("Create session"):
        session, token = await create_session()
        assert isinstance(session, AuthSession)
        assert isinstance(token, str)

        assert isinstance(session.session_id, str)
        assert isinstance(session.session_secret, str)
        assert isinstance(session.created_at, datetime)
        assert session.last_used_at is None
        assert session.metadata == AuthSessionMetadata.empty()
        assert session.assertions == []
        assert session.current_user_id is None

    with subtests.test("Get session from token"):
        session2 = await get_session_from_token(token)
        assert isinstance(session2, AuthSession)

        assert session2.session_id == session.session_id
        assert session2.session_secret == session.session_secret
        assert session2.last_used_at is not None  # Got updated
