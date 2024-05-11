from typing import Any

from app.models.user import User, UserID
from app.repo._schema import UsersTable
from app.resources import get_resources
from mowaki.lib.crypto import create_encrypted_password


async def create_user(email, password=None) -> UserID:
    enc_password = create_encrypted_password(password) if password is not None else None
    query = UsersTable.insert().values(email=email, password=enc_password)

    db = get_resources().database
    async with db.begin() as conn:
        result = await conn.execute(query)
    [pk] = result.inserted_primary_key
    return pk


async def set_user_password(id: UserID, password: str):
    enc_password = create_encrypted_password(password) if password is not None else None
    query = (
        UsersTable.update().where(UsersTable.c.id == id).values(password=enc_password)
    )

    db = get_resources().database
    async with db.begin() as conn:
        await conn.execute(query)


async def list_users() -> list[User]:
    query = UsersTable.select()
    db = get_resources().database
    async with db.begin() as conn:
        result = await conn.execute(query)
    return [_user_from_row(row) for row in result.fetchall()]


async def get_user_by_id(id: UserID) -> User:
    query = UsersTable.select().filter_by(id=id)
    db = get_resources().database
    async with db.begin() as conn:
        result = await conn.execute(query)
    row = result.fetchone()
    if row is None:
        return None
    return _user_from_row(row)


async def get_user_by_email(email: str) -> User:
    query = UsersTable.select().filter_by(email=email)
    db = get_resources().database
    async with db.begin() as conn:
        result = await conn.execute(query)
    row = result.fetchone()
    if row is None:
        return None
    return _user_from_row(row)


async def delete_user(id: UserID):
    query = UsersTable.delete().filter_by(id=id)
    db = get_resources().database
    async with db.begin() as conn:
        await conn.execute(query)


def _user_from_row(row: Any) -> User:
    return User(
        id=row.id,
        email=row.email,
        date_created=row.date_created,
    )
