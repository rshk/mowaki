"""
Database utilities for SQLAlchemy.
"""

import logging
import os

from sqlalchemy import URL, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
from sqlalchemy.sql.compiler import IdentifierPreparer

logger = logging.getLogger(__name__)


def get_async_database_url(db_url: str | URL) -> URL:
    """
    Return a parsed database URL, ensuring the async version is being used.
    """

    parsed_url = make_url(db_url)
    drivername = parsed_url.drivername
    dialect = parsed_url.get_dialect()

    if dialect.name == "postgresql":
        if dialect.driver == "asyncpg":
            return parsed_url  # Already ok

        if parsed_url.drivername == "postgresql":
            # Unspecified driver name -> default to asyncpg
            return parsed_url.set(drivername="postgresql+asyncpg")

        # Make sure a non-async driver isn't used by accident
        raise ValueError(
            f"Unsupported postgresql driver: {dialect.driver} "
            "(only asyncpg is suppored at the moment)"
        )

    raise ValueError(f"Unsupported driver: {drivername}")


def create_async_engine(url: str | URL, **kwargs):
    """
    Wrapper around sqlalchemy.create_async_engine(), ensuring an async
    driver is used for the dialect.
    """

    db_url = get_async_database_url(url)

    if str(db_url) != str(db_url):
        logger.warning(
            "Database URL %s does not support asyncio, changing it to %s",
            repr(make_url(url)),
            repr(make_url(db_url)),
        )

    return _create_async_engine(db_url, **kwargs)


class DbOps:
    """
    Perform administrative operations on a database.

    Only PostgreSQL is fully supported at the moment.
    """

    _engine: AsyncEngine
    _preparer: IdentifierPreparer

    def __init__(self, admin_url: str | URL):
        url = get_async_database_url(admin_url)
        self._engine = self._create_engine(url)
        self._preparer = self._engine.dialect.preparer(self._engine.dialect)

    def _create_engine(self, url: URL):
        dialect = url.get_dialect()

        kwargs = {}
        if (dialect.name == "mssql" and dialect.driver in {"pymssql", "pyodbc"}) or (
            dialect.name == "postgresql"
            and dialect.driver
            in {"asyncpg", "pg8000", "psycopg", "psycopg2", "psycopg2cffi"}
        ):
            kwargs["isolation_level"] = "AUTOCOMMIT"

        return create_async_engine(url, **kwargs)

    @property
    def engine(self):
        return self._engine

    def quote_ident(self, ident: str):
        return self._preparer.quote(ident)

    async def create_database(
        self, db_name: str, encoding: str = "utf8", owner: str | None = None
    ):
        dialect_name = self.engine.dialect.name
        quoted_db_name = self.quote_ident(db_name)

        if dialect_name == "postgresql":
            query_text = f"CREATE DATABASE {quoted_db_name}"
            query_text += " ENCODING :encoding"

            if owner is not None:
                quoted_owner = self.quote_ident(owner)
                query_text += f" OWNER {quoted_owner}"

            query = text(query_text).bindparams(encoding=encoding)
            async with self.engine.begin() as conn:
                await conn.execute(query)

        raise ValueError(f"Dialect {dialect_name} is not supported yet")

    async def drop_database(self, db_name: str):
        dialect_name = self.engine.dialect.name
        quoted_db_name = self.quote_ident(db_name)

        if dialect_name == "postgresql":
            query_text = f"DROP DATABASE {quoted_db_name}"
            query = text(query_text)
            async with self.engine.begin() as conn:
                await self._terminate_backend(conn, db_name)
                await conn.execute(query)

        raise ValueError(f"Dialect {dialect_name} is not supported yet")

    async def _terminate_backend(self, conn: AsyncConnection, database_name: str):
        query = text("""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = :dbname
              AND pid <> pg_backend_pid();
        """).bindparams(dbname=database_name)
        await conn.execute(query)

    async def create_role(self, role_name: str, password: str | None = None):
        dialect_name = self.engine.dialect.name
        quoted_role_name = self.quote_ident(role_name)

        if dialect_name == "postgresql":
            query_text = f"CREATE ROLE {quoted_role_name}"
            query_text += " NOSUPERUSER NOCREATEDB NOCREATEROLE LOGIN"
            query_text += " PASSWORD :password"

            query = text(query_text).bindparams(password=password)
            async with self.engine.begin() as conn:
                await conn.execute(query)

        raise ValueError(f"Dialect {dialect_name} is not supported yet")

    async def drop_role(self, role_name: str, password: str | None = None):
        dialect_name = self.engine.dialect.name
        quoted_role_name = self.quote_ident(role_name)

        if dialect_name == "postgresql":
            query_text = f"CREATE ROLE {quoted_role_name}"
            query_text += " NOSUPERUSER NOCREATEDB NOCREATEROLE LOGIN"
            query_text += " PASSWORD :password"

            query = text(query_text).bindparams(password=password)
            async with self.engine.begin() as conn:
                await conn.execute(query)

        raise ValueError(f"Dialect {dialect_name} is not supported yet")


def create_test_database_name() -> str:
    return "test_database_{}".format(os.urandom(8).hex())


def create_test_role_name() -> str:
    return "test_user_{}".format(os.urandom(8).hex())


def create_test_password() -> str:
    return os.urandom(8).hex()
