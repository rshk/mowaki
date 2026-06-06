"""
Database utilities for SQLAlchemy.
"""

import logging
import os
import re

from sqlalchemy import Connection, text
import sqlalchemy
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine
from sqlalchemy.sql import quoted_name

logger = logging.getLogger(__name__)

re_valid_db_name = re.compile(r"^[a-zA-z0-9_\-]+$")


def get_async_database_url(db_url: str) -> sqlalchemy.URL:
    """
    Return a parsed database URL, ensuring the async version is being used.
    """

    parsed_url = make_url(db_url)
    drivername = parsed_url.drivername

    if drivername in ("postgresql+asyncpg", "postgres+asyncpg"):
        # Already using the async version
        return parsed_url

    if drivername in ("postgresql", "postgres"):
        return parsed_url.set(drivername=f"{drivername}+asyncpg")

    raise ValueError(f"Unsupported driver: {drivername}")


def create_engine(database_url, **kwargs):
    db_url = get_async_database_url(database_url)

    if str(db_url) != str(database_url):
        logger.warning(
            "Database URL %s does not support asyncio, changing it to %s",
            repr(make_url(database_url)),
            repr(make_url(db_url)),
        )

    return create_async_engine(db_url, **kwargs)


def create_test_database_name():
    return "test_database_{}".format(os.urandom(6).hex())


async def create_database(db_url, database_name):
    if not validate_database_name(database_name):
        raise ValueError(f"Invalid database name: {database_name}")

    engine = create_engine(db_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        c = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{database_name}'")
        )
        database_exists = c.scalar() == 1

    if database_exists:
        await drop_database(db_url, database_name)

    async with engine.connect() as conn:
        await conn.execute(text(f'CREATE DATABASE "{database_name}" ENCODING "utf8"'))
    await engine.dispose()


async def drop_database(db_url, database_name):
    if not validate_database_name(database_name):
        raise ValueError(f"Invalid database name: {database_name}")

    engine = create_engine(db_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        await _terminate_backend(conn, database_name)
        await conn.execute(text(f'DROP DATABASE "{database_name}"'))


async def _terminate_backend(conn: AsyncConnection, database_name: str):
    query = text("""
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = :dbname
          AND pid <> pg_backend_pid();
    """).bindparams(dbname=database_name)
    await conn.execute(query)


def validate_database_name(name):
    return bool(re_valid_db_name.match(name))
