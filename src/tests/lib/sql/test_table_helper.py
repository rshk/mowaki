import uuid
from datetime import UTC, datetime

import pytest
import sqlalchemy as sa

from app.exceptions import ObjectNotFound
from app.lib.keygen import generate_uuid
from app.lib.models import BaseModel
from app.lib.sql.table_helper import TableHelper, UpdateHelper
from app.resources import get_database

pytestmark = [
    pytest.mark.usefixtures("database"),
    pytest.mark.asyncio,
]


class SampleBlogPost(BaseModel):
    id: uuid.UUID
    title: str
    text: str
    created_at: datetime


class GridCell(BaseModel):
    xpos: int
    ypos: int
    label: str


@pytest.fixture()
def database_metadata():
    metadata = sa.MetaData()

    sa.Table(
        "sample_blog",
        metadata,
        sa.Column("id", sa.Uuid, primary_key=True, default=generate_uuid),
        sa.Column("title", sa.Text),
        sa.Column("text", sa.Text),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(UTC),
        ),
    )

    sa.Table(
        "grid_cell",
        metadata,
        sa.Column("xpos", sa.Integer, primary_key=True),
        sa.Column("ypos", sa.Integer, primary_key=True),
        sa.Column("label", sa.Text),
    )

    return metadata


@pytest.fixture()
def db_tables(database_metadata):
    return database_metadata.tables


@pytest.fixture(name="th")
def table_helper_fixture(db_tables):
    return TableHelper[SampleBlogPost, uuid.UUID](
        table=db_tables["sample_blog"],
        model=SampleBlogPost,
        get_engine=get_database,
    )


@pytest.mark.usefixtures("database_schema")
class Test_table_helper_with_simple_model:
    async def test_create_and_retrieve_object(
        self, subtests, th: TableHelper[SampleBlogPost, uuid.UUID]
    ):
        with subtests.test("Create object"):
            obj_pk = await th.insert(title="Hello world", text="Original text")
            assert obj_pk is not None
            assert isinstance(obj_pk, uuid.UUID)

            assert obj_pk is not None
            assert isinstance(obj_pk, uuid.UUID)

        with subtests.test("Retrieve created object"):
            obj = await th.get_by_pk(obj_pk)
            assert obj is not None
            assert isinstance(obj, SampleBlogPost)
            assert obj.id == obj_pk
            assert obj.title == "Hello world"
            assert obj.text == "Original text"

        with subtests.test("Retrieve by title"):
            obj = await th.get_by(title="Hello world")
            assert obj is not None
            assert isinstance(obj, SampleBlogPost)
            assert obj.id == obj_pk

        with subtests.test("Partial update and retrieve"):
            await th.update(obj_pk, text="Updated text")

            obj = await th.get_by_pk(obj_pk)
            assert obj.title == "Hello world"
            assert obj.text == "Updated text"

        with subtests.test("Update atomically and check object"):
            async with th.for_update(obj_pk) as upd:
                assert isinstance(upd, UpdateHelper)
                obj = await upd.get()
                await upd.update(text=obj.text + ", with more text.")

                obj = await upd.get()
                assert obj.title == "Hello world"
                assert obj.text == "Updated text, with more text."

            obj = await th.get_by_pk(obj_pk)
            assert obj.title == "Hello world"
            assert obj.text == "Updated text, with more text."

        with subtests.test("Delete object"):
            await th.delete(obj_pk)
            with pytest.raises(ObjectNotFound):
                await th.get_by_pk(obj_pk)

    async def test_complex_query(
        self, th: TableHelper[SampleBlogPost, uuid.UUID], freeze_time
    ):
        with freeze_time("2026-08-20T00:00Z"):
            pk1 = await th.insert(title="Midnight", text="...")

        with freeze_time("2026-08-20T01:00Z"):
            pk2 = await th.insert(title="One AM", text="...")

        with freeze_time("2026-08-20T02:00Z"):
            await th.insert(title="Two AM", text="...")

        with freeze_time("2026-08-20T03:00Z"):
            await th.insert(title="Three AM", text="...")

        # WARNING: We're accessing th._table directly here for
        # convenience while testing, but DO NOT do this in real code,
        # as _table is a private attribute and not guaranteed to stay
        # there. Use the Table instance from app.repo._schema instead!

        result = await th.select(
            th._table.c.created_at <= datetime(2026, 8, 20, 1, 30, tzinfo=UTC)
        )

        results = result.fetchall()
        assert len(results) == 2
        assert {x.id for x in results} == {pk1, pk2}


@pytest.mark.usefixtures("database_schema")
async def test_get_by_raises_objectnotfound(th):
    with pytest.raises(ObjectNotFound):
        await th.get_by(title="Does not exist")


@pytest.mark.usefixtures("database_schema")
class Test_table_helper_with_multi_column_pk:
    @pytest.fixture(name="th")
    def table_helper_fixture(self, db_tables):
        return TableHelper[GridCell, (int, int)](
            table=db_tables["grid_cell"],
            model=GridCell,
            get_engine=get_database,
        )

    async def test_create_and_retrieve_object(self, subtests, th):
        with subtests.test("Create object"):
            pk = await th.insert(xpos=1, ypos=5, label="Point at (1, 5)")
            assert pk is not None
            assert isinstance(pk, sa.Row)
            assert len(pk) == 2
            [xpos, ypos] = pk

            assert isinstance(xpos, int)
            assert isinstance(ypos, int)

        with subtests.test("Retrieve created object"):
            obj = await th.get_by_pk((xpos, ypos))
            assert obj is not None
            assert isinstance(obj, GridCell)
            assert obj.xpos == xpos
            assert obj.ypos == ypos
            assert obj.label == "Point at (1, 5)"

        with subtests.test("Partial update and retrieve"):
            await th.update((xpos, ypos), label="POINT(1, 5)")

            obj = await th.get_by_pk((xpos, ypos))
            assert obj.label == "POINT(1, 5)"

        with subtests.test("Update atomically and check object"):
            async with th.for_update((xpos, ypos)) as upd:
                assert isinstance(upd, UpdateHelper)
                obj = await upd.get()
                await upd.update(label=obj.label + "!!!")

                obj = await upd.get()
                assert obj.label == "POINT(1, 5)!!!"

            obj = await th.get_by_pk((xpos, ypos))
            assert obj.label == "POINT(1, 5)!!!"

        with subtests.test("Delete object"):
            await th.delete((xpos, ypos))
            with pytest.raises(ObjectNotFound):
                await th.get_by_pk((xpos, ypos))

    async def test_key_length_must_match(self, subtests, th):
        with pytest.raises(ValueError):
            await th.get_by_pk((1, 2, 3))

    async def test_key_must_be_a_tuple(self, subtests, th):
        with pytest.raises(TypeError):
            await th.get_by_pk(123)
