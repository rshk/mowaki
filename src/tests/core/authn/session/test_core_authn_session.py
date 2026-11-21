from datetime import datetime

import pytest

from app.core.authn.exceptions import SessionNotFound
from app.core.authn.session import (
    create_session,
    get_session,
    get_session_from_token,
    invalidate_session,
)
from app.exceptions import ObjectNotFound
from app.types.auth.session import (
    AuthSession,
    AuthSessionMetadata,
    SessionToken,
)

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

    with subtests.test("Get session by id"):
        session3 = await get_session(session.session_id)
        assert isinstance(session3, AuthSession)
        assert session3.session_id == session.session_id
        assert session3.last_used_at == session2.last_used_at  # unchanged


class Test_get_session_from_token:
    async def test_malformed_token_raises_sessionnotfound(self):
        with pytest.raises(SessionNotFound) as exc:
            await get_session_from_token(SessionToken("not a valid token"))
        assert exc.value.args[0] == "Invalid session token"

    async def test_not_found_token_raises_sessionnotfound(self):
        with pytest.raises(SessionNotFound) as exc:
            await get_session_from_token(SessionToken("xxxxxx.yyyyyy"))
        assert exc.value.args[0] == "Session not found for token"


async def test_invalidate_session():
    session, _ = await create_session()
    assert await get_session(session.session_id) is not None

    await invalidate_session(session.session_id)
    with pytest.raises(ObjectNotFound):
        await get_session(session.session_id)
