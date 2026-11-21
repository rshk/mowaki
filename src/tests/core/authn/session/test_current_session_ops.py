import pytest
import pytest_asyncio
from app import repo
from app.core.authn.session import (
    create_session,
    edit_session_metadata,
    get_current_session,
    get_session,
    invalidate_current_session,
    parse_session_token,
    rotate_current_session_secret,
)
from app.core.context import get_request_context
from app.exceptions import ObjectNotFound
from app.repo.auth.session import hash_session_secret
from app.types.auth import assertions
from app.types.auth.session import (
    AuthSession,
    AuthSessionMetadata,
    HashedSessionSecret,
    SessionToken,
)

from tests.utils.session import TestingRequestContextManager

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("database_schema", "request_ctx"),
]


class Test_get_current_session:
    @pytest_asyncio.fixture
    async def request_ctx_manager(self) -> TestingRequestContextManager:
        return TestingRequestContextManager()

    async def test_get_current_session(self):
        session = get_current_session()
        assert isinstance(session, AuthSession)
        assert session.session_id is not None
        assert session.session_secret is not None
        assert session.created_at is not None
        assert session.last_used_at is None
        assert session.metadata == AuthSessionMetadata.empty()
        assert session.assertions == []
        assert session.current_user_id is None


class Test_get_current_session_with_assertions:
    @pytest_asyncio.fixture
    async def request_ctx_manager(self) -> TestingRequestContextManager:
        return TestingRequestContextManager(
            assertions=[assertions.EmailAuth(email_address="user@example.com")]
        )

    async def test_get_current_session(self):
        session = get_current_session()
        assert isinstance(session, AuthSession)
        assert len(session.assertions) == 1
        assert session.assertions[0].params == assertions.EmailAuth(
            email_address="user@example.com"
        )


class Test_get_current_session_with_user_id:
    @pytest_asyncio.fixture
    async def request_ctx_manager(self) -> TestingRequestContextManager:
        return TestingRequestContextManager(current_user_id=True)

    async def test_get_current_session(self):
        session = get_current_session()
        assert isinstance(session, AuthSession)
        assert session.current_user_id is not None


async def test_invalidate_current_session():
    old_session = get_current_session()

    await invalidate_current_session()

    new_session = get_current_session()

    # Ensure session has been updated in request context
    assert new_session.session_id != old_session.session_id

    # Ensure old session was deleted
    with pytest.raises(ObjectNotFound):
        await get_session(old_session.session_id)

    # Ensure the new token has been updated in the session
    ctx = get_request_context()
    assert ctx.new_session_token is not None
    token_info = parse_session_token(ctx.new_session_token)
    assert token_info.session_id == new_session.session_id


async def test_rotate_current_session_secret():
    old_session = get_current_session()

    await rotate_current_session_secret()

    new_session = get_current_session()

    # Session ID is unchanged
    assert old_session.session_id == new_session.session_id

    # Ensure the new token has been updated in the session
    ctx = get_request_context()
    assert ctx.new_session_token is not None
    token_info = parse_session_token(ctx.new_session_token)
    assert token_info.session_id == new_session.session_id
    assert new_session.session_secret != old_session.session_secret

    # Ensure session has been updated in the database
    session2 = await get_session(old_session.session_id)
    assert session2.session_id == new_session.session_id
    assert session2.session_secret == new_session.session_secret
    assert session2.session_secret != old_session.session_secret


class Test_edit_blank_metadata:
    async def test_edit_current_session_metadata(self, subtests: pytest.Subtests):
        session = get_current_session()
        session_id = session.session_id

        assert session.metadata.user_agent is None
        assert session.metadata.ip_address is None

        async with edit_session_metadata() as md:
            md.user_agent = "FakeUserAgent/1.0"
            md.ip_address = "1.2.3.4"

        with subtests.test("Session has been updated in context"):
            session_ctx = get_current_session()
            assert session_ctx.session_id == session_id
            assert session_ctx.session_secret == session.session_secret
            assert session_ctx.metadata.user_agent == "FakeUserAgent/1.0"
            assert session_ctx.metadata.ip_address == "1.2.3.4"

        with subtests.test("Session has been updated in the database"):
            session_db = await get_session(session.session_id)
            assert session_db.session_id == session.session_id
            assert session_db.session_secret == session.session_secret
            assert session_db.metadata.user_agent == "FakeUserAgent/1.0"
            assert session_db.metadata.ip_address == "1.2.3.4"

        with subtests.test("Original session object is untouched"):
            # Update the RequestContext with a new instance, not the
            # AuthSession directly
            assert session.metadata.user_agent is None
            assert session.metadata.ip_address is None


class Test_edit_existing_metadata:
    @pytest_asyncio.fixture
    async def request_ctx_manager(self) -> TestingRequestContextManager:
        metadata = AuthSessionMetadata(
            user_agent="OriginalUserAgent/1.0",
            ip_address="2.2.2.2",
        )
        session_id, _ = await repo.auth.session.create(metadata=metadata)
        return TestingRequestContextManager(session_id=session_id)

    async def test_edit_metadata(self, subtests: pytest.Subtests):
        session = get_current_session()
        session_id = session.session_id

        assert session.metadata.user_agent == "OriginalUserAgent/1.0"
        assert session.metadata.ip_address == "2.2.2.2"

        async with edit_session_metadata() as md:
            md.user_agent = "NewUserAgent/1.0"
            md.ip_address = "3.3.3.3"

        with subtests.test("Session has been updated in context"):
            session_ctx = get_current_session()
            assert session_ctx.session_id == session_id
            assert session_ctx.session_secret == session.session_secret
            assert session_ctx.metadata.user_agent == "NewUserAgent/1.0"
            assert session_ctx.metadata.ip_address == "3.3.3.3"

        # Ensure session has been updated in the database
        with subtests.test("Session has been updated in the database"):
            session_db = await get_session(session.session_id)
            assert session_db.session_id == session.session_id
            assert session_db.session_secret == session.session_secret
            assert session_db.metadata.user_agent == "NewUserAgent/1.0"
            assert session_db.metadata.ip_address == "3.3.3.3"


#     class Test_add_assertion:
#         async def test_add_assertion(self, subtests, request_context_factory):
#             async with request_context_factory():
#                 session_id = get_current_session().session_id
#                 _prev_secret = get_current_session().session_secret
#                 _prev_token = get_request_context().new_session_token

#                 with subtests.test("email-auth for non-user"):
#                     # Add an "email auth" assertion associated with an email address
#                     # not currently tied to any user.

#                     assertion1 = EmailAuth("not-a-user@example.com")
#                     await add_session_assertion(assertion1)

#                     # Verify both the session in the request context
#                     # and the one stored in the database.

#                     ctx_session = get_current_session()
#                     db_session = await get_session(session_id)

#                     for session in (ctx_session, db_session):
#                         assert session.session_id == session_id
#                         assert session.session_secret != _prev_secret  # rotated
#                         assert session.assertions == [Assertion.from_params(assertion1)]
#                         assert session.current_user_id is None

#                     assert ctx_session.session_secret == db_session.session_secret
#                     _new_secret = db_session.session_secret

#                     # Make sure a new session token has been generated
#                     _new_token = get_request_context().new_session_token
#                     assert _new_token is not None
#                     assert _new_token != _prev_token

#                     # Make sure the new token matches the secret
#                     assert _token_matches_secret(_new_token, _new_secret)

#                     # Update "previous" values
#                     _prev_secret = _new_secret
#                     _prev_token = _new_token

#                 with subtests.test("email-auth for user"):
#                     # Add a second "email auth" assertion, this time
#                     # associated with an email address belonging to a
#                     # user.
#                     # This will set session.current_user_id to the
#                     # user_id provided by the new assertion.

#                     assertion2 = EmailAuth("user-1@example.com")
#                     await add_session_assertion(assertion2)

#                     # Verify both the session in the request context
#                     # and the one stored in the database.

#                     ctx_session = get_current_session()
#                     db_session = await get_session(session_id)

#                     for session in (ctx_session, db_session):
#                         assert session.session_id == session_id
#                         assert session.session_secret != _prev_secret  # rotated
#                         assert session.assertions == [assertion1, assertion2]
#                         assert session.current_user_id == UserID(
#                             uuid.UUID("4e81dca7-4888-4fad-b056-e767acda47c3")
#                         )

#                     assert ctx_session.session_secret == db_session.session_secret
#                     _new_secret = db_session.session_secret

#                     # Make sure a new session token has been generated
#                     _new_token = get_request_context().new_session_token
#                     assert _new_token is not None
#                     assert _new_token != _prev_token

#                     # Make sure the new token matches the secret
#                     assert _token_matches_secret(_new_token, _new_secret)

#                     # Update "previous" values
#                     _prev_secret = _new_secret
#                     _prev_token = _new_token

#                 with subtests.test("email-auth for different user"):
#                     assertion3 = EmailAuth("user-2@example.com")
#                     await add_session_assertion(assertion3)

#                     # Verify both the session in the request context
#                     # and the one stored in the database.

#                     ctx_session = get_current_session()
#                     db_session = await get_session(session_id)

#                     for session in (ctx_session, db_session):
#                         assert session.assertions == [
#                             assertion1,
#                             assertion2,
#                             assertion3,
#                         ]
#                         assert session.current_user_id == UserID(
#                             uuid.UUID("4e81dca7-4888-4fad-b056-e767acda47c3")
#                         )

#                     assert ctx_session.session_secret == db_session.session_secret
#                     _new_secret = db_session.session_secret

#                     # Make sure a new session token has been generated
#                     _new_token = get_request_context().new_session_token
#                     assert _new_token is not None
#                     assert _new_token != _prev_token

#                     # Make sure the new token matches the secret
#                     assert _token_matches_secret(_new_token, _new_secret)

#         async def test_add_assertion_for_user(self, request_context_factory):

#             # Add an assertion tied to a user.
#             # Ensure that current_user_id is set automatically.

#             async with request_context_factory():
#                 session_id = get_current_session().session_id
#                 _prev_secret = get_current_session().session_secret
#                 _prev_token = get_request_context().new_session_token

#                 # Add an "email auth" assertion associated with an email address
#                 # belonging to a user.

#                 assertion = EmailAuth("user-1@example.com")
#                 await add_session_assertion(assertion)

#                 # Verify both the session in the request context
#                 # and the one stored in the database.

#                 ctx_session = get_current_session()
#                 db_session = await get_session(session_id)

#                 for session in (ctx_session, db_session):
#                     assert session.session_id == session_id
#                     assert session.session_secret != _prev_secret  # rotated
#                     assert session.assertions == [assertion]
#                     assert session.current_user_id == UserID(
#                         uuid.UUID("4e81dca7-4888-4fad-b056-e767acda47c3")
#                     )

#                 assert ctx_session.session_secret == db_session.session_secret
#                 _new_secret = db_session.session_secret

#                 # Make sure a new session token has been generated
#                 _new_token = get_request_context().new_session_token
#                 assert _new_token is not None
#                 assert _new_token != _prev_token

#                 # Make sure the new token matches the secret
#                 assert _token_matches_secret(_new_token, _new_secret)

#         async def test_add_assertion_for_different_user(self, request_context_factory):

#             # The session already has an email-auth assertion for a
#             # different user, and a current_user_id set.
#             # Add another email-auth assertion for a different
#             # email/user combination, and ensure current_user_id is
#             # *not* updated this time.

#             user_id = UserID(uuid.UUID("4e81dca7-4888-4fad-b056-e767acda47c3"))
#             assertions = [
#                 Assertion.from_params(EmailAuth("user-1@example.com")),
#             ]

#             async with request_context_factory(
#                 assertions=assertions, current_user_id=user_id
#             ):
#                 session_id = get_current_session().session_id
#                 _prev_secret = get_current_session().session_secret
#                 _prev_token = get_request_context().new_session_token

#                 # Add an "email auth" assertion associated with an email address
#                 # belonging to a different user.

#                 assertion = EmailAuth("user-2@example.com")
#                 await add_session_assertion(assertion)

#                 # Verify both the session in the request context
#                 # and the one stored in the database.

#                 ctx_session = get_current_session()
#                 db_session = await get_session(session_id)

#                 for session in (ctx_session, db_session):
#                     assert session.session_id == session_id
#                     assert session.session_secret != _prev_secret  # rotated
#                     assert session.assertions == [*assertions, assertion]
#                     assert session.current_user_id == UserID(
#                         uuid.UUID("4e81dca7-4888-4fad-b056-e767acda47c3")
#                     )

#                 assert ctx_session.session_secret == db_session.session_secret
#                 _new_secret = db_session.session_secret

#                 # Make sure a new session token has been generated
#                 _new_token = get_request_context().new_session_token
#                 assert _new_token is not None
#                 assert _new_token != _prev_token

#                 # Make sure the new token matches the secret
#                 assert _token_matches_secret(_new_token, _new_secret)

#         async def test_add_same_assertion_twice(self, request_context_factory):

#             # Add the same assertion again, and make sure only the
#             # last one is kept.

#             user_id = UserID(uuid.UUID("4e81dca7-4888-4fad-b056-e767acda47c3"))
#             assertions = [
#                 Assertion.from_params(EmailAuth("user-1@example.com")),
#             ]

#             async with request_context_factory(
#                 assertions=assertions, current_user_id=user_id
#             ):
#                 session_id = get_current_session().session_id
#                 _prev_secret = get_current_session().session_secret
#                 _prev_token = get_request_context().new_session_token

#                 # Add an "email auth" assertion associated with an email address
#                 # belonging to a different user.

#                 assertion = EmailAuth("user-1@example.com")
#                 await add_session_assertion(assertion)

#                 # Verify both the session in the request context
#                 # and the one stored in the database.

#                 ctx_session = get_current_session()
#                 db_session = await get_session(session_id)

#                 for session in (ctx_session, db_session):
#                     assert session.session_id == session_id
#                     assert session.session_secret != _prev_secret  # rotated
#                     assert session.assertions == [assertion]
#                     assert session.current_user_id == UserID(
#                         uuid.UUID("4e81dca7-4888-4fad-b056-e767acda47c3")
#                     )

#                 assert ctx_session.session_secret == db_session.session_secret
#                 _new_secret = db_session.session_secret

#                 # Make sure a new session token has been generated
#                 _new_token = get_request_context().new_session_token
#                 assert _new_token is not None
#                 assert _new_token != _prev_token

#                 # Make sure the new token matches the secret
#                 assert _token_matches_secret(_new_token, _new_secret)

#         async def test_add_same_assertion_with_different_user_id(
#             self, request_context_factory
#         ):

#             # Add the same assertion again, only this time it is
#             # associated to a different user ID!

#             user_email = "user-1@example.com"

#             user_id1 = UserID(uuid.UUID("4e81dca7-4888-4fad-b056-e767acda47c3"))
#             assertion1 = Assertion.from_params(EmailAuth(user_email))

#             user_id2 = UserID(uuid.UUID("d117eb12-9db6-4c08-ae5d-206aafdeba94"))
#             assertion2 = EmailAuth(user_email)

#             async with request_context_factory(
#                 assertions=[assertion1], current_user_id=user_id1
#             ):
#                 session_id = get_current_session().session_id
#                 _prev_secret = get_current_session().session_secret
#                 _prev_token = get_request_context().new_session_token

#                 # Same email, different user ID
#                 await add_session_assertion(assertion2)

#                 # Verify both the session in the request context
#                 # and the one stored in the database.

#                 ctx_session = get_current_session()
#                 db_session = await get_session(session_id)

#                 for session in (ctx_session, db_session):
#                     assert session.session_id == session_id
#                     assert session.session_secret != _prev_secret  # rotated
#                     assert session.assertions == [assertion2]
#                     assert session.current_user_id == user_id2  # updated!

#                 assert ctx_session.session_secret == db_session.session_secret
#                 _new_secret = db_session.session_secret

#                 # Make sure a new session token has been generated
#                 _new_token = get_request_context().new_session_token
#                 assert _new_token is not None
#                 assert _new_token != _prev_token

#                 # Make sure the new token matches the secret
#                 assert _token_matches_secret(_new_token, _new_secret)

#     class Test_set_current_user_id:
#         async def test_set_current_user_id_to_valid_id(self, request_context_factory):
#             user_id = UserID(uuid.UUID("4e81dca7-4888-4fad-b056-e767acda47c3"))
#             assertions = [
#                 Assertion.from_params(EmailAuth("u1@example.com")),
#             ]

#             async with request_context_factory(assertions=assertions):
#                 session_id = get_current_session().session_id
#                 _prev_secret = get_current_session().session_secret
#                 _prev_token = get_request_context().new_session_token

#                 await set_current_user_id(user_id)

#                 # Verify both the session in the request context
#                 # and the one stored in the database.

#                 ctx_session = get_current_session()
#                 db_session = await get_session(session_id)

#                 for session in (ctx_session, db_session):
#                     assert session.session_id == session_id
#                     assert session.session_secret != _prev_secret  # rotated
#                     assert session.current_user_id == user_id  # updated

#                 assert ctx_session.session_secret == db_session.session_secret
#                 _new_secret = db_session.session_secret

#                 # Make sure a new session token has been generated
#                 _new_token = get_request_context().new_session_token
#                 assert _new_token is not None
#                 assert _new_token != _prev_token

#                 # Make sure the new token matches the secret
#                 assert _token_matches_secret(_new_token, _new_secret)

#         async def test_set_current_user_id_to_second_valid_id(
#             self, request_context_factory
#         ):
#             user_id1 = UserID(uuid.UUID("4e81dca7-1111-4fad-b056-e767acda47c3"))
#             user_id2 = UserID(uuid.UUID("6c87c6e3-2222-4ac2-a578-6bc7bcc9fce4"))
#             assertions = [
#                 Assertion.from_params(EmailAuth("u1@example.com")),
#                 Assertion.from_params(EmailAuth("u2@example.com")),
#             ]

#             async with request_context_factory(
#                 assertions=assertions,
#                 current_user_id=user_id1,
#             ):
#                 session_id = get_current_session().session_id
#                 _prev_secret = get_current_session().session_secret
#                 _prev_token = get_request_context().new_session_token

#                 await set_current_user_id(user_id2)

#                 # Verify both the session in the request context
#                 # and the one stored in the database.

#                 ctx_session = get_current_session()
#                 db_session = await get_session(session_id)

#                 for session in (ctx_session, db_session):
#                     assert session.session_id == session_id
#                     assert session.session_secret != _prev_secret  # rotated
#                     assert session.current_user_id == UserID(user_id2)  # updated

#                 assert ctx_session.session_secret == db_session.session_secret
#                 _new_secret = db_session.session_secret

#                 # Make sure a new session token has been generated
#                 _new_token = get_request_context().new_session_token
#                 assert _new_token is not None
#                 assert _new_token != _prev_token

#                 # Make sure the new token matches the secret
#                 assert _token_matches_secret(_new_token, _new_secret)

#         async def test_attempt_to_set_current_user_id_to_invalid_id(
#             self, request_context_factory
#         ):
#             user_id = UserID(uuid.UUID("4e81dca7-4888-4fad-b056-e767acda47c3"))
#             assertions = [
#                 Assertion.from_params(EmailAuth("u1@example.com")),
#             ]

#             async with request_context_factory(
#                 assertions=assertions, current_user_id=user_id
#             ):
#                 session_id = get_current_session().session_id
#                 _prev_secret = get_current_session().session_secret

#                 assert get_current_session().current_user_id == user_id

#                 with pytest.raises(AuthorizationError):
#                     # This fails. Session is not updated.
#                     await set_current_user_id(
#                         UserID(uuid.UUID("99999999-9999-4999-9999-999999999999"))
#                     )

#                 # Verify both the session in the request context
#                 # and the one stored in the database.

#                 ctx_session = get_current_session()
#                 db_session = await get_session(session_id)

#                 for session in (ctx_session, db_session):
#                     assert session.session_id == session_id
#                     assert session.session_secret == _prev_secret  # NOT rotated
#                     assert session.current_user_id == user_id  # NOT updated

#                 assert ctx_session.session_secret == db_session.session_secret

#                 # Make sure a new session token has NOT been generated
#                 assert get_request_context().new_session_token is None

#         async def test_unset_current_user_id(self, request_context_factory):
#             user_id = UserID(uuid.UUID("4e81dca7-4888-4fad-b056-e767acda47c3"))
#             assertions = [
#                 Assertion.from_params(EmailAuth("u1@example.com", user_id=user_id)),
#             ]

#             async with request_context_factory(
#                 assertions=assertions, current_user_id=user_id
#             ):
#                 session_id = get_current_session().session_id
#                 _prev_secret = get_current_session().session_secret
#                 _prev_token = get_request_context().new_session_token

#                 await unset_current_user_id()

#                 # Verify both the session in the request context
#                 # and the one stored in the database.

#                 ctx_session = get_current_session()
#                 db_session = await get_session(session_id)

#                 for session in (ctx_session, db_session):
#                     assert session.session_id == session_id
#                     assert session.session_secret != _prev_secret  # rotated
#                     assert session.current_user_id is None

#                 assert ctx_session.session_secret == db_session.session_secret
#                 _new_secret = db_session.session_secret

#                 # Make sure a new session token has been generated
#                 _new_token = get_request_context().new_session_token
#                 assert _new_token is not None
#                 assert _new_token != _prev_token

#                 # Make sure the new token matches the secret
#                 assert _token_matches_secret(_new_token, _new_secret)


# Helper functions ---------------------------------------------------


def _token_matches_secret(token: SessionToken, secret: HashedSessionSecret) -> bool:
    hashed = hash_session_secret(parse_session_token(token).session_secret)
    return hashed == secret
