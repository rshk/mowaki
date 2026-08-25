import uuid
from datetime import UTC, datetime

import pytest

from app import repo
from app.core.authn.session import format_session_token, parse_session_token
from app.exceptions import ObjectNotFound
from app.repo.auth.session import hash_session_secret
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


async def test_rotate_secret(subtests):
    session_id, original_secret = await repo.auth.session.create()
    session1 = await repo.auth.session.get(session_id)

    async with repo.auth.session.for_update(session_id) as upd:
        new_secret = await upd.rotate_secret()

    session2 = await repo.auth.session.get(session_id)

    assert session1.session_secret != session2.session_secret
    assert original_secret != new_secret
    assert session1.session_secret == hash_session_secret(original_secret)
    assert session2.session_secret == hash_session_secret(new_secret)


async def test_edit_metadata(subtests):
    session_id, _ = await repo.auth.session.create()
    session = await repo.auth.session.get(session_id)

    assert session.metadata.ip_address is None
    assert session.metadata.user_agent is None
    assert session.metadata.device_id is None

    with subtests.test("Set initial metadata"):
        async with (
            repo.auth.session.for_update(session_id) as upd,
            upd.edit_metadata() as metadata,
        ):
            metadata.ip_address = "1.2.3.4"
            metadata.user_agent = "Mozilla/5.0"

        session = await repo.auth.session.get(session_id)
        assert session.metadata.ip_address == "1.2.3.4"
        assert session.metadata.user_agent == "Mozilla/5.0"
        assert session.metadata.device_id is None

    with subtests.test("Partial update metadata"):
        async with (
            repo.auth.session.for_update(session_id) as upd,
            upd.edit_metadata() as metadata,
        ):
            metadata.user_agent = "Mozilla/6.0"  # lol
            metadata.device_id = "62478520-203d-406d-b959-cad7c20eb4a8"

        session = await repo.auth.session.get(session_id)
        assert session.metadata.ip_address == "1.2.3.4"
        assert session.metadata.user_agent == "Mozilla/6.0"
        assert session.metadata.device_id == "62478520-203d-406d-b959-cad7c20eb4a8"


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


async def test_remove_assertion():
    session_id, _ = await repo.auth.session.create()
    async with repo.auth.session.for_update(session_id) as upd:
        await upd.add_assertion(
            Assertion.from_params(EmailAuth(email_address="foo@example.com"))
        )

    async with repo.auth.session.for_update(session_id) as upd:
        [assertion] = (await upd.get()).assertions
        await upd.remove_assertion(assertion.id)

    session = await repo.auth.session.get(session_id)
    assert session.assertions == []


async def test_manipulate_current_user_id(subtests):

    session_id, _ = await repo.auth.session.create()

    with subtests.test("Set current_user_id"):
        user_id = UserID(uuid.UUID("0c2c6ffc-0d94-4173-b02a-46fb0c204dd0"))

        async with repo.auth.session.for_update(session_id) as upd:
            await upd.set_current_user_id(user_id)

        session = await repo.auth.session.get(session_id)
        assert session.current_user_id == user_id

    with subtests.test("Update current_user_id"):
        user_id = UserID(uuid.UUID("713e0853-c645-42a2-a93f-bf308123ccd2"))

        async with repo.auth.session.for_update(session_id) as upd:
            await upd.set_current_user_id(user_id)

        session = await repo.auth.session.get(session_id)
        assert session.current_user_id == user_id

    with subtests.test("Unset current_user_id"):
        async with repo.auth.session.for_update(session_id) as upd:
            await upd.unset_current_user_id()

        session = await repo.auth.session.get(session_id)
        assert session.current_user_id is None


async def test_delete_session():
    session_id, _ = await repo.auth.session.create()
    await repo.auth.session.delete(session_id)

    with pytest.raises(ObjectNotFound):
        await repo.auth.session.get(session_id)
