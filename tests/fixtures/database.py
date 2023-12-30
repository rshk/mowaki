import asyncio
import os

import pytest
import pytest_asyncio
from sqlalchemy.engine import make_url

from app.config import get_config
from app.io.database.schema import metadata
from app.lib.database import create_database, create_engine, drop_database


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

    # asyncio.run(create_database(db_admin_url, db_name))
    await create_database(db_admin_url, db_name)

    yield

    # asyncio.run(drop_database(db_admin_url, db_name))
    await drop_database(db_admin_url, db_name)


@pytest_asyncio.fixture()
async def database_schema(database):
    cfg = get_config()
    engine = create_engine(cfg.database_url, isolation_level="AUTOCOMMIT")

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
