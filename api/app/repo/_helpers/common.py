from __future__ import annotations

from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncContextManager,
    AsyncIterator,
    Callable,
    Coroutine,
    Generic,
    Self,
    Type,
    TypeVar,
    reveal_type,
)

import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncTransaction

from app.exceptions import ObjectNotFound
from app.io.resources import get_database
from app.types._protocols import FromRow

T = TypeVar("T", bound=FromRow)

# Callable to update an object
UpdaterFn = Callable[..., Coroutine[Any, Any, sa.CursorResult[Any]]]


class TableCrud(Generic[T]):
    """Helper class for performing basic CRUD operations on a table."""

    __slots__ = ["_table", "_model", "_engine", "_connection"]

    _table: sa.Table
    _model: Type[T]
    _engine: AsyncEngine | None
    _connection: AsyncConnection | None

    def __init__(self, table: sa.Table, model: Type[T]):
        """
        Args:
            table: SQLAlchemy Table to use to perform operations
            model: pydantic model to use for wrapping results
        """
        self._table = table
        self._model = model
        self._engine = None
        self._connection = None

    def bind(
        self,
        conn: AsyncConnection | None = None,
        engine: AsyncEngine | None = None,
    ) -> Self:
        """
        Return a clone of this TableCrud, "bound" to a connection or engine.
        """

        new = self.__class__(table=self._table, model=self._model)

        if conn is not None:
            # Bind to a connection
            new._connection = conn

        else:
            # Bind to an engine
            if engine is None:
                engine = get_database()
            new._engine = engine

        return new

    async def _execute(self, query, *args, **kwargs) -> WrappedResult[T]:
        """Wrapper for AsyncConnection.execute()"""

        async with self._connect() as conn:
            result = await conn.execute(query, *args, **kwargs)
        return self._wrap_result(result)

    def _wrap_result(self, result: sa.CursorResult) -> WrappedResult[T]:
        return WrappedResult[T](self._model, result)

    @asynccontextmanager
    async def _connect(self) -> AsyncIterator[AsyncConnection]:
        @asynccontextmanager
        async def _connect_from_connection(conn: AsyncConnection):
            yield conn

        @asynccontextmanager
        async def _connect_from_engine(engine: AsyncEngine):
            async with engine.begin() as conn:
                yield conn

        context = None

        if self._connection is not None:
            context = _connect_from_connection(self._connection)

        elif self._engine is not None:
            context = _connect_from_engine(self._engine)
        else:
            context = _connect_from_engine(get_database())

        async with context as conn:
            yield conn

    def _get_name(self):
        return self._model.__name__

    def _get_pk_filter(self, *key):
        pk_cols = self._table.primary_key.columns
        if len(key) != len(pk_cols):
            raise ValueError("Mismatched pk length")
        where_clause = sa.and_(*(col == val for col, val in zip(pk_cols, key)))
        return where_clause

    # ----------------------------------------------------------------

    async def get_by_pk(self, *key):
        query = self._table.select().where(self._get_pk_filter(*key))
        result = await self._execute(query)
        try:
            return result.one()
        except NoResultFound as exc:
            raise ObjectNotFound(f"{self._get_name()} pk={key}") from exc

    async def get_by(self, **filters) -> T:
        query = self._table.select().filter_by(**filters)
        result = await self._execute(query)
        try:
            return result.one()
        except NoResultFound as exc:
            raise ObjectNotFound(f"{self._get_name()} with {filters}") from exc

    async def insert(self, **values) -> Any | None:
        query = self._table.insert().values(**values)
        result = await self._execute(query)
        return result.inserted_primary_key

    async def update(self, *key, **updates):
        where_clause = self._get_pk_filter(*key)
        query = self._table.update().where(where_clause).values(**updates)
        async with self._connect() as conn:
            await conn.execute(query)

    @asynccontextmanager
    async def for_update(self, *key) -> AsyncIterator[tuple[T, UpdaterFn]]:
        where_clause = self._get_pk_filter(*key)
        query = self._table.select().where(where_clause).with_for_update()

        async with self._connect() as conn, conn.begin():
            result = await conn.execute(query)

            async def update_object(**updates):
                query = self._table.update().where(where_clause).values(**updates)
                result = await conn.execute(query)
                return result

            yield self._wrap_result(result).one(), update_object

    async def delete(self, *key):
        where_clause = self._get_pk_filter(*key)
        query = self._table.delete().where(where_clause)
        async with self._connect() as conn:
            await conn.execute(query)


class WrappedResult(Generic[T]):
    def __init__(self, model: Type[T], result: sa.CursorResult) -> None:
        self._model = model
        self._result = result

    def all(self) -> list[T]:
        return [self._model.from_row(row) for row in self._result.all()]

    def fetchall(self) -> list[T]:
        return self.all()

    def fetchone(self) -> T | None:
        row = self._result.fetchone()
        if row is None:
            return None
        return self._model.from_row(row)

    def first(self) -> T | None:
        row = self._result.first()
        if row is None:
            return None
        return self._model.from_row(row)

    def one(self) -> T:
        # Raises NoResultFound, MultipleResultsFound
        row = self._result.one()
        return self._model.from_row(row)

    def one_or_none(self) -> T | None:
        # Raises MultipleResultsFound
        row = self._result.one_or_none()
        if row is None:
            return None
        return self._model.from_row(row)

    @property
    def inserted_primary_key(self) -> Any | None:
        return self._result.inserted_primary_key
