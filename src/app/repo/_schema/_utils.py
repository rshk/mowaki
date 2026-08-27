"""
Utilities for UUID-based primary keys
"""

import sqlalchemy as sa

from app.lib.keygen import generate_uuid


def primary_key_column(name: str = "id") -> sa.Column:
    """Define a UUID-based primary key column"""
    return sa.Column(name, sa.Uuid, primary_key=True, default=generate_uuid)


def primary_key_reference(
    name: str,
    fk: str | None = None,
    gen_fk: bool | None = None,
    index: bool = True,
    nullable: bool = False,
) -> sa.Column:
    """
    Define a "foreign key" reference column
    """

    args = []

    if gen_fk is None:
        gen_fk = bool(fk)

    if gen_fk and (fk is not None):
        args.append(sa.ForeignKey(fk))

    return sa.Column(name, sa.Uuid, *args, index=index, nullable=nullable)
