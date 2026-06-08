import pytest
from app import repo
from app.types.user import UserMetadata

pytestmark = [
    pytest.mark.usefixtures("database_schema"),
]


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
