from uuid import UUID

import pytest
import pytest_asyncio
from app import repo
from app.core.authn.session import (
    add_session_assertion,
    create_session,
    edit_session_metadata,
    get_current_session,
    get_session,
    invalidate_current_session,
    parse_session_token,
    rotate_current_session_secret,
    set_current_user_id,
    unset_current_user_id,
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
from app.types.user import UserID

from tests.utils.session import TestingRequestContextManager

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.usefixtures("database_schema", "request_ctx"),
]


# --------------------------------------------------------------------
# Tests for get_current_session()
# --------------------------------------------------------------------


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


# --------------------------------------------------------------------
# Tests for invalidate_current_session()
# --------------------------------------------------------------------


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


# --------------------------------------------------------------------
# Tests for rotate_current_session_secret()
# --------------------------------------------------------------------


async def test_rotate_current_session_secret(subtests: pytest.Subtests):
    session = get_current_session()
    session_id = session.session_id

    await rotate_current_session_secret()

    ctx = get_request_context()
    session_ctx = ctx.auth_session

    with subtests.test("Session has been updated in context"):
        # Session ID is unchanged
        assert session_ctx.session_id == session.session_id

        # New token has been added to the context
        assert ctx.new_session_token is not None
        token_info = parse_session_token(ctx.new_session_token)
        assert token_info.session_id == session_id

        # New secret hash is different from the old one
        assert session_ctx.session_secret != session.session_secret

    with subtests.test("Session has been updated in the database"):
        session_db = await get_session(session.session_id)
        assert session_db.session_id == session_id
        assert session_db.session_secret == session_ctx.session_secret
        assert session_db.session_secret != session.session_secret


# --------------------------------------------------------------------
# Tests for add_session_assertion()
# --------------------------------------------------------------------


class Test_add_assertion_to_blank_session:
    async def test_add_assertion(self, subtests):
        session = get_current_session()
        assert session.assertions == []

        await add_session_assertion(assertions.EmailAuth("user@example.com"))

        with subtests.test("Session has been updated in context"):
            session_ctx = get_current_session()
            assert len(session_ctx.assertions) == 1
            assert session_ctx.assertions[0].params == assertions.EmailAuth(
                "user@example.com"
            )

        with subtests.test("Session has been updated in the database"):
            session_db = await get_session(session.session_id)
            assert len(session_db.assertions) == 1
            assert session_db.assertions[0].params == assertions.EmailAuth(
                "user@example.com"
            )

    async def test_add_multiple_assertions(self, subtests):
        session = get_current_session()
        assert session.assertions == []

        await add_session_assertion(assertions.EmailAuth("user@example.com"))
        await add_session_assertion(assertions.EmailAuth("different@example.com"))

        with subtests.test("Session has been updated in context"):
            session_ctx = get_current_session()
            assert len(session_ctx.assertions) == 2
            assert session_ctx.assertions[0].params == assertions.EmailAuth(
                "user@example.com"
            )
            assert session_ctx.assertions[1].params == assertions.EmailAuth(
                "different@example.com"
            )

        with subtests.test("Session has been updated in the database"):
            session_db = await get_session(session.session_id)
            assert len(session_db.assertions) == 2
            assert session_db.assertions[0].params == assertions.EmailAuth(
                "user@example.com"
            )
            assert session_db.assertions[1].params == assertions.EmailAuth(
                "different@example.com"
            )


# --------------------------------------------------------------------
# Tests for (un)set_current_user_id()
# --------------------------------------------------------------------


class Test_set_and_unset_user_id_from_empty:
    async def test_set_current_user_id(self, subtests):
        session = get_current_session()
        assert session.current_user_id is None

        user_id = UserID(UUID("01a1ff5c-970c-7227-a8b6-dfceb025444e"))
        await set_current_user_id(user_id)

        with subtests.test("Session has been updated in context"):
            session_ctx = get_current_session()
            assert session_ctx.current_user_id == user_id

        with subtests.test("Session has been updated in the database"):
            session_db = await get_session(session.session_id)
            assert session_db.current_user_id == user_id

    async def test_unset_current_user_id(self, subtests):
        session = get_current_session()
        assert session.current_user_id is None

        await unset_current_user_id()

        with subtests.test("Session has been updated in context"):
            session_ctx = get_current_session()
            assert session_ctx.current_user_id is None

        with subtests.test("Session has been updated in the database"):
            session_db = await get_session(session.session_id)
            assert session_db.current_user_id is None


class Test_set_and_unset_user_id_from_existing:
    @pytest_asyncio.fixture
    async def request_ctx_manager(self) -> TestingRequestContextManager:
        return TestingRequestContextManager(
            current_user_id=UserID(UUID("a1b0054e-51fc-4d16-92da-ba7db97c1c90")),
        )

    async def test_set_current_user_id(self, subtests):
        session = get_current_session()
        assert session.current_user_id == UserID(UUID("a1b0054e-51fc-4d16-92da-ba7db97c1c90"))

        user_id = UserID(UUID("01a1ff5c-970c-7227-a8b6-dfceb025444e"))
        await set_current_user_id(user_id)

        with subtests.test("Session has been updated in context"):
            session_ctx = get_current_session()
            assert session_ctx.current_user_id == user_id

        with subtests.test("Session has been updated in the database"):
            session_db = await get_session(session.session_id)
            assert session_db.current_user_id == user_id

    async def test_unset_current_user_id(self, subtests):
        session = get_current_session()
        assert session.current_user_id == UserID(UUID("a1b0054e-51fc-4d16-92da-ba7db97c1c90"))

        await unset_current_user_id()

        with subtests.test("Session has been updated in context"):
            session_ctx = get_current_session()
            assert session_ctx.current_user_id is None

        with subtests.test("Session has been updated in the database"):
            session_db = await get_session(session.session_id)
            assert session_db.current_user_id is None


# --------------------------------------------------------------------
# Tests for unset_current_user_id()
# --------------------------------------------------------------------


# --------------------------------------------------------------------
# Tests for edit_session_metadata()
# --------------------------------------------------------------------


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

        with subtests.test("Session has been updated in the database"):
            session_db = await get_session(session.session_id)
            assert session_db.session_id == session.session_id
            assert session_db.session_secret == session.session_secret
            assert session_db.metadata.user_agent == "NewUserAgent/1.0"
            assert session_db.metadata.ip_address == "3.3.3.3"


# --------------------------------------------------------------------
# Secret rotation
# --------------------------------------------------------------------


class Test_secret_rotation:
    async def test_rotate_current_session_secret(self):
        ctx = get_request_context()
        assert ctx.new_session_token is None

        await rotate_current_session_secret()

        assert ctx.new_session_token is not None  # rotated

    async def test_add_session_assertion(self):
        ctx = get_request_context()
        assert ctx.new_session_token is None

        await add_session_assertion(assertions.EmailAuth("user@example.com"))

        assert ctx.new_session_token is not None  # rotated

    async def test_set_current_user_id(self):
        ctx = get_request_context()
        assert ctx.new_session_token is None

        await set_current_user_id(UserID(UUID("01a1ff5c-970c-7227-a8b6-dfceb025444e")))

        assert ctx.new_session_token is not None  # rotated

    async def test_unset_current_user_id(self):
        ctx = get_request_context()
        assert ctx.new_session_token is None

        await unset_current_user_id()

        assert ctx.new_session_token is not None  # rotated

    async def test_add_session_assertion_twice(self):
        ctx = get_request_context()
        assert ctx.new_session_token is None

        await add_session_assertion(assertions.EmailAuth("user@example.com"))

        assert ctx.new_session_token is not None  # rotated
        first_new_token = ctx.new_session_token

        await add_session_assertion(assertions.EmailAuth("different@example.com"))

        assert ctx.new_session_token == first_new_token  # unchanged

    async def test_add_session_assertion_then_set_current_user_id(self):
        ctx = get_request_context()
        assert ctx.new_session_token is None

        await add_session_assertion(assertions.EmailAuth("user@example.com"))

        assert ctx.new_session_token is not None  # rotated
        first_new_token = ctx.new_session_token

        await set_current_user_id(UserID(UUID("01a1ff5c-970c-7227-a8b6-dfceb025444e")))

        assert ctx.new_session_token == first_new_token  # unchanged


class Test_secret_rotation_only_happens_once_per_request:
    @pytest_asyncio.fixture
    async def request_ctx_manager(self) -> TestingRequestContextManager:
        return TestingRequestContextManager(new_session_token=True)

    async def test_rotate_current_session_secret(self):
        ctx = get_request_context()
        assert ctx.new_session_token is not None
        new_token = ctx.new_session_token

        await rotate_current_session_secret()

        assert ctx.new_session_token == new_token  # unchanged

    async def test_add_session_assertion(self):
        ctx = get_request_context()
        assert ctx.new_session_token is not None
        new_token = ctx.new_session_token

        await add_session_assertion(assertions.EmailAuth("user@example.com"))

        assert ctx.new_session_token == new_token  # unchanged

    async def test_set_current_user_id(self):
        ctx = get_request_context()
        assert ctx.new_session_token is not None
        new_token = ctx.new_session_token

        await set_current_user_id(UserID(UUID("01a1ff5c-970c-7227-a8b6-dfceb025444e")))

        assert ctx.new_session_token == new_token  # unchanged

    async def test_unset_current_user_id(self):
        ctx = get_request_context()
        assert ctx.new_session_token is not None
        new_token = ctx.new_session_token

        await unset_current_user_id()

        assert ctx.new_session_token == new_token  # unchanged
