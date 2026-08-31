from contextlib import asynccontextmanager
from datetime import datetime
import uuid

import pytest
from app.core.authn.exceptions import SessionNotFound
from app.core.authn.session import (
    create_session,
    edit_current_session,
    format_session_token,
    get_current_session,
    get_session,
    get_session_from_token,
    invalidate_session,
)
from app.core.context import RequestContext, get_request_context, request_context
from app.exceptions import ObjectNotFound
from app.lib.context import scoped_context
from app.svc.webapi import get_auth_subject_from_session
from app.types.auth.assertions import Assertion, EmailAuth, PasskeyAuth
from app.types.auth.passkey_data import PasskeyID
from app.types.auth.session import AuthSession, AuthSessionMetadata, SessionToken
from app.types.user import UserID

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


class Test_current_session_operations:
    @pytest.fixture
    def request_context_factory(self):
        @asynccontextmanager
        async def request_context_factory():
            session, new_token = await create_session()
            auth_subject = await get_auth_subject_from_session(session)

            ctx = RequestContext(
                auth_session=session,
                new_session_token=new_token,
                auth_subject=auth_subject,
            )

            with scoped_context(request_context, ctx):
                yield

        return request_context_factory

    async def test_get_current_session(self, request_context_factory):
        async with request_context_factory():
            session = get_current_session()
            assert isinstance(session, AuthSession)

    async def test_rotate_current_session_secret(self, request_context_factory):
        async with request_context_factory():
            session1 = get_current_session()

            async with edit_current_session() as upd:
                new_secret = await upd.rotate_secret()
                assert upd.new_secret is not None
                assert upd.new_secret == new_secret

            # Ensure new token is propagated to the context
            ctx = get_request_context()
            assert ctx.new_session_token == format_session_token(
                session1.session_id, new_secret
            )

        # Ensure updates took effect
        session2 = await get_session(session1.session_id)
        assert session2.session_id == session1.session_id
        assert session2.session_secret != session1.session_secret
        assert session2.last_used_at == session1.last_used_at

    async def test_edit_current_session_metadata(self, request_context_factory):
        async with request_context_factory():
            session1 = get_current_session()

            async with edit_current_session() as upd:
                async with upd.edit_metadata() as md:
                    md.user_agent = "FakeUserAgent/1.0"
                    md.ip_address = "1.2.3.4"
                assert upd.new_secret is None

            # No new token
            ctx = get_request_context()
            assert ctx.new_session_token is None

        session2 = await get_session(session1.session_id)
        assert session2.session_id == session1.session_id
        assert session2.session_secret == session1.session_secret
        assert session2.metadata.user_agent == "FakeUserAgent/1.0"
        assert session2.metadata.ip_address == "1.2.3.4"

    async def test_manipulate_assertions(self, request_context_factory, subtests):
        async with request_context_factory():
            with subtests.test("Add a new assertion"):
                async with edit_current_session() as upd:
                    assertion1 = Assertion.from_params(EmailAuth("foo@example.com"))
                    assertion2 = Assertion.from_params(
                        PasskeyAuth(PasskeyID(uuid.UUID("01a045ac-f71c-7170-81b3-46dfd21d742a")),
                                    UserID(uuid.UUID("01a045ad-1b5b-7701-bf26-3d6762babf15")))
                    )
                    await upd.add_assertion(assertion1)
