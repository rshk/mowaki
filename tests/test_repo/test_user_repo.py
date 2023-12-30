import pytest

import app.repo.users as user_repo

pytestmark = [
    pytest.mark.usefixtures("setup_resources_context", "database", "database_schema")
]


@pytest.mark.asyncio
async def test_create_and_retrieve_user():
    user_id = await user_repo.create_user(email="user@example.com")
    user = await user_repo.get_user_by_id(user_id)

    assert user.id == user_id
    assert user.email == "user@example.com"


@pytest.mark.asyncio
async def test_list_users_returns_empty_list_if_db_empty():
    users = await user_repo.list_users()
    assert users == []


@pytest.mark.asyncio
async def test_create_and_list_users():
    user_id = await user_repo.create_user(email="user@example.com")
    users = await user_repo.list_users()

    assert len(users) == 1

    [user] = users

    assert user.id == user_id
    assert user.email == "user@example.com"
