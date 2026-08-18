"""
Table helper

Reusable high-level functions to perform CRUD operations between a
model and a table.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable, Coroutine
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import sqlalchemy as sa
from sqlalchemy.engine.interfaces import CoreExecuteOptionsParameter
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncTransaction

from app.exceptions import ObjectNotFound
from app.lib.protocols import FromDict

# Fuctio returig a SQLAlchemy engine
type GetEngineFn = Callable[[], AsyncEngine]

# Callable to update an object
type UpdaterFn = Callable[..., Coroutine[Any, Any, sa.CursorResult[Any]]]


class TableHelper[T: FromDict]:
    __slots__ = ["_get_engine", "_model", "_table"]

    _table: sa.Table
    _model: type[T]
    _get_engine: GetEngineFn

    def __init__(self, table: sa.Table, model: type[T], get_engine: GetEngineFn):
        self._table = table
        self._model = model
        self._get_engine = get_engine

    def _connect(self) -> AsyncConnection:
        engine = self._get_engine()
        return engine.connect()

    async def _begin(self) -> AsyncTransaction:
        engine = self._get_engine()
        async with engine.connect() as conn:
            return conn.begin_nested()

    async def _execute(
        self,
        statement: sa.Executable,
        parameters: Any | None = None,
        *,
        execution_options: CoreExecuteOptionsParameter | None = None,
    ) -> WrappedResult[T]:
        async with self._connect() as conn:
            result = await conn.execute(
                statement, parameters, execution_options=execution_options
            )
        return WrappedResult[T](self._model, result)

    def _get_name(self):
        """Get model name. Used for error messages."""
        return self._model.__name__

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
    async def for_update(self, *key) -> AsyncGenerator[UpdateHelper[T]]:
        """Select a object for atomic update"""

        where_clause = self._get_pk_filter(*key)
        query = self._table.select().where(where_clause).with_for_update()

        async with self._connect() as conn:
            result = await conn.execute(query)

            async def update_object(**updates):
                query = self._table.update().where(where_clause).values(**updates)
                result = await conn.execute(query)
                return result

            yield UpdateHelper(
                result=WrappedResult[T](self._model, result),
                update=update_object,
            )

    async def delete(self, *key):
        where_clause = self._get_pk_filter(*key)
        query = self._table.delete().where(where_clause)
        async with self._connect() as conn:
            await conn.execute(query)


class WrappedResult[T: FromDict]:
    """
    Wrapper for a sqlalchemy.CursorResult

    Exposes many of the standard Result methods, using the specified
    model to return the resulting data.
    """

    def __init__(self, model: type[T], result: sa.CursorResult) -> None:
        self._model = model
        self._result = result

    def all(self) -> list[T]:
        return [self._model.from_dict(row._asdict()) for row in self._result.all()]

    def fetchall(self) -> list[T]:
        return self.all()

    def fetchone(self) -> T | None:
        row = self._result.fetchone()
        if row is None:
            return None
        return self._model.from_dict(row._asdict())

    def first(self) -> T | None:
        row = self._result.first()
        if row is None:
            return None
        return self._model.from_dict(row._asdict())

    def one(self) -> T:
        # Raises NoResultFound, MultipleResultsFound
        row = self._result.one()
        return self._model.from_dict(row._asdict())

    def one_or_none(self) -> T | None:
        # Raises MultipleResultsFound
        row = self._result.one_or_none()
        if row is None:
            return None
        return self._model.from_dict(row._asdict())

    @property
    def inserted_primary_key(self) -> Any | None:
        return self._result.inserted_primary_key


@dataclass(slots=True)
class UpdateHelper[T: FromDict]:
    result: WrappedResult[T]
    update: UpdaterFn
