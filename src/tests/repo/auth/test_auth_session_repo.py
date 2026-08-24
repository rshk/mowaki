import uuid
from datetime import UTC, datetime

import pytest

from app import repo
from app.core.authn.session import format_session_token, parse_session_token
from app.types.auth.assertions import Assertion, EmailAuth, PasskeyAuth
from app.types.auth.passkey_data import PasskeyID
from app.types.user import UserID

pytestmark = [
    pytest.mark.usefixtures("database_schema"),
    pytest.mark.asyncio,
]


async def test_create_and_retrieve_session(subtests):
    with subtests.test("create session"):
        session_id, _ = await repo.auth.session.create()

    with subtests.test("retrieve session"):
        session = await repo.auth.session.get(session_id)
        assert session.session_id == session_id


async def test_create_and_retrieve_session_by_token():
    session_id, secret = await repo.auth.session.create()

    token = format_session_token(session_id, secret)
    token_data = parse_session_token(token)
    session = await repo.auth.session.get_for_token(token_data)

    assert session.session_id == session_id


async def test_created_at_is_set_correctly(freeze_time):
    with freeze_time("2026-08-01"):
        session_id, _ = await repo.auth.session.create()
    session = await repo.auth.session.get(session_id)
    assert session.created_at == datetime(2026, 8, 1, 0, 0, tzinfo=UTC)


async def test_set_last_used_at(subtests, freeze_time):
    with freeze_time("2026-08-01"):
        session_id, _ = await repo.auth.session.create()

    session = await repo.auth.session.get(session_id)
    assert session.last_used_at is None

    with subtests.test("Set to current time (default)"):
        with freeze_time("2026-08-05"):
            await repo.auth.session.set_last_used_at(session_id)

        session = await repo.auth.session.get(session_id)
        assert session.last_used_at == datetime(2026, 8, 5, 0, 0, tzinfo=UTC)

    with subtests.test("Set to custom time"):
        with freeze_time("2026-08-08"):
            await repo.auth.session.set_last_used_at(
                session_id, datetime(2026, 8, 7, 0, 0, tzinfo=UTC)
            )

        session = await repo.auth.session.get(session_id)
        assert session.last_used_at == datetime(2026, 8, 7, 0, 0, tzinfo=UTC)


async def test_edit_set_last_used_at(subtests, freeze_time):
    with freeze_time("2026-08-01"):
        session_id, _ = await repo.auth.session.create()

    session = await repo.auth.session.get(session_id)
    assert session.last_used_at is None

    with subtests.test("Set to current time (default)"):
        with freeze_time("2026-08-05"):
            async with repo.auth.session.for_update(session_id) as upd:
                await upd.set_last_used_at()

        session = await repo.auth.session.get(session_id)
        assert session.last_used_at == datetime(2026, 8, 5, 0, 0, tzinfo=UTC)

    with subtests.test("Set to custom time"):
        with freeze_time("2026-08-08"):
            async with repo.auth.session.for_update(session_id) as upd:
                await upd.set_last_used_at(datetime(2026, 8, 7, 0, 0, tzinfo=UTC))

        session = await repo.auth.session.get(session_id)
        assert session.last_used_at == datetime(2026, 8, 7, 0, 0, tzinfo=UTC)


async def test_add_assertion(freeze_time, subtests):
    session_id, _ = await repo.auth.session.create()

    session = await repo.auth.session.get(session_id)
    assert session.assertions == []

    with subtests.test("Add first assertion"):
        with freeze_time("2026-08-15"):
            new_assertion = Assertion.from_params(
                EmailAuth(email_address="user@example.com")
            )

        async with repo.auth.session.for_update(session_id) as upd:
            await upd.add_assertion(new_assertion)

        session = await repo.auth.session.get(session_id)
        assert len(session.assertions) == 1

        [assertion] = session.assertions
        assert assertion.id == new_assertion.id
        assert assertion.created_at == datetime(2026, 8, 15, 0, 0, tzinfo=UTC)
        assert isinstance(assertion.params, EmailAuth)
        assert assertion.expires_at is None
        assert assertion.params.email_address == "user@example.com"

    with subtests.test("Add second assertion"):
        # Add another one
        new_assertion = Assertion.from_params(
            PasskeyAuth(
                passkey_id=PasskeyID(uuid.UUID("b59ea115-92e3-4748-b52b-aedcbc8dca8b")),
                user_id=UserID(uuid.UUID("c5664eed-6066-4e03-8af0-20a081ee8abd")),
            )
        )

        async with repo.auth.session.for_update(session_id) as upd:
            await upd.add_assertion(new_assertion)

        session = await repo.auth.session.get(session_id)
        assert len(session.assertions) == 2


async def test_set_assertions():
    session_id, _ = await repo.auth.session.create()

    async with repo.auth.session.for_update(session_id) as upd:
        await upd.add_assertion(
            Assertion.from_params(EmailAuth(email_address="foo@example.com"))
        )
        await upd.add_assertion(
            Assertion.from_params(EmailAuth(email_address="bar@example.com"))
        )

    session = await repo.auth.session.get(session_id)
    assert len(session.assertions) == 2

    async with repo.auth.session.for_update(session_id) as upd:
        await upd.set_assertions(
            [Assertion.from_params(EmailAuth(email_address="bar@example.com"))]
        )

    session = await repo.auth.session.get(session_id)
    assert len(session.assertions) == 1
    [assertion] = session.assertions
    assert isinstance(assertion.params, EmailAuth)
    assert assertion.params.email_address == "bar@example.com"
