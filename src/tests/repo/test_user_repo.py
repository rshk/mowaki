import uuid

import pytest

from app import repo
from app.exceptions import ObjectNotFound
from app.lib.keygen import generate_uuid
from app.types.user import UserID, UserMetadata

pytestmark = [
    pytest.mark.usefixtures("database_schema"),
    # pytest.mark.asyncio(loop_scope="session"),
]


@pytest.mark.asyncio()
async def test_create_and_retrieve_user(subtests):
    with subtests.test("create user"):
        user_id = await repo.user.create("user@example.com")
        assert isinstance(user_id, uuid.UUID)

    with subtests.test("retrieve user"):
        user = await repo.user.get(user_id)
        assert user.id == user_id
        assert user.email == "user@example.com"
        assert user.metadata == UserMetadata()
        assert user.is_active is True

    with subtests.test("get user by email"):
        user = await repo.user.get_by_email("user@example.com")
        assert user.id == user_id


@pytest.mark.asyncio()
async def test_get_nonexisting_user():
    with pytest.raises(ObjectNotFound):
        await repo.user.get(UserID(generate_uuid()))


@pytest.mark.asyncio()
async def test_email_is_normalized_on_creation():
    user_id = await repo.user.create("user@EXAMPLE.COM")
    user = await repo.user.get(user_id)
    assert user.email == "user@example.com"


@pytest.mark.asyncio()
async def test_email_is_normalized_for_retrieval():
    user_id = await repo.user.create("user@example.com")
    user = await repo.user.get_by_email("user@EXAMPLE.COM")
    assert user.id == user_id


@pytest.mark.asyncio()
async def test_update_user_metadata():
    user_id = await repo.user.create("user@example.com")
    async with repo.user.edit_metadata(user_id) as metadata:
        metadata.display_name = "Some user"
        metadata.bio = "User's biography goes here"

    user = await repo.user.get(user_id)
    assert user.metadata.display_name == "Some user"
    assert user.metadata.bio == "User's biography goes here"


@pytest.mark.asyncio()
async def test_activate_and_deactivate_user(subtests):
    user_id = await repo.user.create("user@example.com")

    user = await repo.user.get(user_id)
    assert user.is_active is True

    with subtests.test("deactivate and check"):
        await repo.user.deactivate(user_id)
        user = await repo.user.get(user_id)
        assert user.is_active is False

    with subtests.test("reactivate and check"):
        await repo.user.reactivate(user_id)
        user = await repo.user.get(user_id)
        assert user.is_active is True
