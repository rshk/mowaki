"""
Table helper

Reusable high-level functions to perform CRUD operations between a
model and a table.
"""

from __future__ import annotations

from typing import Any

import sqlalchemy as sa

from app.lib.protocols import FromDict


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
