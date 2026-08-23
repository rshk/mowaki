from datetime import UTC, datetime

import pytest
from app import repo
from app.core.authn.session import format_session_token, parse_session_token
from freezegun import freeze_time

from app.types.auth.assertions import Assertion, EmailAuth

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


async def test_create_and_retrieve_session_by_token(subtests):
    session_id, secret = await repo.auth.session.create()

    token = format_session_token(session_id, secret)
    token_data = parse_session_token(token)
    session = await repo.auth.session.get_for_token(token_data)

    assert session.session_id == session_id


async def test_created_at_is_set_correctly():
    with freeze_time("2026-08-01"):
        session_id, _ = await repo.auth.session.create()
    session = await repo.auth.session.get(session_id)
    assert session.created_at == datetime(2026, 8, 1, 0, 0, tzinfo=UTC)


async def test_set_last_used_at(subtests):
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


async def test_add_assertion():
    session_id, _ = await repo.auth.session.create()

    session = await repo.auth.session.get(session_id)
    assert session.assertions == []

    new_assertion = Assertion.from_params(EmailAuth(email_address="user@example.com"))

    async with repo.auth.session.for_update(session_id) as upd:
        await upd.add_assertion(new_assertion)
