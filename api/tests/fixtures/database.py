import os

import pytest_asyncio
from app.lib.database.utils import DbOps, create_async_engine
from app.repo._schema import metadata
from sqlalchemy import URL
from sqlalchemy.engine import make_url

from .config import TestingConfig


@pytest_asyncio.fixture(scope="session")
async def database_url(testing_config: TestingConfig) -> URL:
    role_name = "test_user_{}".format(os.urandom(8).hex())
    password = os.urandom(8).hex()
    db_name = "test_database_{}".format(os.urandom(8).hex())

    # pydantic.PostgresDsn is wonky, use more reliable parsing
    admin_url = make_url(str(testing_config.admin_database_url))

    return URL.create(
        drivername="postgresql+asyncio",
        username=role_name,
        password=password,
        host=admin_url.host,
        port=admin_url.port,
        database=db_name,
    )


@pytest_asyncio.fixture(scope="session")
async def database(testing_config: TestingConfig, database_url: URL):
    """
    Setup (and teardown) a database for testing.
    """

    assert database_url.database is not None
    assert database_url.username is not None
    assert database_url.password is not None

    dbops = DbOps(str(testing_config.admin_database_url))
    await dbops.create_role(database_url.username, password=database_url.password)
    await dbops.create_database(database_url.database, owner=database_url.username)

    yield

    await dbops.drop_database(database_url.database)
    await dbops.drop_role(database_url.username)


@pytest_asyncio.fixture()
async def database_schema(database_url, database):
    """
    Ficture to actually create and drop the database schema
    """

    engine = create_async_engine(database_url, isolation_level="AUTOCOMMIT")

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
