from typing import Annotated

import pytest_asyncio
from app.config import Config
from app.lib.database.utils import DbOps, create_async_engine
from app.repo._schema import metadata
from pytest_annotated import Fixture
from sqlalchemy import URL, make_url

from .config import TestingConfig


@pytest_asyncio.fixture(scope="session")
async def database(testing_config: TestingConfig, config: Config):
    """
    Create (and drop) a new database for testing.

    Also creates a new (unprivileged) role to use for connecting to
    the newly created database.
    """

    database_url = make_url(str(config.database_url))

    assert database_url.database is not None
    assert database_url.username is not None
    assert database_url.password is not None

    dbops = DbOps(str(testing_config.admin_database_url))
    await dbops.create_role(database_url.username, password=database_url.password)
    await dbops.create_database(database_url.database, owner=database_url.username)

    yield database_url

    await dbops.drop_database(database_url.database)
    await dbops.drop_role(database_url.username)


@pytest_asyncio.fixture()
async def database_schema(database_url: Annotated[URL, Fixture(database)]):
    """
    Ficture to actually create and drop the database schema
    before/after each test execution.
    """

    engine = create_async_engine(database_url, isolation_level="AUTOCOMMIT")

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
