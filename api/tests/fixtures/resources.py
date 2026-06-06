import pytest
import pytest_asyncio
from app.config import config_context, update_config
from app.io.resources import (
    initialize_resources,
    resources_context,
    update_resources,
)
from app.lib.context import scoped_context
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.fixture(scope="session")
def setup_resources_context(config, setup_config_context):
    resources = initialize_resources(config)
    with scoped_context(resources_context, resources):
        yield


# @pytest_asyncio.fixture(scope="session")
# async def database_resource(database_url, database_schema):
#     tok1 = update_config(database_url=database_url)
#     tok2 = update_resources(database=create_async_engine(database_url))

#     yield

#     resources_context.reset(tok2)
#     config_context.reset(tok1)
