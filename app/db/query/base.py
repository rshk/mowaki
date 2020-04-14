from abc import ABC, abstractproperty

from sqlalchemy import delete, select, update, and_
from sqlalchemy.dialects.postgresql.dml import insert

from app.db import db


class TableDB(ABC):

    db = db

    @abstractproperty
    def table(self):
        pass

    def __init__(self):
        self._pk_fields = [x.name for x in self.table.primary_key.columns]

    def create(self, **kwargs):
        query = self._create_query(**kwargs)
        result = self.db.execute(query)
        user_id, = result.inserted_primary_key
        return user_id

    def _create_query(self, **kwargs):
        return insert(self.table).values(**kwargs)

    def update(self, *args, **kwargs):
        query = self._update_query(*args, **kwargs)
        self.db.execute(query)

    def _update_query(self, *args, **kwargs):
        all_fields = self._get_named_fields(args, kwargs)
        pk_fields = self._pick_pk_fields(all_fields)
        condition = self._build_condition_from_fields(pk_fields)
        return update(self.table).values(**all_fields).where(condition)

    def delete(self, *args, **kwargs):
        query = self._delete_query(*args, **kwargs)
        self.db.execute(query)

    def _delete_query(self, *args, **kwargs):
        all_fields = self._get_named_fields(args, kwargs)
        for key in self._pk_fields:
            if key not in all_fields:
                raise ValueError('All key fields must be specified for DELETE')

        condition = self._build_condition_from_fields(all_fields)
        return delete(self.table).where(condition)

    def _get_named_fields(self, args, kwargs):
        if len(args) > len(self._pk_fields):
            raise ValueError(
                'Too many positional arguments '
                '(expected up to {}, got {})'
                .format(len(self._pk_fields), len(args)))

        key_fields = dict(zip(self._pk_fields, args))
        return dict(**key_fields, **kwargs)

    def _pick_pk_fields(self, fields):
        pk_fields = {}
        for key in self._pk_fields:
            try:
                value = fields.pop(key)
            except KeyError:
                raise ValueError('Unspecified value for key {}'.format(key))
            else:
                pk_fields[key] = value
        return pk_fields

    def _build_condition_from_fields(self, fields):
        return and_(*(
            self.table.c[key] == value
            for key, value in fields.items()
        ))

    def get(self, *args, **kwargs):
        query = self._select_query(*args, **kwargs)
        result = self.db.execute(query)
        return result.fetchone()

    def list(self):
        # No need for ordering when getting one item
        query = self._select_query(_order_by_pk=True)
        result = self.db.execute(query)
        yield from result.fetchall()

    def _select_query(self, *args, _order_by_pk=False, **kwargs):
        all_fields = self._get_named_fields(args, kwargs)
        condition = self._build_condition_from_fields(all_fields)
        query = select([self.table]).where(condition)

        if _order_by_pk:
            query = query.order_by(*(
                self.table.c[key].asc()
                for key in self._pk_fields))

        return query
