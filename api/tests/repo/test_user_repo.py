import pytest
from app import repo

pytestmark = [
    pytest.mark.usefixtures("database_schema"),
]


async def test_create_and_retrieve_user(subtests):
    with subtests.test("create user"):
        user = await repo.user.create("user@example.com")
    pass
