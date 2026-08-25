import pytest
import sqlalchemy as sa
from sqlalchemy.exc import ResourceClosedError

from app.exceptions import MultipleObjectsFound, ObjectNotFound
from app.lib.models import BaseModel
from app.lib.sql.table_helper import TableHelper
from app.resources import get_database

pytestmark = [
    pytest.mark.usefixtures("database"),
    pytest.mark.usefixtures("database_schema"),
    pytest.mark.asyncio,
]


class SampleObject(BaseModel):
    id: int
    text: str


@pytest.fixture()
def database_metadata():
    metadata = sa.MetaData()

    sa.Table(
        "sample_object",
        metadata,
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("text", sa.Text),
    )

    return metadata


@pytest.fixture(name="th")
def table_helper_fixture(database_metadata):
    return TableHelper[SampleObject, int](
        table=database_metadata.tables["sample_object"],
        model=SampleObject,
        get_engine=get_database,
        default_ordering="PK",
    )


class Test_wrapped_result:
    # result.all() ---------------------------------------------------

    async def test_all_for_empty_result(self, th: TableHelper[SampleObject, int]):
        result = await th.select()
        assert result.all() == []

    async def test_all_for_non_empty_result(self, th: TableHelper[SampleObject, int]):
        await th.insert(text="foo")
        await th.insert(text="bar")
        result = await th.select()

        objs = result.all()

        assert isinstance(objs, list)
        assert len(objs) == 2
        assert all(isinstance(x, SampleObject) for x in objs)
        assert {x.text for x in objs} == {"foo", "bar"}

    async def test_subsequent_call_to_all_returns_no_results(
        self, th: TableHelper[SampleObject, int]
    ):
        await th.insert(text="foo")
        await th.insert(text="bar")
        result = await th.select()

        objs = result.all()
        assert len(objs) == 2

        assert result.all() == []

    # result.fetchone() ----------------------------------------------

    async def test_fetchone_returns_none_if_no_result(
        self, th: TableHelper[SampleObject, int]
    ):
        result = await th.select()
        assert result.fetchone() is None

    async def test_fetchone_returns_object_if_result(
        self, th: TableHelper[SampleObject, int]
    ):
        await th.insert(text="foo")
        result = await th.select()

        obj = result.fetchone()

        assert isinstance(obj, SampleObject)
        assert obj.text == "foo"

    async def test_fetchone_consumes_rows(self, th: TableHelper[SampleObject, int]):
        await th.insert(text="foo")
        result = await th.select()

        assert result.fetchone() is not None
        assert result.fetchone() is None

    # result.first() -------------------------------------------------

    async def test_first_returns_none_if_no_result(
        self, th: TableHelper[SampleObject, int]
    ):
        result = await th.select()
        assert result.first() is None

    async def test_first_closes_the_cursor(
        self, th: TableHelper[SampleObject, int], subtests
    ):
        await th.insert(text="foo")

        with subtests.test("called once"):
            result = await th.select()
            obj = result.first()
            assert obj is not None
            assert obj.text == "foo"

        with subtests.test("called twice"):  # noqa: SIM117
            with pytest.raises(ResourceClosedError):
                result.first()

    # result.one() ---------------------------------------------------

    async def test_one_raises_if_no_result(self, th: TableHelper[SampleObject, int]):
        result = await th.select()
        with pytest.raises(ObjectNotFound):
            result.one()

    async def test_one_returns_single_object(self, th: TableHelper[SampleObject, int]):
        await th.insert(text="foo")
        result = await th.select()
        obj = result.one()
        assert isinstance(obj, SampleObject)
        assert obj.text == "foo"

    async def test_one_raises_if_multiple_results(
        self, th: TableHelper[SampleObject, int]
    ):
        await th.insert(text="foo")
        await th.insert(text="bar")
        result = await th.select()
        with pytest.raises(MultipleObjectsFound):
            result.one()

    # result.one_or_none() -------------------------------------------

    async def test_one_or_none_returns_none_if_no_result(
        self, th: TableHelper[SampleObject, int]
    ):
        result = await th.select()
        assert result.one_or_none() is None

    async def test_one_or_none_returns_single_object(
        self, th: TableHelper[SampleObject, int]
    ):
        await th.insert(text="foo")
        result = await th.select()
        obj = result.one_or_none()
        assert isinstance(obj, SampleObject)
        assert obj.text == "foo"

    async def test_one_or_none_raises_if_multiple_results(
        self, th: TableHelper[SampleObject, int]
    ):
        await th.insert(text="foo")
        await th.insert(text="bar")
        result = await th.select()
        with pytest.raises(MultipleObjectsFound):
            result.one_or_none()
