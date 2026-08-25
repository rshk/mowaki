from __future__ import annotations

from typing import Any

import sqlalchemy as sa
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from app.exceptions import MultipleObjectsFound, ObjectNotFound
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
        return self.all()  # pragma: nocover

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
        # Raises ObjectNotfound, MultipleObjectsfound
        try:
            row = self._result.one()
        except NoResultFound as exc:
            raise ObjectNotFound(self._get_name()) from exc
        except MultipleResultsFound as exc:
            raise MultipleObjectsFound(self._get_name()) from exc

        return self._model.from_dict(row._asdict())

    def one_or_none(self) -> T | None:
        # Raises MultipleObjectsFound

        try:
            row = self._result.one_or_none()
        except MultipleResultsFound as exc:
            raise MultipleObjectsFound(self._get_name()) from exc

        if row is None:
            return None
        return self._model.from_dict(row._asdict())

    @property
    def inserted_primary_key(self) -> Any | None:
        return self._result.inserted_primary_key

    def _get_name(self):
        """Get model name. Used for error messages."""
        return self._model.__name__
