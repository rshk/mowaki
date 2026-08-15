"""
Query builder

Helpers to build common queries on a Table.
"""

from typing import Any

import sqlalchemy as sa


def get_primary_key_filter(table: sa.Table, key: tuple[Any, ...]):
    """
    Create a query clause for selecting an object by primary key.

    Args:
        table: the sqlalchemy.Table object
        key: tuple of key column values
    """

    pk_cols = table.primary_key.columns
    if len(key) != len(pk_cols):
        raise ValueError("Mismatched pk length")
    where_clause = sa.and_(*(col == val for col, val in zip(pk_cols, key)))
    return where_clause
