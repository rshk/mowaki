import os

import pytest_asyncio
from sqlalchemy.engine import make_url

from app.config import get_config
from app.repo._schema import metadata
from mowaki.lib.database import create_database, create_engine, drop_database


@pytest_asyncio.fixture(scope="session")
async def database():
    """
    Create the testing database
    """

    cfg = get_config()
    db_url = make_url(cfg.database_url)
    db_name = db_url.database

    try:
        db_admin_url = os.environ["TEST_DATABASE_ADMIN_URL"]
    except KeyError:
        raise ValueError(
            "Configuration error: please supply a valid TEST_DATABASE_ADMIN_URL"
        )

    await create_database(db_admin_url, db_name)

    yield

    await drop_database(db_admin_url, db_name)


@pytest_asyncio.fixture()
async def database_schema(database):
    # The database fixture is required as a dependency but not currently used

    cfg = get_config()
    engine = create_engine(cfg.database_url, isolation_level="AUTOCOMMIT")

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
