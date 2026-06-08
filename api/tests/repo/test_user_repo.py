import uuid

import pytest
from app import repo
from app.exceptions import ObjectNotFound
from app.types.user import UserID, UserMetadata

pytestmark = [
    pytest.mark.usefixtures("database_schema"),
    # pytest.mark.asyncio(loop_scope="session"),
]


@pytest.mark.asyncio()
async def test_create_and_retrieve_user(subtests):
    with subtests.test("create user"):
        user = await repo.user.create("user@example.com")
        assert user.id is not None
        assert user.email == "user@example.com"
        assert user.metadata == UserMetadata()
        assert user.is_active is True

    with subtests.test("retrieve user"):
        user = await repo.user.get(user.id)
        assert user.id is not None
        assert user.email == "user@example.com"
        assert user.metadata == UserMetadata()
        assert user.is_active is True


@pytest.mark.asyncio()
async def test_get_nonexisting_user():
    with pytest.raises(ObjectNotFound):
        await repo.user.get(UserID(uuid.uuid4()))
