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


# @pytest.mark.usefixtures("database_schema")
# class Test_wrapped_result:
