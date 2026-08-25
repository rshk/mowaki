import uuid
from datetime import UTC, datetime

import pytest
import pytest_asyncio
import sqlalchemy as sa
from app import repo
from app.exceptions import ObjectNotFound
from app.lib.models import BaseModel
from app.lib.sql.table_helper import TableHelper, UpdateHelper
from app.lib.sql.utils import create_async_engine
from app.resources import get_database
from app.types.auth.auth_flow import FlowState
from app.types.auth.session import SessionID

pytestmark = [
    pytest.mark.usefixtures("database"),
    pytest.mark.asyncio,
]


class SampleBlogPost(BaseModel):
    id: uuid.UUID
    title: str
    text: str
    created_at: datetime


@pytest.fixture()
def database_metadata():
    metadata = sa.MetaData()

    sa.Table(
        "sample_blog",
        metadata,
        sa.Column("id", sa.Uuid, primary_key=True, default=lambda: uuid.uuid4()),
        sa.Column("title", sa.Text),
        sa.Column("text", sa.Text),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(UTC),
        ),
    )

    return metadata


@pytest.fixture()
def db_tables(database_metadata):
    return database_metadata.tables


@pytest.fixture(name="th")
def table_helper_fixture(db_tables):
    return TableHelper[SampleBlogPost](
        table=db_tables["sample_blog"],
        model=SampleBlogPost,
        get_engine=get_database,
    )


@pytest_asyncio.fixture()
async def database_schema(database, resources, database_metadata):
    """
    Create a custom database schema for testing TableHelper machinery
    """

    metadata = database_metadata

    if resources:
        pass  # Make linter happy; only need resources as a dependency

    database_url = database
    engine = create_async_engine(
        database_url,
        isolation_level="AUTOCOMMIT",
        poolclass=sa.NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.mark.usefixtures("database_schema")
class Test_table_helper_with_simple_model:
    async def test_create_and_retrieve_object(self, subtests, th):
        with subtests.test("Create object"):
            pk = await th.insert(title="Hello world", text="Original text")
            assert pk is not None
            assert isinstance(pk, sa.Row)
            assert len(pk) == 1
            [obj_pk] = pk

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


@pytest.mark.usefixtures("database_schema")
async def test_get_by_raises_objectnotfound(th):
    with pytest.raises(ObjectNotFound):
        await th.get_by(title="Does not exist")
