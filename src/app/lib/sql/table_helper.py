"""
Table helper

Reusable high-level functions to perform CRUD operations between a
model and a table.
"""

from __future__ import annotations

from collections.abc import (
    AsyncGenerator,
    Callable,
    Coroutine,
    Iterable,
    Iterator,
    Sized,
)
from contextlib import asynccontextmanager
from typing import Any

import sqlalchemy as sa
from sqlalchemy.engine.interfaces import CoreExecuteOptionsParameter
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from app.exceptions import ItsABug
from app.lib.protocols import FromDict

from .wrapped_result import WrappedResult

# Fuctio returig a SQLAlchemy engine
type GetEngineFn = Callable[[], AsyncEngine]

# Callable to get (an updated version of) an object
type GetterFn[T] = Callable[[], Coroutine[Any, Any, T]]

# Callable to update an object
type UpdaterFn = Callable[..., Coroutine[Any, Any, None]]

# Loose "order by" specification, from user input
type OrderBySpec = str | list[str] | tuple[str] | None


class TableHelper[T: FromDict, K]:
    __slots__ = ["_default_ordering", "_get_engine", "_model", "_table"]

    _table: sa.Table
    _model: type[T]
    _get_engine: GetEngineFn
    _default_ordering: list[Any] | None

    def __init__(
        self,
        table: sa.Table,
        model: type[T],
        get_engine: GetEngineFn,
        default_ordering: OrderBySpec = None,
    ):
        self._table = table
        self._model = model
        self._get_engine = get_engine
        self._default_ordering = None
        if default_ordering is not None:
            self._default_ordering = list(self._parse_order_by(default_ordering))

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

    def _get_pk_filter(self, key: K):
        """Get a SQLAlchemy where clause to filter this table by primary key"""

        pk_cols = self._table.primary_key.columns

        if len(pk_cols) == 1:
            return pk_cols[0] == key

        if not (isinstance(key, Sized) and isinstance(key, Iterable)):
            raise TypeError(f"Bad key {key}, expected {K}")

        if len(key) != len(pk_cols):
            raise ValueError(
                "Mismatched primary key length "
                f"(got {len(key)}, expected {len(pk_cols)})"
            )

        where_clause = sa.and_(*(col == val for col, val in zip(pk_cols, key)))
        return where_clause

    def _parse_order_by(self, order_by: str | Iterable[str]) -> Iterator[Any]:
        if order_by == "PK":
            # Special case: order by primary key
            yield from self._table.primary_key.columns
            return

        if isinstance(order_by, str):
            _order_by = order_by.split(",")
        else:
            _order_by = list(order_by)

        for item in _order_by:
            if item.startswith("~"):
                yield self._table.c[item[1:]].desc()
            else:
                yield self._table.c[item].asc()

    async def get_by_pk(self, key: K) -> T:
        result = await self.select(pk=key)
        return result.one()

    async def get_by(self, **filters) -> T:
        result = await self.select(**filters)
        return result.one()

    async def select(
        self,
        *where_clause,
        pk: K | None = None,
        order_by: str | list[str] | tuple[str] | None = None,
        **filters,
    ) -> WrappedResult[T]:
        """
        Select multiple objects from a table.

        Args:

            *where_clause:

                Passed to SQLAlchemy Selectable.where().

            pk:

                Valid primary key for this object. Will be converted
                to the appropriate WHERE clause.

            order_by:

                Adds an ORDER BY clause to the query. If set to None,
                no ORDER BY will be added to the query. If set to the
                special value "PK", order by primary
                column. Otherwise, accepts a string in the form
                "field1,~field2", where fields prefixed with "~" will
                be sorted in descending order.

            **filters:

                Other arguments are treated as column names mapping to
                exact values. Will be passed to
                Selectable.filter_by().
        """

        query = self._table.select()

        if pk is not None:
            query = query.where(self._get_pk_filter(pk))

        if order_by is None:
            if self._default_ordering is not None:
                query = query.order_by(*self._default_ordering)
        else:
            query = query.order_by(*self._parse_order_by(order_by))

        if where_clause:
            query = query.where(*where_clause)

        if filters:
            query = query.filter_by(**filters)

        return await self._execute(query)

    async def insert(self, **values) -> K:
        query = self._table.insert().values(**values)
        result = await self._execute(query)

        pk = result.inserted_primary_key

        if pk is None:
            # This should never happen
            raise ItsABug(
                "Unexpected empty primary key returned by INSERT"
            )  # pragma: nocover

        if len(self._table.primary_key.columns) == 1:
            assert len(pk) == 1
            return pk[0]

        return pk

    async def update(self, key: K, **updates):
        where_clause = self._get_pk_filter(key)
        query = self._table.update().where(where_clause).values(**updates)
        async with self._begin() as conn:
            await conn.execute(query)

    @asynccontextmanager
    async def for_update(self, key: K) -> AsyncGenerator[UpdateHelper[T]]:
        """
        Select a object for atomic update.

        Returns an UpdateHelper instance with the following attributes:

        - obj: the selected object, as model instance
        - update: async function accepting object properties as
          keyword arguments, performing an update on the selected
          object
        """

        where_clause = self._get_pk_filter(key)
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

    async def delete(self, key: K):
        where_clause = self._get_pk_filter(key)
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
