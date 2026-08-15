"""
Table helper

Reusable high-level functions to perform CRUD operations between a
model and a table.
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Type

import sqlalchemy as sa
from sqlalchemy.engine.interfaces import CoreExecuteOptionsParameter
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncTransaction

from app.types._protocols import FromDict

type GetEngineFn = Callable[[], AsyncEngine]


class TableHelper[T: FromDict]:
    __slots__ = ["_table", "_model", "_get_engine"]

    _table: sa.Table
    _model: Type[T]
    _get_engine: GetEngineFn

    def __init__(self, table: sa.Table, model: Type[T], get_engine: GetEngineFn):
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
        execution_options: Optional[CoreExecuteOptionsParameter] = None,
    ) -> WrappedResult[T]:
        async with self._connect() as conn:
            result = await conn.execute(
                statement, parameters, execution_options=execution_options
            )
        return WrappedResult[T](self._model, result)

    def _get_name(self):
        """Get model name. Used for error messages."""
        return self._model.__name__


class WrappedResult[T: FromDict]:
    """
    Wrapper for a sqlalchemy.CursorResult

    Exposes many of the standard Result methods, using the specified
    model to return the resulting data.
    """

    def __init__(self, model: Type[T], result: sa.CursorResult) -> None:
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
