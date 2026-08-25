"""
Table helper

Reusable high-level functions to perform CRUD operations between a
model and a table.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable, Coroutine
from contextlib import asynccontextmanager
from typing import Any

import sqlalchemy as sa
from sqlalchemy.engine.interfaces import CoreExecuteOptionsParameter
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from app.lib.protocols import FromDict

from .wrapped_result import WrappedResult

# Fuctio returig a SQLAlchemy engine
type GetEngineFn = Callable[[], AsyncEngine]

# Callable to get (an updated version of) an object
type GetterFn[T] = Callable[[], Coroutine[Any, Any, T]]

# Callable to update an object
type UpdaterFn = Callable[..., Coroutine[Any, Any, None]]


class TableHelper[T: FromDict]:
    __slots__ = ["_get_engine", "_model", "_table"]

    _table: sa.Table
    _model: type[T]
    _get_engine: GetEngineFn

    def __init__(self, table: sa.Table, model: type[T], get_engine: GetEngineFn):
        self._table = table
        self._model = model
        self._get_engine = get_engine

    @asynccontextmanager
    async def _begin(self) -> AsyncGenerator[AsyncConnection]:
        engine = self._get_engine()
        async with engine.connect() as conn, conn.begin():
            yield conn

    async def _execute(
        self,
        statement: sa.Executable,
        parameters: Any | None = None,
        *,
        execution_options: CoreExecuteOptionsParameter | None = None,
    ) -> WrappedResult[T]:

        async with self._begin() as conn:
            result = await conn.execute(
                statement, parameters, execution_options=execution_options
            )
        return WrappedResult[T](self._model, result)

    # ----------------------------------------------------------------

    def _get_pk_filter(self, *key):
        """Get a SQLAlchemy where clause to filter this table by primary key"""
        pk_cols = self._table.primary_key.columns
        if len(key) != len(pk_cols):
            raise ValueError("Mismatched pk length")
        where_clause = sa.and_(*(col == val for col, val in zip(pk_cols, key)))
        return where_clause

    async def get_by_pk(self, *key):
        query = self._table.select().where(self._get_pk_filter(*key))
        result = await self._execute(query)
        return result.one()

    async def get_by(self, **filters) -> T:
        query = self._table.select().filter_by(**filters)
        result = await self._execute(query)
        return result.one()

    async def select(self, *where_clause, **filters) -> WrappedResult[T]:
        query = self._table.select()
        if where_clause:
            query = query.where(*where_clause)
        if filters:
            query = query.filter_by(**filters)
        return await self._execute(query)

    async def insert(self, **values) -> Any | None:
        query = self._table.insert().values(**values)
        result = await self._execute(query)
        return result.inserted_primary_key

    async def update(self, *key, **updates):
        where_clause = self._get_pk_filter(*key)
        query = self._table.update().where(where_clause).values(**updates)
        async with self._begin() as conn:
            await conn.execute(query)

    @asynccontextmanager
    async def for_update(self, *key) -> AsyncGenerator[UpdateHelper[T]]:
        """
        Select a object for atomic update.

        Returns an UpdateHelper instance with the following attributes:

        - obj: the selected object, as model instance
        - update: async function accepting object properties as
          keyword arguments, performing an update on the selected
          object
        """

        where_clause = self._get_pk_filter(*key)
        query = self._table.select().where(where_clause).with_for_update()

        async with self._begin() as conn:
            result = await conn.execute(query)
            obj = WrappedResult(self._model, result).one()

            async def get_object():
                query = self._table.select().where(where_clause)
                result = await conn.execute(query)
                return WrappedResult(self._model, result).one()

            async def update_object(**updates):
                query = self._table.update().where(where_clause).values(**updates)
                await conn.execute(query)

            yield UpdateHelper(obj=obj, get=get_object, update=update_object)

    async def delete(self, *key):
        where_clause = self._get_pk_filter(*key)
        query = self._table.delete().where(where_clause)
        async with self._begin() as conn:
            await conn.execute(query)


class UpdateHelper[T: FromDict]:
    __slots__ = ["_get", "_obj", "_update"]

    _obj: T | None
    _get: GetterFn[T]
    _update: UpdaterFn

    def __init__(self, obj: T, get: GetterFn[T], update: UpdaterFn):
        self._obj = obj
        self._get = get
        self._update = update

    async def get(self, cache=True):
        if cache and self._obj is not None:
            return self._obj
        self._obj = await self._get()
        return self._obj

    async def update(self, **kwargs):
        await self._update(**kwargs)
        self._obj = None  # Invalidate
