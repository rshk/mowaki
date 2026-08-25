from pydantic import TypeAdapter
import pytest
import sqlalchemy as sa
from sqlalchemy.exc import ResourceClosedError

from app.exceptions import MultipleObjectsFound, ObjectNotFound
from app.lib.models import BaseModel
from app.lib.sql.json_with_schema import JsonWithSchema
from app.lib.sql.table_helper import TableHelper
from app.resources import get_database

pytestmark = [
    pytest.mark.usefixtures("database"),
    pytest.mark.usefixtures("database_schema"),
    pytest.mark.asyncio,
]


class Obj(BaseModel):
    text: str


ObjList = TypeAdapter(list[Obj])


class Test_pydantic_model:
    @pytest.fixture()
    def database_metadata(self):
        metadata = sa.MetaData()
        sa.Table(
            "mytable",
            metadata,
            sa.Column("id", sa.BigInteger, primary_key=True),
            sa.Column("obj", JsonWithSchema(Obj), nullable=True),
        )
        return metadata

    async def test_store_and_retrieve_object(self, subtests, database_metadata):
        MyTable = database_metadata.tables["mytable"]
        db = get_database()
        obj = Obj(text="Hello world")

        with subtests.test("insert"):
            async with db.connect() as conn, conn.begin():
                query = MyTable.insert().values(obj=obj)
                result = await conn.execute(query)
                assert result is not None
                assert result.inserted_primary_key is not None
                [pk] = result.inserted_primary_key

        with subtests.test("retrieve"):
            async with db.connect() as conn, conn.begin():
                query = MyTable.select().filter_by(id=pk)
                result = await conn.execute(query)
                row = result.one()
                assert row.id == pk
                assert row.obj == obj

    async def test_store_and_retrieve_none(self, subtests, database_metadata):
        MyTable = database_metadata.tables["mytable"]
        db = get_database()

        with subtests.test("insert"):
            async with db.connect() as conn, conn.begin():
                query = MyTable.insert().values(obj=None)
                result = await conn.execute(query)
                assert result is not None
                assert result.inserted_primary_key is not None
                [pk] = result.inserted_primary_key

        with subtests.test("retrieve"):
            async with db.connect() as conn, conn.begin():
                query = MyTable.select().filter_by(id=pk)
                result = await conn.execute(query)
                row = result.one()
                assert row.id == pk
                assert row.obj is None


class Test_pydantic_type_adapter:
    @pytest.fixture()
    def database_metadata(self):
        metadata = sa.MetaData()
        sa.Table(
            "mytable",
            metadata,
            sa.Column("id", sa.BigInteger, primary_key=True),
            sa.Column("obj", JsonWithSchema(ObjList), nullable=True),
        )
        return metadata

    async def test_store_and_retrieve_object(self, subtests, database_metadata):
        MyTable = database_metadata.tables["mytable"]
        db = get_database()
        obj = [Obj(text="Hello world")]

        with subtests.test("insert"):
            async with db.connect() as conn, conn.begin():
                query = MyTable.insert().values(obj=obj)
                result = await conn.execute(query)
                assert result is not None
                assert result.inserted_primary_key is not None
                [pk] = result.inserted_primary_key

        with subtests.test("retrieve"):
            async with db.connect() as conn, conn.begin():
                query = MyTable.select().filter_by(id=pk)
                result = await conn.execute(query)
                row = result.one()
                assert row.id == pk
                assert row.obj == obj

    async def test_store_and_retrieve_none(self, subtests, database_metadata):
        MyTable = database_metadata.tables["mytable"]
        db = get_database()

        with subtests.test("insert"):
            async with db.connect() as conn, conn.begin():
                query = MyTable.insert().values(obj=None)
                result = await conn.execute(query)
                assert result is not None
                assert result.inserted_primary_key is not None
                [pk] = result.inserted_primary_key

        with subtests.test("retrieve"):
            async with db.connect() as conn, conn.begin():
                query = MyTable.select().filter_by(id=pk)
                result = await conn.execute(query)
                row = result.one()
                assert row.id == pk
                assert row.obj is None
