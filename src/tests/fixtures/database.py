import asyncio

import pytest
import pytest_asyncio
from sqlalchemy import NullPool, make_url

from app.config import Config
from app.lib.sql.utils import DbOps, create_async_engine
from app.repo._schema import metadata

from .config import TestingConfig


@pytest.fixture(scope="session")
def database(testing_config: TestingConfig, config: Config):
    """
    Create (and drop) a new database for testing.

    Also creates a new (unprivileged) role to use for connecting to
    the newly created database.
    """

    dburl = make_url(str(config.database_url))
    dbops = DbOps(str(testing_config.admin_database_url))

    async def setup_db():
        assert dburl.database is not None
        assert dburl.username is not None

        await dbops.create_role(dburl.username, password=dburl.password)
        await dbops.create_database(dburl.database, owner=dburl.username)

    async def teardown_db():
        assert dburl.database is not None
        assert dburl.username is not None

        await dbops.drop_database(dburl.database)
        await dbops.drop_role(dburl.username)

    asyncio.run(setup_db())
    yield dburl
    asyncio.run(teardown_db())


async def setup_and_teardown_database(database_url: str, admin_database_url: str):
    dburl = make_url(database_url)

    assert dburl.database is not None
    assert dburl.username is not None
    assert dburl.password is not None

    dbops = DbOps(admin_database_url)
    await dbops.create_role(dburl.username, password=dburl.password)
    await dbops.create_database(dburl.database, owner=dburl.username)

    yield dburl

    await dbops.drop_database(dburl.database)
    await dbops.drop_role(dburl.username)


@pytest_asyncio.fixture()
async def database_schema(database, resources):
    """
    Ficture to actually create and drop the database schema
    before/after each test execution.
    """

    if resources:
        pass  # Make linter happy; only need resources as a dependency

    database_url = database
    engine = create_async_engine(
        database_url,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
